"""
Исключения для модуля платежей
"""

from fastapi import status
from app.exceptions.base import BaseAppException


class PaymentNotFoundError(BaseAppException):
    """Платеж не найден"""

    def __init__(self, message: str = "Платеж не найден", detail: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail or "Payment not found",
        )


class PaymentCreationError(BaseAppException):
    """Ошибка при создании платежа"""

    def __init__(
        self, message: str = "Ошибка при создании платежа", detail: str = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail or message,
        )


class PaymentWebhookError(BaseAppException):
    """Ошибка при обработке вебхука платежа"""

    def __init__(
        self, message: str = "Ошибка при обработке вебхука платежа", detail: str = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail or message,
        )


class InvalidPaymentDataError(BaseAppException):
    """Невалидные данные платежа"""

    def __init__(self, message: str = "Невалидные данные платежа", detail: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail or message,
        )
