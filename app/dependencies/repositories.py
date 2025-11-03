"""
Зависимости для репозиториев и сервисов
"""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import UserRepository, BuildRepository, BalanceRepository, TransactionRepository
from app.repositories.chat_repository import ChatRepository
from app.repositories.feedback_repository import FeedbackRepository
from app.repositories.component_repository import ComponentRepository
from app.services.payment_service import PaymentService
from .database import get_db_session

# Зависимости для репозиториев
__all__ = ["get_user_repository", "get_chat_repository", "get_feedback_repository", "get_build_repository", "get_component_repository", "get_balance_repository", "get_transaction_repository", "get_payment_service"]


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


def get_balance_repository(db: AsyncSession = Depends(get_db_session)) -> BalanceRepository:
    """
    Получить экземпляр BalanceRepository
    
    Args:
        db: Сессия базы данных
        
    Returns:
        BalanceRepository: Экземпляр репозитория балансов
    """
    return BalanceRepository(db)


def get_transaction_repository(db: AsyncSession = Depends(get_db_session)) -> TransactionRepository:
    """
    Получить экземпляр TransactionRepository
    
    Args:
        db: Сессия базы данных
        
    Returns:
        TransactionRepository: Экземпляр репозитория транзакций
    """
    return TransactionRepository(db)


def get_payment_service(
    balance_repo: BalanceRepository = Depends(get_balance_repository),
    transaction_repo: TransactionRepository = Depends(get_transaction_repository)
) -> PaymentService:
    """
    Получить экземпляр PaymentService
    
    Args:
        balance_repo: Репозиторий балансов
        transaction_repo: Репозиторий транзакций
        
    Returns:
        PaymentService: Экземпляр сервиса платежей
    """
    return PaymentService(balance_repo, transaction_repo)
