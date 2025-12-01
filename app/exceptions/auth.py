"""
Исключения для модуля авторизации
"""

from fastapi import status
from app.exceptions.base import BaseAppException


class AuthenticationError(BaseAppException):
    """Общая ошибка аутентификации"""

    def __init__(self, message: str = "Ошибка аутентификации", detail: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail or message,
        )


class InvalidCredentialsError(AuthenticationError):
    """Неверные учетные данные"""

    def __init__(
        self, message: str = "Не удалось проверить учетные данные", detail: str = None
    ):
        super().__init__(
            message=message, detail=detail or "Could not validate credentials"
        )


class TokenNotFoundError(AuthenticationError):
    """Токен не найден или истек"""

    def __init__(self, message: str = "Токен не найден или истек", detail: str = None):
        super().__init__(message=message, detail=detail or "Token not found or expired")


class TokenExpiredError(AuthenticationError):
    """Токен истек"""

    def __init__(self, message: str = "Токен истек", detail: str = None):
        super().__init__(message=message, detail=detail or "Token expired")


class TokenAlreadyUsedError(BaseAppException):
    """Токен уже был использован"""

    def __init__(self, message: str = "Токен уже был использован", detail: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail or "Token already used",
        )


class FailedToLinkTokenError(BaseAppException):
    """Не удалось связать токен с пользователем"""

    def __init__(
        self,
        message: str = "Не удалось связать токен с пользователем",
        detail: str = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail or "Failed to link token with user",
        )


class FailedToSaveTokenError(BaseAppException):
    """Не удалось сохранить токен"""

    def __init__(
        self, message: str = "Не удалось сохранить JWT токен", detail: str = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail or "Failed to save JWT token",
        )


class GoogleAuthError(BaseAppException):
    """Ошибка при авторизации через Google"""

    def __init__(
        self, message: str = "Ошибка при авторизации через Google", detail: str = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail or message,
        )


class TelegramAuthError(BaseAppException):
    """Ошибка при авторизации через Telegram"""

    def __init__(
        self, message: str = "Ошибка при авторизации через Telegram", detail: str = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail or message,
        )
