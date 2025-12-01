"""
Исключения для модуля баланса
"""

from fastapi import status
from app.exceptions.base import BaseAppException


class BalanceNotFoundError(BaseAppException):
    """Баланс не найден"""

    def __init__(self, message: str = "Баланс не найден", detail: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail or "Balance not found",
        )


class InsufficientBalanceError(BaseAppException):
    """Недостаточно средств на балансе"""

    def __init__(
        self, message: str = "Недостаточно средств на балансе", detail: str = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail or message,
        )


class TransactionNotFoundError(BaseAppException):
    """Транзакция не найдена"""

    def __init__(self, message: str = "Транзакция не найдена", detail: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail or "Transaction not found",
        )


class InvalidTransactionError(BaseAppException):
    """Невалидная транзакция"""

    def __init__(self, message: str = "Невалидная транзакция", detail: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail or message,
        )
