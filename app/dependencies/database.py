"""
Зависимости для работы с базой данных
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db

# Базовые зависимости для работы с БД
__all__ = ["get_db_session"]


def get_db_session(db: AsyncSession = Depends(get_db)) -> AsyncSession:
    """
    Получить сессию базы данных
    
    Args:
        db: Сессия базы данных из FastAPI dependency
        
    Returns:
        AsyncSession: Сессия базы данных
    """
    return db
