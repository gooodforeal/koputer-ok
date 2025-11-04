from fastapi import APIRouter, Depends, Query, Request
from typing import Optional
from app.dependencies import get_current_user
from app.dependencies.repositories import (
    get_balance_service,
    get_payment_service
)
from app.services.balance_service import BalanceService
from app.services.payment_service import PaymentService
from app.schemas.balance import (
    BalanceResponse,
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
    balance_service: BalanceService = Depends(get_balance_service)
):
    """Получить баланс текущего пользователя"""
    return await balance_service.get_balance(current_user.id)


@router.get("/stats", response_model=BalanceStats)
async def get_balance_stats(
    current_user: User = Depends(get_current_user),
    balance_service: BalanceService = Depends(get_balance_service)
):
    """Получить статистику по балансу"""
    return await balance_service.get_balance_stats(current_user.id)


@router.get("/transactions", response_model=TransactionListResponse)
async def get_transactions(
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(20, ge=1, le=100, description="Количество записей на странице"),
    transaction_type: Optional[TransactionType] = Query(None, description="Фильтр по типу"),
    status: Optional[TransactionStatus] = Query(None, description="Фильтр по статусу"),
    current_user: User = Depends(get_current_user),
    balance_service: BalanceService = Depends(get_balance_service)
):
    """Получить список транзакций текущего пользователя"""
    return await balance_service.get_transactions(
        user_id=current_user.id,
        page=page,
        per_page=per_page,
        transaction_type=transaction_type,
        status=status
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

