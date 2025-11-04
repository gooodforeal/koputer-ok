"""
Сервис для работы с балансом
"""
from typing import Optional
from app.repositories import BalanceRepository, TransactionRepository
from app.models.balance import TransactionType, TransactionStatus
from app.schemas.balance import (
    BalanceResponse,
    TransactionListResponse,
    BalanceStats
)

class BalanceService:
    """Сервис для работы с балансом"""
    
    def __init__(
        self,
        balance_repo: BalanceRepository,
        transaction_repo: TransactionRepository
    ):
        self.balance_repo = balance_repo
        self.transaction_repo = transaction_repo
    
    async def get_balance(self, user_id: int) -> BalanceResponse:
        """
        Получить баланс пользователя
        
        Args:
            user_id: ID пользователя
            
        Returns:
            BalanceResponse с данными баланса
        """
        balance = await self.balance_repo.get_or_create(user_id)
        return balance
    
    async def get_balance_stats(self, user_id: int) -> BalanceStats:
        """
        Получить статистику по балансу
        
        Args:
            user_id: ID пользователя
            
        Returns:
            BalanceStats со статистикой
        """
        balance = await self.balance_repo.get_or_create(user_id)
        stats = await self.transaction_repo.get_user_transactions_stats(user_id)
        
        return BalanceStats(
            current_balance=balance.balance,
            total_deposited=stats['total_deposited'],
            total_withdrawn=stats['total_withdrawn'],
            total_spent=stats['total_spent'],
            transactions_count=stats['transactions_count']
        )
    
    async def get_transactions(
        self,
        user_id: int,
        page: int = 1,
        per_page: int = 20,
        transaction_type: Optional[TransactionType] = None,
        status: Optional[TransactionStatus] = None
    ) -> TransactionListResponse:
        """
        Получить список транзакций пользователя
        
        Args:
            user_id: ID пользователя
            page: Номер страницы
            per_page: Количество записей на странице
            transaction_type: Фильтр по типу
            status: Фильтр по статусу
            
        Returns:
            TransactionListResponse со списком транзакций
        """
        skip = (page - 1) * per_page
        
        transactions = await self.transaction_repo.get_user_transactions(
            user_id=user_id,
            skip=skip,
            limit=per_page,
            transaction_type=transaction_type,
            status=status
        )
        
        total = await self.transaction_repo.count_user_transactions(
            user_id=user_id,
            transaction_type=transaction_type,
            status=status
        )
        
        total_pages = (total + per_page - 1) // per_page
        
        return TransactionListResponse(
            transactions=transactions,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )

