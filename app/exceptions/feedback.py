"""
Исключения для модуля отзывов
"""

from fastapi import status
from app.exceptions.base import BaseAppException


class FeedbackNotFoundError(BaseAppException):
    """Отзыв не найден"""

    def __init__(self, message: str = "Отзыв не найден", detail: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail or "Feedback not found",
        )


class FeedbackAlreadyExistsError(BaseAppException):
    """Отзыв уже существует"""

    def __init__(
        self,
        message: str = "Вы уже оставили отзыв. Вы можете отредактировать существующий отзыв.",
        detail: str = None,
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail or message,
        )


class FeedbackAccessDeniedError(BaseAppException):
    """Доступ к отзыву запрещен"""

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


class FeedbackValidationError(BaseAppException):
    """Ошибка валидации данных отзыва"""

    def __init__(
        self, message: str = "Ошибка валидации данных отзыва", detail: str = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail or message,
        )
