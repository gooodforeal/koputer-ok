"""
Сервис для публикации задач отправки email в RabbitMQ
"""
import logging
import uuid
from typing import Optional
from datetime import datetime
from app.services.rabbitmq_service import rabbitmq_service

logger = logging.getLogger(__name__)


class EmailPublisher:
    """Класс для публикации задач отправки email в RabbitMQ"""
    
    async def connect(self):
        """Подключение к RabbitMQ"""
        await rabbitmq_service.connect()
    
    async def disconnect(self):
        """Отключение от RabbitMQ"""
        await rabbitmq_service.disconnect()
    
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
            # Настраиваем очередь и exchange для Celery
            queue_name = "celery_login"
            exchange, queue = await rabbitmq_service.setup_celery_queue(queue_name)
            
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
            
            # Публикуем сообщение через универсальный сервис
            await rabbitmq_service.publish_json(
                exchange=exchange,
                routing_key=queue_name,
                data=task_message,
                message_id=task_id
            )
            
            logger.info(f"Задача отправки email о входе на {email} опубликована в RabbitMQ очередь {queue_name} (task_id: {task_id})")
            
        except Exception as e:
            logger.error(f"Ошибка при публикации задачи отправки email: {str(e)}")
            # Пытаемся переподключиться
            try:
                await rabbitmq_service.disconnect()
                await rabbitmq_service.connect()
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
            # Настраиваем очередь и exchange для Celery
            queue_name = "celery_balance"
            exchange, queue = await rabbitmq_service.setup_celery_queue(queue_name)
            
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
            
            # Публикуем сообщение через универсальный сервис
            await rabbitmq_service.publish_json(
                exchange=exchange,
                routing_key=queue_name,
                data=task_message,
                message_id=task_id
            )
            
            logger.info(f"Задача отправки email о пополнении баланса на {email} опубликована в RabbitMQ очередь {queue_name} (task_id: {task_id})")
            
        except Exception as e:
            logger.error(f"Ошибка при публикации задачи отправки email о пополнении: {str(e)}")
            # Пытаемся переподключиться
            try:
                await rabbitmq_service.disconnect()
                await rabbitmq_service.connect()
            except:
                pass


# Глобальный экземпляр publisher
email_publisher = EmailPublisher()

