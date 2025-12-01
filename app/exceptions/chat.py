"""
Исключения для модуля чата
"""

from fastapi import status
from app.exceptions.base import BaseAppException


class ChatNotFoundError(BaseAppException):
    """Чат не найден"""

    def __init__(self, message: str = "Чат не найден", detail: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail or "Chat not found",
        )


class ChatAccessDeniedError(BaseAppException):
    """Доступ к чату запрещен"""

    def __init__(
        self,
        message: str = "У вас нет прав для доступа к этому чату",
        detail: str = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail or message,
        )


class MessageNotFoundError(BaseAppException):
    """Сообщение не найдено"""

    def __init__(self, message: str = "Сообщение не найдено", detail: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail or "Message not found",
        )


class MessageAccessDeniedError(BaseAppException):
    """Доступ к сообщению запрещен"""

    def __init__(
        self,
        message: str = "У вас нет прав для выполнения этого действия",
        detail: str = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail or message,
        )


class ChatAlreadyExistsError(BaseAppException):
    """Чат уже существует"""

    def __init__(
        self, message: str = "У вас уже есть активный чат", detail: str = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail or message,
        )


class InvalidChatStatusError(BaseAppException):
    """Невалидный статус чата"""

    def __init__(self, message: str = "Невалидный статус чата", detail: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail or message,
        )
