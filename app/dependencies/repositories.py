"""
Зависимости для репозиториев
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import UserRepository, BuildRepository
from app.repositories.chat_repository import ChatRepository
from app.repositories.feedback_repository import FeedbackRepository
from app.repositories.component_repository import ComponentRepository
from .database import get_db_session

# Зависимости для репозиториев
__all__ = ["get_user_repository", "get_chat_repository", "get_feedback_repository", "get_build_repository", "get_component_repository"]


def get_user_repository(db: AsyncSession = Depends(get_db_session)) -> UserRepository:
    """
    Получить экземпляр UserRepository
    
    Args:
        db: Сессия базы данных
        
    Returns:
        UserRepository: Экземпляр репозитория пользователей
    """
    return UserRepository(db)


def get_chat_repository(db: AsyncSession = Depends(get_db_session)) -> ChatRepository:
    """
    Получить экземпляр ChatRepository
    
    Args:
        db: Сессия базы данных
        
    Returns:
        ChatRepository: Экземпляр репозитория чатов
    """
    return ChatRepository(db)


def get_feedback_repository(db: AsyncSession = Depends(get_db_session)) -> FeedbackRepository:
    """
    Получить экземпляр FeedbackRepository
    
    Args:
        db: Сессия базы данных
        
    Returns:
        FeedbackRepository: Экземпляр репозитория отзывов
    """
    return FeedbackRepository(db)


def get_build_repository(db: AsyncSession = Depends(get_db_session)) -> BuildRepository:
    """
    Получить экземпляр BuildRepository
    
    Args:
        db: Сессия базы данных
        
    Returns:
        BuildRepository: Экземпляр репозитория сборок
    """
    return BuildRepository(db)


def get_component_repository(db: AsyncSession = Depends(get_db_session)) -> ComponentRepository:
    """
    Получить экземпляр ComponentRepository
    
    Args:
        db: Сессия базы данных
        
    Returns:
        ComponentRepository: Экземпляр репозитория компонентов
    """
    return ComponentRepository(db)
