"""
Исключения для модуля пользователей
"""

from fastapi import status
from app.exceptions.base import BaseAppException


class UserNotFoundError(BaseAppException):
    """Пользователь не найден"""

    def __init__(self, message: str = "Пользователь не найден", detail: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail or "User not found",
        )


class UserAlreadyExistsError(BaseAppException):
    """Пользователь уже существует"""

    def __init__(
        self, message: str = "Пользователь уже существует", detail: str = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail or "User already exists",
        )


class UserInactiveError(BaseAppException):
    """Пользователь неактивен"""

    def __init__(self, message: str = "Пользователь неактивен", detail: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail or "User is inactive",
        )


class InsufficientPermissionsError(BaseAppException):
    """Недостаточно прав доступа"""

    def __init__(self, message: str = "Недостаточно прав", detail: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail or message,
        )
