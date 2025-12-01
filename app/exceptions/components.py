"""
Исключения для модуля компонентов
"""

from fastapi import status
from app.exceptions.base import BaseAppException


class ComponentNotFoundError(BaseAppException):
    """Компонент не найден"""

    def __init__(self, message: str = "Компонент не найден", detail: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail or "Component not found",
        )


class ComponentParseError(BaseAppException):
    """Ошибка при парсинге компонентов"""

    def __init__(
        self, message: str = "Ошибка при парсинге компонентов", detail: str = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail or message,
        )


class ComponentParseAlreadyRunningError(BaseAppException):
    """Парсинг уже запущен"""

    def __init__(self, message: str = "Парсинг уже запущен", detail: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail or message,
        )


class ComponentParseNotRunningError(BaseAppException):
    """Парсинг не запущен"""

    def __init__(self, message: str = "Парсинг не запущен", detail: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail or message,
        )


class InvalidComponentCategoryError(BaseAppException):
    """Неизвестная категория компонента"""

    def __init__(self, category: str = None, message: str = None, detail: str = None):
        if message is None:
            message = (
                f"Неизвестная категория: {category}"
                if category
                else "Неизвестная категория"
            )
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail or message,
        )
