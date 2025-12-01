"""
Базовое исключение для всех доменных ошибок приложения
"""

from fastapi import status


class BaseAppException(Exception):
    """
    Базовое исключение для всех доменных ошибок приложения.
    Все доменные исключения должны наследоваться от этого класса.
    """

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        detail: str = None,
    ):
        """
        Инициализация базового исключения

        Args:
            message: Сообщение об ошибке
            status_code: HTTP статус код (по умолчанию 400)
            detail: Дополнительная информация об ошибке
        """
        self.message = message
        self.status_code = status_code
        self.detail = detail or message
        super().__init__(self.message)

    def __str__(self) -> str:
        return self.message

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(message='{self.message}', status_code={self.status_code})"
