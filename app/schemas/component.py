from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from app.models.component import ComponentCategory


class ComponentResponse(BaseModel):
    """Схема ответа для компонента"""
    id: int
    name: str
    link: str
    price: Optional[int]
    image: Optional[str]
    category: ComponentCategory
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ParseStatusResponse(BaseModel):
    """Схема ответа для статуса парсинга"""
    is_running: bool
    current_category: Optional[str] = None
    processed_categories: int = 0
    total_categories: int = 0
    processed_products: int = 0
    errors: list[str] = []


class ParseStartResponse(BaseModel):
    """Схема ответа для запуска парсинга"""
    message: str
    status: str

