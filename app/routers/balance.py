from fastapi import APIRouter, Depends, Query, Request
from typing import Optional
from app.dependencies import (
    get_current_user,
    get_balance_repository,
    get_transaction_repository,
    get_payment_service
)
from app.repositories import BalanceRepository, TransactionRepository
from app.services.payment_service import PaymentService
from app.schemas.balance import (
    BalanceResponse,
    TransactionResponse,
    TransactionListResponse,
    PaymentCreate,
    PaymentResponse,
    BalanceStats
)
from app.models.user import User
from app.models.balance import TransactionType, TransactionStatus

import logging


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/balance", tags=["balance"])


@router.get("/", response_model=BalanceResponse)
async def get_balance(
    current_user: User = Depends(get_current_user),
    balance_repo: BalanceRepository = Depends(get_balance_repository)
):
    """Получить баланс текущего пользователя"""
    balance = await balance_repo.get_or_create(current_user.id)
    return balance


@router.get("/stats", response_model=BalanceStats)
async def get_balance_stats(
    current_user: User = Depends(get_current_user),
    balance_repo: BalanceRepository = Depends(get_balance_repository),
    transaction_repo: TransactionRepository = Depends(get_transaction_repository)
):
    """Получить статистику по балансу"""
    balance = await balance_repo.get_or_create(current_user.id)
    stats = await transaction_repo.get_user_transactions_stats(current_user.id)
    
    return BalanceStats(
        current_balance=balance.balance,
        total_deposited=stats['total_deposited'],
        total_withdrawn=stats['total_withdrawn'],
        total_spent=stats['total_spent'],
        transactions_count=stats['transactions_count']
    )


@router.get("/transactions", response_model=TransactionListResponse)
async def get_transactions(
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(20, ge=1, le=100, description="Количество записей на странице"),
    transaction_type: Optional[TransactionType] = Query(None, description="Фильтр по типу"),
    status: Optional[TransactionStatus] = Query(None, description="Фильтр по статусу"),
    current_user: User = Depends(get_current_user),
    transaction_repo: TransactionRepository = Depends(get_transaction_repository)
):
    """Получить список транзакций текущего пользователя"""
    skip = (page - 1) * per_page
    
    transactions = await transaction_repo.get_user_transactions(
        user_id=current_user.id,
        skip=skip,
        limit=per_page,
        transaction_type=transaction_type,
        status=status
    )
    
    total = await transaction_repo.count_user_transactions(
        user_id=current_user.id,
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


@router.post("/payment/create", response_model=PaymentResponse)
async def create_payment(
    payment_data: PaymentCreate,
    current_user: User = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Создать платеж для пополнения баланса через Юкассу"""
    return await payment_service.create_payment(current_user.id, payment_data)


@router.post("/payment/webhook")
async def payment_webhook(
    request: Request,
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Обработчик вебхука от Юкассы для уведомлений о статусе платежа"""
    logger.info(f"Webhook received from IP: {request.client.host if request.client else 'unknown'}")
    
    webhook_data = await request.json()
    return await payment_service.process_webhook(webhook_data)


@router.get("/payment/{payment_id}/status", response_model=dict)
async def get_payment_status(
    payment_id: str,
    current_user: User = Depends(get_current_user),
    payment_service: PaymentService = Depends(get_payment_service)
):
    """Получить статус платежа и обновить его в базе данных, если он изменился"""
    return await payment_service.sync_payment_status(payment_id, current_user.id)

