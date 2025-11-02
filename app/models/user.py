from sqlalchemy import Column, String, Boolean, Enum
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel


class UserRole(str, enum.Enum):
    """Роли пользователей в системе"""
    USER = "USER"
    ADMIN = "ADMIN"
    SUPER_ADMIN = "SUPER_ADMIN"


class User(BaseModel):
    __tablename__ = "users"

    email = Column(String, unique=True, index=True, nullable=True)
    name = Column(String, nullable=False)
    picture = Column(String, nullable=True)
    google_id = Column(String, unique=True, index=True, nullable=True)
    telegram_id = Column(String, unique=True, index=True, nullable=True)
    username = Column(String, nullable=True)  # Telegram username
    is_active = Column(Boolean, default=True)
    role = Column(Enum(UserRole), default=UserRole.USER, nullable=False)

    # Связи с чатами
    user_chats = relationship("Chat", foreign_keys="Chat.user_id", back_populates="user")
    admin_chats = relationship("Chat", foreign_keys="Chat.admin_id", back_populates="admin")
    
    # Связи с отзывами
    feedbacks = relationship("Feedback", foreign_keys="Feedback.user_id", back_populates="user")
    assigned_feedbacks = relationship("Feedback", foreign_keys="Feedback.assigned_to_id", back_populates="assigned_to")
    
    # Связи со сборками
    builds = relationship("Build", back_populates="author", cascade="all, delete-orphan")
    build_ratings = relationship("BuildRating", back_populates="user", cascade="all, delete-orphan")
    build_comments = relationship("BuildComment", back_populates="user", cascade="all, delete-orphan")