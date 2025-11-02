"""
Сервис для фоновых задач приложения
"""
import asyncio
import logging

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
            print(f"Активных токенов авторизации: {active_count}")
        except Exception as e:
            print(f"Ошибка при очистке токенов: {e}")
        await asyncio.sleep(60)  # Очищаем каждую минуту
