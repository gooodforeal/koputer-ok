"""
Сервис для интеграции с платежной системой Юкасса
"""
import uuid
from decimal import Decimal
from typing import Optional, Dict, Any
from yookassa import Configuration, Payment
from yookassa.domain.notification import WebhookNotificationFactory
from app.config import settings
import json


# Настройка Юкассы
Configuration.account_id = settings.yookassa_shop_id
Configuration.secret_key = settings.yookassa_secret_key


class YooKassaService:
    """Сервис для работы с платежной системой Юкасса"""
    
    @staticmethod
    async def create_payment(
        amount: Decimal,
        user_id: int,
        description: str = "Пополнение баланса",
        return_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Создать платеж в Юкассе
        
        Args:
            amount: Сумма платежа
            user_id: ID пользователя
            description: Описание платежа
            return_url: URL для возврата после оплаты
            metadata: Дополнительные метаданные
            
        Returns:
            Словарь с данными платежа (payment_id, confirmation_url)
        """
        # Генерируем уникальный ID платежа
        payment_id = str(uuid.uuid4())
        
        # Формируем метаданные
        payment_metadata = {
            "user_id": user_id,
            **(metadata or {})
        }
        
        # URL возврата по умолчанию
        # ВАЖНО: payment_id здесь еще не известен (это временный UUID),
        # реальный payment_id будет известен только после создания платежа
        # Поэтому используем дефолтный URL, который будет обновлен после создания
        if not return_url:
            # Используем базовый URL профиля, payment_id будет добавлен через метаданные
            # или через redirect после создания платежа
            return_url = f"{settings.frontend_url}/profile"
        
        # Создаем платеж
        payment = Payment.create({
            "amount": {
                "value": str(amount),
                "currency": "RUB"
            },
            "confirmation": {
                "type": "redirect",
                "return_url": return_url
            },
            "capture": True,
            "description": description,
            "metadata": payment_metadata,
            "payment_method_data": {
                "type": "bank_card"
            },
            "save_payment_method": False
        }, payment_id)
        
        return {
            "payment_id": payment.id,
            "confirmation_url": payment.confirmation.confirmation_url,
            "status": payment.status,
            "amount": Decimal(payment.amount.value),
            "description": payment.description
        }
    
    @staticmethod
    async def get_payment_status(payment_id: str) -> Dict[str, Any]:
        """
        Получить статус платежа
        
        Args:
            payment_id: ID платежа в Юкассе
            
        Returns:
            Словарь с информацией о платеже
        """
        payment = Payment.find_one(payment_id)
        
        # Безопасное получение атрибутов
        paid = getattr(payment, 'paid', False)
        cancelled = getattr(payment, 'cancelled', False)
        
        # Альтернативный способ проверки отмены через статус
        if not cancelled and hasattr(payment, 'status'):
            status = str(payment.status).lower()
            cancelled = status == 'canceled' or status == 'cancelled'
        
        # Безопасная обработка created_at
        created_at = None
        if hasattr(payment, 'created_at') and payment.created_at:
            if isinstance(payment.created_at, str):
                created_at = payment.created_at
            else:
                # Если это datetime объект, конвертируем в строку
                try:
                    created_at = payment.created_at.isoformat()
                except AttributeError:
                    # Если isoformat недоступен, используем строковое представление
                    created_at = str(payment.created_at)
        
        return {
            "payment_id": payment.id,
            "status": payment.status,
            "amount": Decimal(payment.amount.value),
            "paid": paid,
            "cancelled": cancelled,
            "created_at": created_at,
            "metadata": getattr(payment, 'metadata', None) or {}
        }
    
    @staticmethod
    async def cancel_payment(payment_id: str) -> Dict[str, Any]:
        """
        Отменить платеж
        
        Args:
            payment_id: ID платежа в Юкассе
            
        Returns:
            Словарь с информацией об отмене
        """
        payment = Payment.cancel(payment_id)
        
        return {
            "payment_id": payment.id,
            "status": payment.status,
            "cancelled": payment.cancelled
        }
    
    @staticmethod
    def parse_webhook(webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Парсить вебхук от Юкассы
        
        Args:
            webhook_data: Данные вебхука
            
        Returns:
            Распарсенные данные вебхука
        """
        try:
            notification = WebhookNotificationFactory().create(webhook_data)
            payment_object = notification.object
            
            # Безопасное получение атрибутов
            paid = getattr(payment_object, 'paid', False)
            cancelled = getattr(payment_object, 'cancelled', False)
            
            # Альтернативный способ проверки отмены через статус
            if not cancelled and hasattr(payment_object, 'status'):
                status = str(payment_object.status).lower()
                cancelled = status == 'canceled' or status == 'cancelled'
            
            # Обработка created_at - может быть datetime или строкой
            created_at = None
            if hasattr(payment_object, 'created_at') and payment_object.created_at:
                if isinstance(payment_object.created_at, str):
                    created_at = payment_object.created_at
                else:
                    # Если это datetime объект, конвертируем в строку
                    created_at = payment_object.created_at.isoformat()
            
            return {
                "event": notification.type,
                "payment_id": payment_object.id,
                "status": payment_object.status if hasattr(payment_object, 'status') else None,
                "paid": paid,
                "cancelled": cancelled,
                "amount": Decimal(payment_object.amount.value) if hasattr(payment_object, 'amount') and payment_object.amount else Decimal('0'),
                "metadata": payment_object.metadata if hasattr(payment_object, 'metadata') else {},
                "created_at": created_at
            }
        except Exception as e:
            raise ValueError(f"Ошибка при парсинге вебхука: {str(e)}")
    
    @staticmethod
    def is_payment_succeeded(webhook_data: Dict[str, Any]) -> bool:
        """
        Проверить, успешен ли платеж
        
        Args:
            webhook_data: Данные вебхука
            
        Returns:
            True, если платеж успешен
        """
        parsed = YooKassaService.parse_webhook(webhook_data)
        return parsed.get("event") == "payment.succeeded" and parsed.get("paid", False)
    
    @staticmethod
    def is_payment_cancelled(webhook_data: Dict[str, Any]) -> bool:
        """
        Проверить, отменен ли платеж
        
        Args:
            webhook_data: Данные вебхука
            
        Returns:
            True, если платеж отменен
        """
        parsed = YooKassaService.parse_webhook(webhook_data)
        return parsed.get("event") == "payment.cancelled" or parsed.get("cancelled", False)

