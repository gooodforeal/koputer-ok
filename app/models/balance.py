from sqlalchemy import Column, Integer, ForeignKey, Numeric, String, Enum, Text, Index
from sqlalchemy.orm import relationship
import enum
from app.models.base import BaseModel


class TransactionType(str, enum.Enum):
    """Типы транзакций"""
    DEPOSIT = "DEPOSIT"  # Пополнение
    WITHDRAWAL = "WITHDRAWAL"  # Списание
    PAYMENT = "PAYMENT"  # Платеж за услугу
    REFUND = "REFUND"  # Возврат средств


class TransactionStatus(str, enum.Enum):
    """Статусы транзакций"""
    PENDING = "PENDING"  # Ожидает обработки
    COMPLETED = "COMPLETED"  # Завершена
    FAILED = "FAILED"  # Неудачная
    CANCELLED = "CANCELLED"  # Отменена


class Balance(BaseModel):
    """Модель баланса пользователя"""
    __tablename__ = "balances"

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True, nullable=False)
    balance = Column(Numeric(10, 2), default=0.00, nullable=False)  # Текущий баланс

    # Связи
    user = relationship("User", back_populates="balance", uselist=False)
    transactions = relationship("Transaction", back_populates="balance", cascade="all, delete-orphan", order_by="Transaction.created_at.desc()")

    __table_args__ = (
        Index('ix_balances_user_id', 'user_id'),
    )


class Transaction(BaseModel):
    """Модель транзакции"""
    __tablename__ = "transactions"

    balance_id = Column(Integer, ForeignKey("balances.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    amount = Column(Numeric(10, 2), nullable=False)  # Сумма транзакции
    transaction_type = Column(Enum(TransactionType), nullable=False)  # Тип транзакции
    status = Column(Enum(TransactionStatus), default=TransactionStatus.PENDING, nullable=False)
    
    # Поля для интеграции с Юкассой
    payment_id = Column(String(255), nullable=True, unique=True)  # ID платежа в Юкассе
    payment_method = Column(String(50), nullable=True)  # Метод оплаты (YooKassa, manual, etc.)
    
    # Описание транзакции
    description = Column(Text, nullable=True)
    metadata_json = Column(Text, nullable=True)  # JSON строка с дополнительными данными

    # Связи
    balance = relationship("Balance", back_populates="transactions")
    user = relationship("User", back_populates="transactions")

    __table_args__ = (
        Index('ix_transactions_balance_id', 'balance_id'),
        Index('ix_transactions_user_id', 'user_id'),
        Index('ix_transactions_status', 'status'),
        Index('ix_transactions_type', 'transaction_type'),
        Index('ix_transactions_payment_id', 'payment_id'),
        Index('ix_transactions_user_created', 'user_id', 'created_at'),
    )

