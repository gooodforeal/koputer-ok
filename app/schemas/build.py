from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from typing import Optional, List, Dict
from app.schemas.component import ComponentResponse
from app.models.component import ComponentCategory


# Схемы для сборок (Build)
class BuildBase(BaseModel):
    """Базовая схема для сборки"""
    title: str = Field(..., min_length=3, max_length=200, description="Название сборки")
    description: str = Field(..., min_length=10, max_length=5000, description="Описание сборки")
    component_ids: List[int] = Field(default=[], description="Список ID компонентов из таблицы Components")
    additional_info: Optional[str] = Field(None, description="Дополнительная информация")


class BuildCreate(BuildBase):
    """Схема для создания сборки"""
    pass


class BuildUpdate(BaseModel):
    """Схема для обновления сборки"""
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    description: Optional[str] = Field(None, min_length=10, max_length=5000)
    component_ids: Optional[List[int]] = Field(None, description="Список ID компонентов из таблицы Components")
    additional_info: Optional[str] = None


class BuildAuthor(BaseModel):
    """Схема для автора сборки"""
    id: int
    name: str
    picture: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class BuildResponse(BuildBase):
    """Схема для ответа с данными сборки"""
    id: int
    author_id: int
    author: Optional[BuildAuthor] = None
    components: List[ComponentResponse] = Field(default=[], description="Список компонентов сборки")
    views_count: int
    average_rating: float
    ratings_count: int
    total_price: float = Field(default=0.0, description="Общая стоимость сборки из суммы цен компонентов")
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class BuildListResponse(BaseModel):
    """Схема для списка сборок с пагинацией"""
    builds: List[BuildResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class BuildTopResponse(BaseModel):
    """Схема для топа сборок"""
    builds: List[BuildResponse]
    total: int


# Схемы для оценок (BuildRating)
class BuildRatingCreate(BaseModel):
    """Схема для создания оценки"""
    score: int = Field(..., ge=1, le=5, description="Оценка от 1 до 5")


class BuildRatingUpdate(BaseModel):
    """Схема для обновления оценки"""
    score: int = Field(..., ge=1, le=5, description="Оценка от 1 до 5")


class BuildRatingResponse(BaseModel):
    """Схема для ответа с данными оценки"""
    id: int
    build_id: int
    user_id: int
    score: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


# Схемы для комментариев (BuildComment)
class BuildCommentCreate(BaseModel):
    """Схема для создания комментария"""
    content: str = Field(..., min_length=1, max_length=2000, description="Текст комментария")
    parent_id: Optional[int] = Field(None, description="ID родительского комментария для ответа")


class BuildCommentUpdate(BaseModel):
    """Схема для обновления комментария"""
    content: str = Field(..., min_length=1, max_length=2000, description="Текст комментария")


class BuildCommentUser(BaseModel):
    """Схема для пользователя в комментарии"""
    id: int
    name: str
    picture: Optional[str] = None
    
    model_config = ConfigDict(from_attributes=True)


class BuildCommentReplyResponse(BaseModel):
    """Схема для ответа комментария второго уровня (без вложенных replies)"""
    id: int
    build_id: int
    user_id: int
    user: Optional[BuildCommentUser] = None
    content: str
    parent_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class BuildCommentResponse(BaseModel):
    """Схема для ответа с данными комментария корневого уровня"""
    id: int
    build_id: int
    user_id: int
    user: Optional[BuildCommentUser] = None
    content: str
    parent_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    replies: Optional[List[BuildCommentReplyResponse]] = []
    
    model_config = ConfigDict(from_attributes=True)


class BuildCommentSingleResponse(BaseModel):
    """Схема для ответа с единичным комментарием (используется при создании/обновлении)"""
    id: int
    build_id: int
    user_id: int
    user: Optional[BuildCommentUser] = None
    content: str
    parent_id: Optional[int] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    model_config = ConfigDict(from_attributes=True)


class BuildCommentListResponse(BaseModel):
    """Схема для списка комментариев"""
    comments: List[BuildCommentResponse]
    total: int


# Схемы для статистики
class BuildStatsResponse(BaseModel):
    """Схема для статистики сборок"""
    total_builds: int
    total_ratings: int
    total_comments: int
    average_rating: float


# Схема для доступных компонентов по категориям
class BuildComponentsResponse(BaseModel):
    """Схема для списка доступных компонентов по категориям"""
    components_by_category: Dict[str, List[ComponentResponse]] = Field(
        default_factory=dict,
        description="Компоненты, сгруппированные по категориям (ключ - название категории)"
    )


