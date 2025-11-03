from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from decimal import Decimal
from app.models.balance import TransactionType, TransactionStatus


class BalanceResponse(BaseModel):
    """Схема для ответа с балансом пользователя"""
    id: int
    user_id: int
    balance: Decimal
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TransactionBase(BaseModel):
    """Базовая схема транзакции"""
    amount: Decimal = Field(..., gt=0, description="Сумма транзакции")
    transaction_type: TransactionType
    description: Optional[str] = None
    metadata_json: Optional[str] = None


class TransactionCreate(TransactionBase):
    """Схема для создания транзакции"""
    pass


class TransactionResponse(BaseModel):
    """Схема для ответа с транзакцией"""
    id: int
    balance_id: int
    user_id: int
    amount: Decimal
    transaction_type: TransactionType
    status: TransactionStatus
    payment_id: Optional[str] = None
    payment_method: Optional[str] = None
    description: Optional[str] = None
    metadata_json: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TransactionListResponse(BaseModel):
    """Схема для списка транзакций с пагинацией"""
    transactions: List[TransactionResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class PaymentCreate(BaseModel):
    """Схема для создания платежа"""
    amount: Decimal = Field(..., gt=0, description="Сумма пополнения")
    description: Optional[str] = "Пополнение баланса"
    return_url: Optional[str] = None  # URL для возврата после оплаты


class PaymentResponse(BaseModel):
    """Схема для ответа с данными платежа"""
    payment_id: str
    confirmation_url: str
    amount: Decimal
    status: str


class PaymentWebhook(BaseModel):
    """Схема для вебхука от Юкассы"""
    event: str
    object: dict


class BalanceStats(BaseModel):
    """Статистика по балансу"""
    current_balance: Decimal
    total_deposited: Decimal
    total_withdrawn: Decimal
    total_spent: Decimal
    transactions_count: int

