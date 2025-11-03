"""
Сервис для обработки платежей
"""
from typing import Dict, Any, Optional
from decimal import Decimal
from fastapi import HTTPException, status
from app.repositories import BalanceRepository, TransactionRepository
from app.services.yookassa_service import YooKassaService
from app.models.balance import TransactionType, TransactionStatus
from app.schemas.balance import PaymentCreate, PaymentResponse
import logging


logger = logging.getLogger(__name__)


class PaymentService:
    """Сервис для обработки платежей"""
    
    def __init__(
        self,
        balance_repo: BalanceRepository,
        transaction_repo: TransactionRepository
    ):
        self.balance_repo = balance_repo
        self.transaction_repo = transaction_repo
    
    async def create_payment(
        self,
        user_id: int,
        payment_data: PaymentCreate
    ) -> PaymentResponse:
        """
        Создать платеж для пополнения баланса через Юкассу
        
        Args:
            user_id: ID пользователя
            payment_data: Данные для создания платежа
            
        Returns:
            PaymentResponse с данными платежа
        """
        # Получаем или создаем баланс
        balance = await self.balance_repo.get_or_create(user_id)
        
        # Создаем транзакцию в статусе PENDING
        transaction = await self.transaction_repo.create({
            "balance_id": balance.id,
            "user_id": user_id,
            "amount": payment_data.amount,
            "transaction_type": TransactionType.DEPOSIT,
            "status": TransactionStatus.PENDING,
            "description": payment_data.description or "Пополнение баланса",
            "payment_method": "YooKassa"
        })
        
        # Создаем платеж в Юкассе
        try:
            payment_info = await YooKassaService.create_payment(
                amount=payment_data.amount,
                user_id=user_id,
                description=payment_data.description or "Пополнение баланса",
                return_url=payment_data.return_url,
                metadata={
                    "transaction_id": transaction.id,
                    "balance_id": balance.id
                }
            )
            
            # Обновляем транзакцию с payment_id
            await self.transaction_repo.update(
                transaction,
                payment_id=payment_info["payment_id"]
            )
            
            return PaymentResponse(
                payment_id=payment_info["payment_id"],
                confirmation_url=payment_info["confirmation_url"],
                amount=payment_info["amount"],
                status=payment_info["status"]
            )
        except Exception as e:
            # Если ошибка при создании платежа, обновляем статус транзакции
            await self.transaction_repo.update(
                transaction,
                status=TransactionStatus.FAILED
            )
            logger.error(f"Error creating payment: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при создании платежа: {str(e)}"
            )
    
    async def process_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обработать вебхук от Юкассы для уведомлений о статусе платежа
        
        Args:
            webhook_data: Данные вебхука от Юкассы
            
        Returns:
            Словарь с результатом обработки
        """
        try:
            
            # Парсим вебхук
            parsed_data = YooKassaService.parse_webhook(webhook_data)
            payment_id = parsed_data["payment_id"]
            event = parsed_data.get("event")
            
            logger.info(f"Parsed payment_id: {payment_id}, event: {event}")
            
            # Находим транзакцию по payment_id
            transaction = await self.transaction_repo.get_by_payment_id(payment_id)
            if not transaction:
                logger.warning(f"Transaction not found for payment_id: {payment_id}")
                # Логируем, но не возвращаем ошибку, чтобы Юкасса не отправляла повторные запросы
                return {"status": "ok", "message": "Transaction not found"}
            
            logger.info(f"Found transaction {transaction.id} with status {transaction.status}")
            
            # Обрабатываем разные события
            if event == "payment.succeeded" and parsed_data.get("paid"):
                await self._handle_successful_payment(transaction)
            elif event == "payment.cancelled" or parsed_data.get("cancelled"):
                await self._handle_cancelled_payment(transaction)
            
            logger.info(f"Webhook processed successfully for payment {payment_id}")
            return {"status": "ok"}
            
        except Exception as e:
            # Детальное логирование ошибки
            import traceback
            logger.error(f"Error processing webhook: {str(e)}")
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Возвращаем успех, чтобы Юкасса не отправляла повторные запросы
            return {"status": "error", "message": str(e)}
    
    async def sync_payment_status(
        self,
        payment_id: str,
        user_id: int
    ) -> Dict[str, Any]:
        """
        Получить статус платежа и обновить его в базе данных, если он изменился
        
        Args:
            payment_id: ID платежа в Юкассе
            user_id: ID пользователя для проверки доступа
            
        Returns:
            Словарь с информацией о статусе платежа
        """
        # Проверяем, что транзакция принадлежит пользователю
        transaction = await self.transaction_repo.get_by_payment_id(payment_id)
        if not transaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Платеж не найден"
            )
        
        if transaction.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Доступ запрещен"
            )
        
        # Получаем статус из Юкассы
        try:
            payment_status = await YooKassaService.get_payment_status(payment_id)
            paid = payment_status["paid"]
            cancelled = payment_status["cancelled"]
            yookassa_status = payment_status["status"]
            
            # Обновляем статус транзакции, если он изменился в Юкассе
            if transaction.status == TransactionStatus.PENDING:
                if paid and yookassa_status in ["succeeded", "paid"]:
                    # Платеж успешен - пополняем баланс
                    await self._handle_successful_payment(transaction)
                elif cancelled or yookassa_status in ["canceled", "cancelled"]:
                    # Платеж отменен
                    await self._handle_cancelled_payment(transaction)
            
            # Обновляем транзакцию для получения актуального статуса
            await self.transaction_repo.db.refresh(transaction)
            
            return {
                "payment_id": payment_status["payment_id"],
                "status": payment_status["status"],
                "paid": paid,
                "cancelled": cancelled,
                "transaction_status": transaction.status.value,
                "amount": float(payment_status["amount"])
            }
        except Exception as e:
            logger.error(f"Error getting payment status: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Ошибка при получении статуса платежа: {str(e)}"
            )
    
    async def _handle_successful_payment(self, transaction) -> None:
        """
        Обработать успешный платеж - пополнить баланс и обновить транзакцию
        
        Args:
            transaction: Транзакция для обработки
        """
        if transaction.status != TransactionStatus.PENDING:
            logger.info(
                f"Transaction {transaction.id} status is {transaction.status}, "
                "skipping deposit"
            )
            return
        
        logger.info(f"Processing successful payment for transaction {transaction.id}")
        
        # Получаем баланс
        balance = await self.balance_repo.get_by_user_id(transaction.user_id)
        if not balance:
            balance = await self.balance_repo.get_or_create(transaction.user_id)
        
        logger.info(f"Balance before deposit: {balance.balance}")
        
        # Пополняем баланс
        await self.balance_repo.deposit(transaction.user_id, transaction.amount)
        
        # Обновляем статус транзакции
        await self.transaction_repo.update(
            transaction,
            status=TransactionStatus.COMPLETED
        )
        
        # Обновляем баланс для получения актуального значения
        await self.balance_repo.db.refresh(balance)
        logger.info(
            f"Balance after deposit: {balance.balance}, "
            f"Transaction {transaction.id} updated to COMPLETED"
        )
    
    async def _handle_cancelled_payment(self, transaction) -> None:
        """
        Обработать отмененный платеж - обновить статус транзакции
        
        Args:
            transaction: Транзакция для обработки
        """
        if transaction.status != TransactionStatus.PENDING:
            logger.info(
                f"Transaction {transaction.id} status is {transaction.status}, "
                "skipping cancellation"
            )
            return
        
        logger.info(f"Processing cancelled payment for transaction {transaction.id}")
        
        # Обновляем статус транзакции
        await self.transaction_repo.update(
            transaction,
            status=TransactionStatus.CANCELLED
        )
        
        logger.info(f"Transaction {transaction.id} updated to CANCELLED")

