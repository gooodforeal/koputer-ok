"""
Исключения для модуля сборок
"""

from fastapi import status
from app.exceptions.base import BaseAppException


class BuildNotFoundError(BaseAppException):
    """Сборка не найдена"""

    def __init__(self, message: str = "Сборка не найдена", detail: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail or "Build not found",
        )


class BuildAccessDeniedError(BaseAppException):
    """Доступ к сборке запрещен"""

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


class BuildValidationError(BaseAppException):
    """Ошибка валидации данных сборки"""

    def __init__(
        self, message: str = "Ошибка валидации данных сборки", detail: str = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail or message,
        )


class RatingNotFoundError(BaseAppException):
    """Оценка не найдена"""

    def __init__(self, message: str = "Оценка не найдена", detail: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail or "Rating not found",
        )


class RatingAlreadyExistsError(BaseAppException):
    """Оценка уже существует"""

    def __init__(self, message: str = "Вы уже оценили эту сборку", detail: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail or message,
        )


class CommentNotFoundError(BaseAppException):
    """Комментарий не найден"""

    def __init__(self, message: str = "Комментарий не найден", detail: str = None):
        super().__init__(
            message=message,
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail or "Comment not found",
        )


class CommentAccessDeniedError(BaseAppException):
    """Доступ к комментарию запрещен"""

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


class ComponentCategoryError(BaseAppException):
    """Ошибка с категорией компонента"""

    def __init__(
        self, message: str = "Ошибка с категорией компонента", detail: str = None
    ):
        super().__init__(
            message=message,
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail or message,
        )
