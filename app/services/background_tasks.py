"""
Сервис для фоновых задач приложения
"""
import asyncio
import logging
from datetime import datetime, timezone, timedelta


logger = logging.getLogger(__name__)


async def cleanup_cache_task():
    """Периодическая очистка устаревшего кэша"""
    while True:
        try:
            from app.dependencies.auth import cleanup_expired_cache

            active_count = await cleanup_expired_cache()
            print(f"Активных записей в кэше пользователей: {active_count}")
        except ImportError:
            # Если импорт не удался, игнорируем
            pass
        except Exception as e:
            print(f"Ошибка при очистке кэша пользователей: {e}")
        await asyncio.sleep(300)  # Очищаем каждые 5 минут


async def cleanup_auth_tokens_task():
    """Периодическая очистка истекших токенов авторизации"""
    while True:
        try:
            from app.services.auth_tokens import auth_token_storage

            active_count = await auth_token_storage.cleanup_expired_tokens()
        except Exception as e:
            print(f"Ошибка при очистке токенов: {e}")
        await asyncio.sleep(60)  # Очищаем каждую минуту


async def check_pending_payments_task():
    """Периодическая проверка статусов ожидающих платежей"""
    while True:
        try:
            from app.database import AsyncSessionLocal
            from app.repositories import TransactionRepository, BalanceRepository
            from app.services.yookassa_service import YooKassaService
            from app.models.balance import TransactionStatus

            async with AsyncSessionLocal() as db:
                transaction_repo = TransactionRepository(db)
                balance_repo = BalanceRepository(db)
                
                # Получаем все транзакции со статусом PENDING, у которых есть payment_id
                pending_transactions = await transaction_repo.get_pending_payment_transactions()
                
                if pending_transactions:
                    logger.info(f"Проверка статусов {len(pending_transactions)} ожидающих платежей")   
                
                for transaction in pending_transactions:
                    if not transaction.payment_id:
                        continue
                    
                    try:
                        # Проверяем, не прошло ли 5 минут с момента создания транзакции
                        if transaction.created_at:
                            # Вычисляем разницу во времени
                            now = datetime.now(timezone.utc)
                            if isinstance(transaction.created_at, datetime):
                                time_diff = now - transaction.created_at
                            else:
                                # Если created_at это строка, парсим её
                                try:
                                    created_at = datetime.fromisoformat(str(transaction.created_at).replace('Z', '+00:00'))
                                    time_diff = now - created_at
                                except (ValueError, AttributeError):
                                    time_diff = timedelta(0)
                            
                            # Если прошло более 5 минут и платеж все еще не оплачен
                            if time_diff > timedelta(minutes=5) and transaction.status == TransactionStatus.PENDING:
                                await transaction_repo.update(
                                    transaction,
                                    status=TransactionStatus.CANCELLED
                                )
                                logger.info(
                                    f"Платеж {transaction.payment_id} отменен по таймауту (прошло {time_diff.total_seconds() / 60:.1f} минут). "
                                    f"Транзакция {transaction.id} обновлена на CANCELLED"
                                )
                                continue  # Переходим к следующей транзакции
                        
                        # Получаем статус из Юкассы
                        payment_status = await YooKassaService.get_payment_status(transaction.payment_id)
                        paid = payment_status.get("paid", False)
                        cancelled = payment_status.get("cancelled", False)
                        yookassa_status = payment_status.get("status", "")
                        
                        # Обновляем статус транзакции, если он изменился
                        if transaction.status == TransactionStatus.PENDING:
                            if paid and yookassa_status in ["succeeded", "paid"]:
                                # Платеж успешен - пополняем баланс
                                balance = await balance_repo.get_by_user_id(transaction.user_id)
                                if not balance:
                                    balance = await balance_repo.get_or_create(transaction.user_id)
                                
                                await balance_repo.deposit(transaction.user_id, transaction.amount)
                                await transaction_repo.update(
                                    transaction,
                                    status=TransactionStatus.COMPLETED
                                )
                                logger.info(
                                    f"Платеж {transaction.payment_id} завершен. "
                                    f"Транзакция {transaction.id} обновлена на COMPLETED. "
                                    f"Баланс пользователя {transaction.user_id} пополнен на {transaction.amount}"
                                )
                            elif cancelled or yookassa_status in ["canceled", "cancelled"]:
                                # Платеж отменен
                                await transaction_repo.update(
                                    transaction,
                                    status=TransactionStatus.CANCELLED
                                )
                                logger.info(
                                    f"Платеж {transaction.payment_id} отменен. "
                                    f"Транзакция {transaction.id} обновлена на CANCELLED"
                                )
                    except Exception as e:
                        logger.error(
                            f"Ошибка при проверке статуса платежа {transaction.payment_id} "
                            f"(транзакция {transaction.id}): {str(e)}"
                        )
                        # Продолжаем проверку других транзакций
                        continue
                
        except Exception as e:
            logger.error(f"Ошибка в задаче проверки платежей: {e}")
        
        await asyncio.sleep(30)  # Проверяем каждые 30 секунд
