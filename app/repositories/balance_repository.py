from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import Optional, List
from decimal import Decimal
from app.models.balance import Balance, Transaction, TransactionType, TransactionStatus
from app.schemas.balance import TransactionCreate


class BalanceRepository:
    """Репозиторий для работы с балансами"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_user_id(self, user_id: int) -> Optional[Balance]:
        """Получить баланс пользователя"""
        result = await self.db.execute(
            select(Balance).filter(Balance.user_id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_or_create(self, user_id: int) -> Balance:
        """Получить баланс или создать новый"""
        balance = await self.get_by_user_id(user_id)
        if not balance:
            balance = Balance(user_id=user_id, balance=Decimal('0.00'))
            self.db.add(balance)
            await self.db.commit()
            await self.db.refresh(balance)
        return balance
    
    async def update_balance(self, balance: Balance, amount: Decimal) -> Balance:
        """Обновить баланс (пополнение или списание)"""
        balance.balance += amount
        await self.db.commit()
        await self.db.refresh(balance)
        return balance
    
    async def deposit(self, user_id: int, amount: Decimal) -> Balance:
        """Пополнить баланс"""
        balance = await self.get_or_create(user_id)
        return await self.update_balance(balance, amount)
    
    async def withdraw(self, user_id: int, amount: Decimal) -> Optional[Balance]:
        """Списать с баланса"""
        balance = await self.get_by_user_id(user_id)
        if not balance:
            return None
        if balance.balance < amount:
            raise ValueError("Недостаточно средств на балансе")
        return await self.update_balance(balance, -amount)


class TransactionRepository:
    """Репозиторий для работы с транзакциями"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, transaction_id: int) -> Optional[Transaction]:
        """Получить транзакцию по ID"""
        result = await self.db.execute(
            select(Transaction).filter(Transaction.id == transaction_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_payment_id(self, payment_id: str) -> Optional[Transaction]:
        """Получить транзакцию по ID платежа"""
        result = await self.db.execute(
            select(Transaction).filter(Transaction.payment_id == payment_id)
        )
        return result.scalar_one_or_none()
    
    async def create(self, transaction_data: dict) -> Transaction:
        """Создать транзакцию"""
        transaction = Transaction(**transaction_data)
        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction)
        return transaction
    
    async def update(self, transaction: Transaction, **kwargs) -> Transaction:
        """Обновить транзакцию"""
        for key, value in kwargs.items():
            if hasattr(transaction, key):
                setattr(transaction, key, value)
        await self.db.commit()
        await self.db.refresh(transaction)
        return transaction
    
    async def get_user_transactions(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 100,
        transaction_type: Optional[TransactionType] = None,
        status: Optional[TransactionStatus] = None
    ) -> List[Transaction]:
        """Получить транзакции пользователя с фильтрами"""
        stmt = select(Transaction).filter(Transaction.user_id == user_id)
        
        if transaction_type:
            stmt = stmt.filter(Transaction.transaction_type == transaction_type)
        
        if status:
            stmt = stmt.filter(Transaction.status == status)
        
        stmt = stmt.order_by(Transaction.created_at.desc())
        stmt = stmt.offset(skip).limit(limit)
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def count_user_transactions(
        self,
        user_id: int,
        transaction_type: Optional[TransactionType] = None,
        status: Optional[TransactionStatus] = None
    ) -> int:
        """Подсчитать количество транзакций пользователя"""
        stmt = select(func.count(Transaction.id)).filter(Transaction.user_id == user_id)
        
        if transaction_type:
            stmt = stmt.filter(Transaction.transaction_type == transaction_type)
        
        if status:
            stmt = stmt.filter(Transaction.status == status)
        
        result = await self.db.execute(stmt)
        return result.scalar() or 0
    
    async def get_pending_payment_transactions(self) -> List[Transaction]:
        """Получить все транзакции со статусом PENDING, у которых есть payment_id"""
        result = await self.db.execute(
            select(Transaction).filter(
                and_(
                    Transaction.status == TransactionStatus.PENDING,
                    Transaction.payment_id.isnot(None)
                )
            ).order_by(Transaction.created_at.asc())
        )
        return list(result.scalars().all())
    
    async def get_user_transactions_stats(self, user_id: int) -> dict:
        """Получить статистику транзакций пользователя"""
        # Общая сумма пополнений
        deposit_stmt = select(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.transaction_type == TransactionType.DEPOSIT,
                Transaction.status == TransactionStatus.COMPLETED
            )
        )
        total_deposited = await self.db.execute(deposit_stmt)
        total_deposited = total_deposited.scalar() or Decimal('0.00')
        
        # Общая сумма списаний
        withdrawal_stmt = select(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.transaction_type == TransactionType.WITHDRAWAL,
                Transaction.status == TransactionStatus.COMPLETED
            )
        )
        total_withdrawn = await self.db.execute(withdrawal_stmt)
        total_withdrawn = total_withdrawn.scalar() or Decimal('0.00')
        
        # Общая сумма платежей
        payment_stmt = select(func.sum(Transaction.amount)).filter(
            and_(
                Transaction.user_id == user_id,
                Transaction.transaction_type == TransactionType.PAYMENT,
                Transaction.status == TransactionStatus.COMPLETED
            )
        )
        total_spent = await self.db.execute(payment_stmt)
        total_spent = total_spent.scalar() or Decimal('0.00')
        
        # Количество транзакций
        count_stmt = select(func.count(Transaction.id)).filter(
            Transaction.user_id == user_id
        )
        transactions_count = await self.db.execute(count_stmt)
        transactions_count = transactions_count.scalar() or 0
        
        return {
            'total_deposited': total_deposited,
            'total_withdrawn': total_withdrawn,
            'total_spent': total_spent,
            'transactions_count': transactions_count
        }

