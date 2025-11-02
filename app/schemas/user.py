from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional, List
from app.models.user import UserRole


class UserBase(BaseModel):
    """Базовая схема пользователя"""
    email: Optional[EmailStr] = None
    name: str
    picture: Optional[str] = None


class UserCreate(UserBase):
    """Схема для создания пользователя"""
    google_id: Optional[str] = None
    telegram_id: Optional[str] = None
    username: Optional[str] = None


class UserResponse(UserBase):
    """Схема для ответа с данными пользователя"""
    id: int
    google_id: Optional[str] = None
    telegram_id: Optional[str] = None
    username: Optional[str] = None
    is_active: bool
    role: UserRole
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Схема для обновления пользователя"""
    name: Optional[str] = None
    email: Optional[EmailStr] = Field(max_length=30)
    picture: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None


class UserStats(BaseModel):
    """Схема для статистики пользователей"""
    total_users: int
    active_users: int
    inactive_users: int


class UserSearchResponse(BaseModel):
    """Схема для ответа с поиском пользователей"""
    users: List[UserResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


