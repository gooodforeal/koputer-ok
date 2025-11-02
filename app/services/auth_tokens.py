"""
Сервис для управления временными токенами авторизации через Telegram
"""
import secrets
from datetime import datetime, timedelta
from typing import Optional, Dict
import asyncio
from app.services.redis_service import redis_service


class AuthTokenStorage:
    """Хранилище временных токенов авторизации"""
    
    def __init__(self):
        self._lock = asyncio.Lock()
        
    async def create_token(self, expires_in: int = 300) -> str:
        """
        Создает временный токен авторизации
        
        Args:
            expires_in: Время жизни токена в секундах (по умолчанию 5 минут)
            
        Returns:
            str: Уникальный токен
        """
        async with self._lock:
            token = secrets.token_urlsafe(32)
            token_data = {
                "created_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(seconds=expires_in)).isoformat(),
                "telegram_id": None,
                "used": False
            }
            cache_key = f"auth_token:{token}"
            await redis_service.set(cache_key, token_data, ttl=expires_in)
            return token
    
    async def link_telegram_user(self, token: str, telegram_id: int, 
                                 username: Optional[str], 
                                 first_name: str, 
                                 last_name: Optional[str],
                                 photo_url: Optional[str] = None) -> bool:
        """
        Связывает токен с пользователем Telegram
        
        Returns:
            bool: True если успешно, False если токен не найден или истек
        """
        async with self._lock:
            cache_key = f"auth_token:{token}"
            token_data = await redis_service.get(cache_key)
            
            if not token_data:
                return False
                
            # Проверяем срок действия
            expires_at = datetime.fromisoformat(token_data["expires_at"])
            if datetime.now() > expires_at:
                await redis_service.delete(cache_key)
                return False
            
            # Проверяем, не использован ли уже
            if token_data["used"]:
                return False
            
            # Обновляем данные токена
            token_data["telegram_id"] = telegram_id
            token_data["username"] = username
            token_data["first_name"] = first_name
            token_data["last_name"] = last_name
            token_data["photo_url"] = photo_url
            token_data["used"] = True
            
            # Сохраняем обновленные данные
            await redis_service.set(cache_key, token_data)
            
            return True
    
    async def get_token_data(self, token: str) -> Optional[Dict]:
        """
        Получает данные по токену
        
        Returns:
            Optional[Dict]: Данные токена или None если не найден/истек
        """
        async with self._lock:
            cache_key = f"auth_token:{token}"
            token_data = await redis_service.get(cache_key)
            
            if not token_data:
                return None
            
            # Проверяем срок действия
            expires_at = datetime.fromisoformat(token_data["expires_at"])
            if datetime.now() > expires_at:
                await redis_service.delete(cache_key)
                return None
            
            return token_data.copy()
    
    async def update_token_data(self, token: str, **kwargs) -> bool:
        """
        Обновляет данные токена
        
        Returns:
            bool: True если успешно, False если токен не найден
        """
        async with self._lock:
            cache_key = f"auth_token:{token}"
            token_data = await redis_service.get(cache_key)
            
            if not token_data:
                return False
            
            # Обновляем данные
            for key, value in kwargs.items():
                token_data[key] = value
            
            # Сохраняем обновленные данные
            await redis_service.set(cache_key, token_data)
            
            return True
    
    async def invalidate_token(self, token: str) -> bool:
        """
        Удаляет токен из хранилища
        
        Returns:
            bool: True если токен был удален, False если не найден
        """
        async with self._lock:
            cache_key = f"auth_token:{token}"
            return await redis_service.delete(cache_key)
    
    async def cleanup_expired_tokens(self):
        """Удаляет истекшие токены из хранилища (Redis автоматически удаляет истекшие ключи)"""
        # Redis автоматически удаляет истекшие ключи, поэтому просто возвращаем количество активных
        active_count = await redis_service.cleanup_expired_keys("auth_token:*")
        return active_count


# Глобальный экземпляр хранилища
auth_token_storage = AuthTokenStorage()

