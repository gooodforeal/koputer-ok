from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
from datetime import datetime
from app.models.feedback import FeedbackType, FeedbackStatus


class FeedbackBase(BaseModel):
    """Базовая схема отзыва"""
    title: str = Field(..., min_length=3, max_length=255, description="Заголовок отзыва")
    description: str = Field(..., min_length=10, description="Описание отзыва")
    type: FeedbackType = Field(..., description="Тип отзыва")
    rating: Optional[int] = Field(None, ge=1, le=5, description="Оценка от 1 до 5")


class FeedbackCreate(FeedbackBase):
    """Схема для создания отзыва"""
    pass


class FeedbackUpdate(BaseModel):
    """Схема для обновления отзыва"""
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = Field(None, min_length=10)
    type: Optional[FeedbackType] = None
    rating: Optional[int] = Field(None, ge=1, le=5)


class FeedbackAdminUpdate(BaseModel):
    """Схема для обновления отзыва администратором"""
    status: Optional[FeedbackStatus] = None
    assigned_to_id: Optional[int] = None
    admin_response: Optional[str] = None


class FeedbackUserInfo(BaseModel):
    """Информация о пользователе"""
    id: int
    name: str
    email: Optional[str] = None
    picture: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class FeedbackResponse(FeedbackBase):
    """Схема ответа с отзывом"""
    id: int
    status: FeedbackStatus
    user_id: int
    assigned_to_id: Optional[int] = None
    admin_response: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    user: FeedbackUserInfo
    assigned_to: Optional[FeedbackUserInfo] = None
    
    model_config = ConfigDict(from_attributes=True)


class FeedbackListItem(BaseModel):
    """Упрощенная схема отзыва для списков"""
    id: int
    title: str
    type: FeedbackType
    status: FeedbackStatus
    rating: Optional[int] = None
    user_id: int
    user_name: str
    assigned_to_id: Optional[int] = None
    assigned_to_name: Optional[str] = None
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class FeedbackListResponse(BaseModel):
    """Схема ответа со списком отзывов и пагинацией"""
    feedbacks: List[FeedbackResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class FeedbackStats(BaseModel):
    """Статистика по отзывам"""
    total: int
    new: int
    in_review: int
    in_progress: int
    resolved: int
    rejected: int
    by_type: dict[str, int]
    average_rating: Optional[float] = None

