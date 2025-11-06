"""
Сервис для публикации задач отправки email в RabbitMQ через aiopika
"""
import json
import logging
import aio_pika
import uuid
from typing import Optional
from datetime import datetime
from app.config import settings

logger = logging.getLogger(__name__)


class EmailPublisher:
    """Класс для публикации задач отправки email в RabbitMQ"""
    
    def __init__(self):
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self._is_connected = False
    
    async def connect(self):
        """Подключение к RabbitMQ"""
        if self._is_connected and self.connection and not self.connection.is_closed:
            return
        
        try:
            # Формируем URL подключения
            if not settings.rabbitmq_url:
                # Формируем URL из отдельных параметров
                user = settings.rabbitmq_user or "guest"
                password = settings.rabbitmq_password or "guest"
                host = "rabbitmq"  # Имя сервиса в docker-compose
                port = 5672
                rabbitmq_url = f"amqp://{user}:{password}@{host}:{port}/"
            else:
                rabbitmq_url = settings.rabbitmq_url
            
            logger.info(f"Подключение к RabbitMQ: {rabbitmq_url.split('@')[1] if '@' in rabbitmq_url else 'hidden'}")
            
            self.connection = await aio_pika.connect_robust(rabbitmq_url)
            self.channel = await self.connection.channel()
            self._is_connected = True
            
            logger.info("Успешно подключено к RabbitMQ")
        except Exception as e:
            logger.error(f"Ошибка подключения к RabbitMQ: {str(e)}")
            self._is_connected = False
            raise
    
    async def disconnect(self):
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
    
    async def publish_login_email(
        self,
        email: str,
        user_name: str,
        login_time: Optional[str] = None
    ):
        """
        Публикует задачу отправки email при входе в систему через RabbitMQ
        
        Args:
            email: Email адрес получателя
            user_name: Имя пользователя
            login_time: Время входа (опционально)
        """
        if not email:
            logger.warning("Email не указан, пропускаем отправку")
            return
        
        try:
            # Подключаемся, если еще не подключены
            if not self._is_connected or not self.connection or self.connection.is_closed:
                await self.connect()
            
            # Объявляем очередь для задач Celery (отдельная очередь для email о входе)
            queue_name = "celery_login"
            queue = await self.channel.declare_queue(queue_name, durable=True)
            
            # Используем exchange Celery (по умолчанию "celery" или имя приложения)
            # Для правильной маршрутизации используем direct exchange
            exchange = await self.channel.declare_exchange(
                "celery",  # Имя exchange по умолчанию для Celery
                aio_pika.ExchangeType.DIRECT,
                durable=True
            )
            
            # Привязываем очередь к exchange с routing_key равным имени очереди
            await queue.bind(exchange, routing_key=queue_name)
            
            # Формируем сообщение в формате Celery (JSON сериализация)
            task_id = str(uuid.uuid4())
            task_message = {
                "id": task_id,
                "task": "send_login_email",
                "args": [email, user_name, login_time or datetime.now().isoformat()],
                "kwargs": {},
                "retries": 0,
                "eta": None,
                "expires": None,
                "utc": True,
            }
            
            # Сериализуем сообщение в JSON
            body = json.dumps(task_message)
            
            # Создаем сообщение
            message = aio_pika.Message(
                body.encode('utf-8'),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                content_type="application/json",
                content_encoding="utf-8",
                message_id=task_id,
            )
            
            # Публикуем сообщение в exchange с routing_key равным имени очереди
            await exchange.publish(
                message,
                routing_key=queue_name,
            )
            
            logger.info(f"Задача отправки email о входе на {email} опубликована в RabbitMQ очередь {queue_name} (task_id: {task_id})")
            
        except Exception as e:
            logger.error(f"Ошибка при публикации задачи отправки email: {str(e)}")
            # Пытаемся переподключиться
            try:
                await self.disconnect()
                await self.connect()
            except:
                pass
    
    async def publish_balance_email(
        self,
        email: str,
        user_name: str,
        amount: str,
        new_balance: str,
        payment_time: Optional[str] = None,
        transaction_id: Optional[str] = None
    ):
        """
        Публикует задачу отправки email при пополнении баланса через RabbitMQ
        
        Args:
            email: Email адрес получателя
            user_name: Имя пользователя
            amount: Сумма пополнения
            new_balance: Новый баланс после пополнения
            payment_time: Время пополнения (опционально)
            transaction_id: ID транзакции (опционально)
        """
        if not email:
            logger.warning("Email не указан, пропускаем отправку")
            return
        
        try:
            # Подключаемся, если еще не подключены
            if not self._is_connected or not self.connection or self.connection.is_closed:
                await self.connect()
            
            # Объявляем очередь для задач Celery (отдельная очередь для email о пополнении)
            queue_name = "celery_balance"
            queue = await self.channel.declare_queue(queue_name, durable=True)
            
            # Используем exchange Celery (по умолчанию "celery" или имя приложения)
            # Для правильной маршрутизации используем direct exchange
            exchange = await self.channel.declare_exchange(
                "celery",  # Имя exchange по умолчанию для Celery
                aio_pika.ExchangeType.DIRECT,
                durable=True
            )
            
            # Привязываем очередь к exchange с routing_key равным имени очереди
            await queue.bind(exchange, routing_key=queue_name)
            
            # Формируем сообщение в формате Celery (JSON сериализация)
            task_id = str(uuid.uuid4())
            task_message = {
                "id": task_id,
                "task": "send_balance_email",
                "args": [
                    email,
                    user_name,
                    amount,
                    new_balance,
                    payment_time or datetime.now().isoformat(),
                    transaction_id
                ],
                "kwargs": {},
                "retries": 0,
                "eta": None,
                "expires": None,
                "utc": True,
            }
            
            # Сериализуем сообщение в JSON
            body = json.dumps(task_message)
            
            # Создаем сообщение
            message = aio_pika.Message(
                body.encode('utf-8'),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                content_type="application/json",
                content_encoding="utf-8",
                message_id=task_id,
            )
            
            # Публикуем сообщение в exchange с routing_key равным имени очереди
            await exchange.publish(
                message,
                routing_key=queue_name,
            )
            
            logger.info(f"Задача отправки email о пополнении баланса на {email} опубликована в RabbitMQ очередь {queue_name} (task_id: {task_id})")
            
        except Exception as e:
            logger.error(f"Ошибка при публикации задачи отправки email о пополнении: {str(e)}")
            # Пытаемся переподключиться
            try:
                await self.disconnect()
                await self.connect()
            except:
                pass


# Глобальный экземпляр publisher
email_publisher = EmailPublisher()

