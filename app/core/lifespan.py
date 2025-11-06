"""
Управление жизненным циклом приложения
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.services.background_tasks import (
    cleanup_cache_task,
    cleanup_auth_tokens_task,
    check_pending_payments_task
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    
    # Инициализация Redis
    try:
        from app.services.redis_service import redis_service
        await redis_service.get_connection()
        logger.info("Redis соединение инициализировано")
    except Exception as e:
        logger.error(f"Ошибка при инициализации Redis: {e}")
        logger.warning("Приложение будет работать без кэширования")
    
    # Инициализация RabbitMQ для отправки email
    try:
        from app.services.email_publisher import email_publisher
        await email_publisher.connect()
        logger.info("RabbitMQ соединение инициализировано")
    except Exception as e:
        logger.error(f"Ошибка при инициализации RabbitMQ: {e}")
        logger.warning("Приложение будет работать без отправки email")
    
    # Запуск фоновых задач
    cleanup_task = asyncio.create_task(cleanup_cache_task())
    cleanup_tokens_task = asyncio.create_task(cleanup_auth_tokens_task())
    check_payments_task = asyncio.create_task(check_pending_payments_task())
    
    yield
    
    # Остановка фоновых задач
    cleanup_task.cancel()
    cleanup_tokens_task.cancel()
    check_payments_task.cancel()
    
    # Ожидание завершения задач
    try:
        await cleanup_task
    except asyncio.CancelledError:
        pass
    
    try:
        await cleanup_tokens_task
    except asyncio.CancelledError:
        pass
    
    try:
        await check_payments_task
    except asyncio.CancelledError:
        pass
    
    # Закрытие Redis соединения
    try:
        from app.services.redis_service import redis_service
        await redis_service.close()
        logger.info("Redis соединение закрыто")
    except Exception as e:
        logger.error(f"Ошибка при закрытии Redis соединения: {e}")
    
    # Закрытие RabbitMQ соединения
    try:
        from app.services.email_publisher import email_publisher
        await email_publisher.disconnect()
        logger.info("RabbitMQ соединение закрыто")
    except Exception as e:
        logger.error(f"Ошибка при закрытии RabbitMQ соединения: {e}")
