from sqlalchemy import Column, Integer, String, ForeignKey, Text, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel


class ChatStatus(str, enum.Enum):
    """Статусы чата"""
    OPEN = "OPEN"  # Открыт
    IN_PROGRESS = "IN_PROGRESS"  # В работе
    CLOSED = "CLOSED"  # Закрыт


class Chat(BaseModel):
    """Модель чата между пользователем и администратором"""
    __tablename__ = "chats"

    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    admin_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Может быть null если чат еще не назначен
    is_active = Column(Boolean, default=True)
    status = Column(Enum(ChatStatus), default=ChatStatus.OPEN, nullable=False)  # Статус чата
    last_message_at = Column(DateTime(timezone=True), nullable=True)  # Время последнего сообщения

    # Связи
    user = relationship("User", foreign_keys=[user_id], back_populates="user_chats")
    admin = relationship("User", foreign_keys=[admin_id], back_populates="admin_chats")
    messages = relationship("Message", back_populates="chat", cascade="all, delete-orphan")


class Message(BaseModel):
    """Модель сообщения в чате"""
    __tablename__ = "messages"

    chat_id = Column(Integer, ForeignKey("chats.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    message_type = Column(String, default="text")  # text, image, file, etc.

    # Связи
    chat = relationship("Chat", back_populates="messages")
    sender = relationship("User", foreign_keys=[sender_id])
