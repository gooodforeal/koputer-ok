from sqlalchemy import Column, String, Integer, ForeignKey, Text, Enum, Index
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel


class FeedbackType(str, enum.Enum):
    """Типы отзывов"""
    BUG = "BUG"  # Сообщение об ошибке
    FEATURE = "FEATURE"  # Предложение новой функции
    IMPROVEMENT = "IMPROVEMENT"  # Предложение по улучшению
    GENERAL = "GENERAL"  # Общий отзыв


class FeedbackStatus(str, enum.Enum):
    """Статусы отзывов"""
    NEW = "NEW"  # Новый
    IN_REVIEW = "IN_REVIEW"  # На рассмотрении
    IN_PROGRESS = "IN_PROGRESS"  # В работе
    RESOLVED = "RESOLVED"  # Решено
    REJECTED = "REJECTED"  # Отклонено


class Feedback(BaseModel):
    """Модель отзыва"""
    __tablename__ = "feedbacks"

    title = Column(String(255), nullable=False)  # Заголовок отзыва
    description = Column(Text, nullable=False)  # Описание
    type = Column(Enum(FeedbackType), nullable=False)  # Тип отзыва
    status = Column(Enum(FeedbackStatus), default=FeedbackStatus.NEW, nullable=False)  # Статус
    rating = Column(Integer, nullable=True)  # Оценка (1-5), необязательно
    
    # Внешние ключи
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)  # Автор отзыва (уникальный)
    assigned_to_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Назначен администратору
    
    # Ответ администратора
    admin_response = Column(Text, nullable=True)
    
    # Связи
    user = relationship("User", foreign_keys=[user_id], back_populates="feedbacks")
    assigned_to = relationship("User", foreign_keys=[assigned_to_id], back_populates="assigned_feedbacks")
    
    # Индексы
    __table_args__ = (
        Index('ix_feedbacks_user_id', 'user_id', unique=True),
    )

