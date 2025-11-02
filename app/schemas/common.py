from pydantic import BaseModel
from typing import Any, Optional


class MessageResponse(BaseModel):
    """Схема для простого сообщения"""
    message: str


class ErrorResponse(BaseModel):
    """Схема для ошибки"""
    error: str
    detail: Optional[str] = None


class SuccessResponse(BaseModel):
    """Схема для успешного ответа"""
    success: bool = True
    message: str
    data: Optional[Any] = None


class PaginationParams(BaseModel):
    """Схема для параметров пагинации"""
    skip: int = 0
    limit: int = 100


class PaginatedResponse(BaseModel):
    """Схема для пагинированного ответа"""
    items: list
    total: int
    skip: int
    limit: int
    has_next: bool
    has_prev: bool






