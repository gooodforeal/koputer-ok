"""
Универсальный сервис для работы с RabbitMQ через aio_pika
"""
import logging
import aio_pika
from typing import Optional, Dict, Any, Tuple
from enum import Enum
from app.config import settings

logger = logging.getLogger(__name__)


class ExchangeType(Enum):
    """Типы exchange в RabbitMQ"""
    DIRECT = aio_pika.ExchangeType.DIRECT
    TOPIC = aio_pika.ExchangeType.TOPIC
    FANOUT = aio_pika.ExchangeType.FANOUT
    HEADERS = aio_pika.ExchangeType.HEADERS


class RabbitMQService:
    """Универсальный сервис для работы с RabbitMQ"""
    
    def __init__(self):
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self._is_connected = False
    
    def _get_connection_url(self) -> str:
        """Формирует URL подключения к RabbitMQ"""
        if settings.rabbitmq_url:
            return settings.rabbitmq_url
        
        # Формируем URL из отдельных параметров
        user = settings.rabbitmq_user or "guest"
        password = settings.rabbitmq_password or "guest"
        host = settings.rabbitmq_host or "rabbitmq"  # Имя сервиса в docker-compose
        port = settings.rabbitmq_port or 5672
        return f"amqp://{user}:{password}@{host}:{port}/"
    
    async def connect(self) -> None:
        """Подключение к RabbitMQ"""
        if self._is_connected and self.connection and not self.connection.is_closed:
            return
        
        try:
            rabbitmq_url = self._get_connection_url()
            # Скрываем пароль в логах
            log_url = rabbitmq_url.split('@')[1] if '@' in rabbitmq_url else 'hidden'
            logger.info(f"Подключение к RabbitMQ: {log_url}")
            
            self.connection = await aio_pika.connect_robust(rabbitmq_url)
            self.channel = await self.connection.channel()
            self._is_connected = True
            
            logger.info("Успешно подключено к RabbitMQ")
        except Exception as e:
            logger.error(f"Ошибка подключения к RabbitMQ: {str(e)}")
            self._is_connected = False
            raise
    
    async def disconnect(self) -> None:
        """Отключение от RabbitMQ"""
        try:
            if self.channel and not self.channel.is_closed:
                await self.channel.close()
            if self.connection and not self.connection.is_closed:
                await self.connection.close()
            self._is_connected = False
            logger.info("Отключено от RabbitMQ")
        except Exception as e:
            logger.error(f"Ошибка при отключении от RabbitMQ: {str(e)}")
    
    async def ensure_connected(self) -> None:
        """Проверяет подключение и переподключается при необходимости"""
        if not self._is_connected or not self.connection or self.connection.is_closed:
            await self.connect()
    
    async def declare_exchange(
        self,
        exchange_name: str,
        exchange_type: ExchangeType = ExchangeType.DIRECT,
        durable: bool = True
    ) -> aio_pika.Exchange:
        """
        Объявляет exchange в RabbitMQ
        
        Args:
            exchange_name: Имя exchange
            exchange_type: Тип exchange (DIRECT, TOPIC, FANOUT, HEADERS)
            durable: Сохранять exchange после перезапуска RabbitMQ
        
        Returns:
            Объект Exchange
        """
        await self.ensure_connected()
        exchange = await self.channel.declare_exchange(
            exchange_name,
            exchange_type.value,
            durable=durable
        )
        logger.debug(f"Exchange '{exchange_name}' объявлен (тип: {exchange_type.name})")
        return exchange
    
    async def declare_queue(
        self,
        queue_name: str,
        durable: bool = True,
        exclusive: bool = False,
        auto_delete: bool = False,
        arguments: Optional[Dict[str, Any]] = None
    ) -> aio_pika.Queue:
        """
        Объявляет очередь в RabbitMQ
        
        Args:
            queue_name: Имя очереди
            durable: Сохранять очередь после перезапуска RabbitMQ
            exclusive: Очередь доступна только текущему соединению
            auto_delete: Удалять очередь при отсутствии подписчиков
            arguments: Дополнительные аргументы для очереди
        
        Returns:
            Объект Queue
        """
        await self.ensure_connected()
        queue = await self.channel.declare_queue(
            queue_name,
            durable=durable,
            exclusive=exclusive,
            auto_delete=auto_delete,
            arguments=arguments or {}
        )
        logger.debug(f"Очередь '{queue_name}' объявлена")
        return queue
    
    async def bind_queue(
        self,
        queue: aio_pika.Queue,
        exchange: aio_pika.Exchange,
        routing_key: str = ""
    ) -> None:
        """
        Привязывает очередь к exchange
        
        Args:
            queue: Объект очереди
            exchange: Объект exchange
            routing_key: Ключ маршрутизации
        """
        await self.ensure_connected()
        await queue.bind(exchange, routing_key=routing_key)
        logger.debug(f"Очередь '{queue.name}' привязана к exchange '{exchange.name}' с routing_key '{routing_key}'")
    
    async def publish_message(
        self,
        exchange: aio_pika.Exchange,
        routing_key: str,
        message_body: bytes,
        message_id: Optional[str] = None,
        content_type: str = "application/json",
        content_encoding: str = "utf-8",
        delivery_mode: aio_pika.DeliveryMode = aio_pika.DeliveryMode.PERSISTENT,
        headers: Optional[Dict[str, Any]] = None,
        priority: Optional[int] = None,
        expiration: Optional[str] = None
    ) -> None:
        """
        Публикует сообщение в RabbitMQ
        
        Args:
            exchange: Объект exchange
            routing_key: Ключ маршрутизации
            message_body: Тело сообщения (bytes)
            message_id: Уникальный ID сообщения
            content_type: Тип контента
            content_encoding: Кодировка контента
            delivery_mode: Режим доставки (PERSISTENT или TRANSIENT)
            headers: Дополнительные заголовки сообщения
            priority: Приоритет сообщения (0-255)
            expiration: Время жизни сообщения в формате "TTL" (например, "60000" для 60 секунд)
        """
        await self.ensure_connected()
        
        message = aio_pika.Message(
            message_body,
            delivery_mode=delivery_mode,
            content_type=content_type,
            content_encoding=content_encoding,
            message_id=message_id,
            headers=headers,
            priority=priority,
            expiration=expiration
        )
        
        await exchange.publish(message, routing_key=routing_key)
        logger.debug(f"Сообщение опубликовано в exchange '{exchange.name}' с routing_key '{routing_key}'")
    
    async def publish_json(
        self,
        exchange: aio_pika.Exchange,
        routing_key: str,
        data: Dict[str, Any],
        message_id: Optional[str] = None,
        **kwargs
    ) -> None:
        """
        Публикует JSON сообщение в RabbitMQ
        
        Args:
            exchange: Объект exchange
            routing_key: Ключ маршрутизации
            data: Данные для сериализации в JSON
            message_id: Уникальный ID сообщения
            **kwargs: Дополнительные параметры для publish_message
        """
        import json
        message_body = json.dumps(data).encode('utf-8')
        await self.publish_message(
            exchange=exchange,
            routing_key=routing_key,
            message_body=message_body,
            message_id=message_id,
            **kwargs
        )
    
    async def setup_celery_queue(
        self,
        queue_name: str,
        exchange_name: str = "celery"
    ) -> Tuple[aio_pika.Exchange, aio_pika.Queue]:
        """
        Настраивает очередь и exchange для Celery
        
        Args:
            queue_name: Имя очереди
            exchange_name: Имя exchange (по умолчанию "celery")
        
        Returns:
            Кортеж (exchange, queue)
        """
        exchange = await self.declare_exchange(
            exchange_name,
            ExchangeType.DIRECT,
            durable=True
        )
        
        queue = await self.declare_queue(queue_name, durable=True)
        await self.bind_queue(queue, exchange, routing_key=queue_name)
        
        return exchange, queue


# Глобальный экземпляр сервиса
rabbitmq_service = RabbitMQService()

