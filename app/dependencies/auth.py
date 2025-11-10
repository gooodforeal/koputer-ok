"""
Зависимости для аутентификации
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.auth import get_current_user_from_token
from app.models.user import User
from .repositories import get_user_repository
from app.repositories import UserRepository
from .services import get_redis_service
from app.services.redis_service import RedisService
from typing import Optional
import asyncio
from datetime import datetime, timedelta
import json

# Безопасность
security = HTTPBearer()

# TTL для кэша пользователей в секундах
_cache_ttl_seconds = 300  # 5 минут

async def clear_user_cache(user_email: str = None, telegram_id: str = None):
    """
    Очистить кэш пользователей
    
    Args:
        user_email: Email пользователя для очистки конкретного кэша.
        telegram_id: Telegram ID пользователя для очистки конкретного кэша.
                   Если оба None, очищает весь кэш.
    """
    redis_service = get_redis_service()
    if user_email:
        await redis_service.delete(f"user_cache:{user_email}")
    if telegram_id:
        await redis_service.delete(f"user_cache:telegram_{telegram_id}")
    if not user_email and not telegram_id:
        # Очищаем все ключи кэша пользователей
        keys = await redis_service.get_keys("user_cache:*")
        for key in keys:
            await redis_service.delete(key)


async def cleanup_expired_cache():
    """Очистить устаревшие записи из кэша (Redis автоматически удаляет истекшие ключи)"""
    # Redis автоматически удаляет истекшие ключи, поэтому просто возвращаем количество активных
    redis_service = get_redis_service()
    active_count = await redis_service.cleanup_expired_keys("user_cache:*")
    return active_count


# Зависимости для аутентификации
__all__ = ["get_current_user", "get_optional_user", "security", "clear_user_cache", "cleanup_expired_cache"]


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    user_repo: UserRepository = Depends(get_user_repository),
    redis_service: RedisService = Depends(get_redis_service)
) -> User:
    """
    Получает текущего пользователя из JWT токена с кэшированием
    
    Args:
        credentials: HTTP Bearer токен
        user_repo: Репозиторий пользователей
        
    Returns:
        User: Текущий пользователь
        
    Raises:
        HTTPException: Если токен недействителен или пользователь не найден
    """
    token = credentials.credentials
    payload = get_current_user_from_token(token)
    
    # Поддерживаем как email (Google OAuth), так и telegram_id (Telegram OAuth)
    user_email = payload.get("email")
    telegram_id = payload.get("telegram_id")
    
    if user_email is None and telegram_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Определяем ключ для кэша
    cache_key = f"user_cache:{user_email if user_email else f'telegram_{telegram_id}'}"
    
    # Проверяем кэш в Redis
    cached_data = await redis_service.get(cache_key)
    if cached_data:
        # Десериализуем пользователя из кэша
        try:
            # Создаем объект User с данными из кэша
            user = User()
            user.id = cached_data.get("id")
            user.email = cached_data.get("email")
            user.name = cached_data.get("name")
            user.picture = cached_data.get("picture")
            user.google_id = cached_data.get("google_id")
            user.telegram_id = cached_data.get("telegram_id")
            user.username = cached_data.get("username")
            user.is_active = cached_data.get("is_active", True)
            
            # Обрабатываем роль
            role_value = cached_data.get("role")
            if role_value:
                from app.models.user import UserRole
                user.role = UserRole(role_value)
            else:
                user.role = None
                
            # Обрабатываем даты
            if cached_data.get("created_at"):
                from datetime import datetime
                user.created_at = datetime.fromisoformat(cached_data["created_at"])
            if cached_data.get("updated_at"):
                from datetime import datetime
                user.updated_at = datetime.fromisoformat(cached_data["updated_at"])
                
            return user
        except Exception as e:
            # Если не удалось десериализовать, удаляем из кэша
            await redis_service.delete(cache_key)
    
    # Получаем пользователя из базы данных
    user = None
    if user_email:
        user = await user_repo.get_by_email(email=user_email)
    elif telegram_id:
        user = await user_repo.get_by_telegram_id(telegram_id=str(telegram_id))
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Кэшируем пользователя в Redis
    user_dict = {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "picture": user.picture,
        "google_id": user.google_id,
        "telegram_id": user.telegram_id,
        "username": user.username,  # Telegram username
        "is_active": user.is_active,
        "role": user.role.value if user.role else None,  # Преобразуем enum в строку
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None
    }
    await redis_service.set(cache_key, user_dict, ttl=_cache_ttl_seconds)
    
    return user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(HTTPBearer(auto_error=False)),
    user_repo: UserRepository = Depends(get_user_repository),
    redis_service: RedisService = Depends(get_redis_service)
) -> Optional[User]:
    """
    Получает текущего пользователя из JWT токена (опционально)
    
    Args:
        credentials: HTTP Bearer токен (опционально)
        user_repo: Репозиторий пользователей
        
    Returns:
        Optional[User]: Текущий пользователь или None если токен не предоставлен
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = get_current_user_from_token(token)
        
        # Поддерживаем как email (Google OAuth), так и telegram_id (Telegram OAuth)
        user_email = payload.get("email")
        telegram_id = payload.get("telegram_id")
        
        if user_email is None and telegram_id is None:
            return None
        
        # Определяем ключ для кэша
        cache_key = f"user_cache:{user_email if user_email else f'telegram_{telegram_id}'}"
        
        # Проверяем кэш в Redis
        cached_data = await redis_service.get(cache_key)
        if cached_data:
            try:
                # Создаем объект User с данными из кэша
                user = User()
                user.id = cached_data.get("id")
                user.email = cached_data.get("email")
                user.name = cached_data.get("name")
                user.picture = cached_data.get("picture")
                user.google_id = cached_data.get("google_id")
                user.telegram_id = cached_data.get("telegram_id")
                user.username = cached_data.get("username")
                user.is_active = cached_data.get("is_active", True)
                
                # Обрабатываем роль
                role_value = cached_data.get("role")
                if role_value:
                    from app.models.user import UserRole
                    user.role = UserRole(role_value)
                else:
                    user.role = None
                    
                # Обрабатываем даты
                if cached_data.get("created_at"):
                    user.created_at = datetime.fromisoformat(cached_data["created_at"])
                if cached_data.get("updated_at"):
                    user.updated_at = datetime.fromisoformat(cached_data["updated_at"])
                    
                return user
            except Exception:
                # Если не удалось десериализовать, удаляем из кэша
                await redis_service.delete(cache_key)
        
        # Получаем пользователя из базы данных
        user = None
        if user_email:
            user = await user_repo.get_by_email(email=user_email)
        elif telegram_id:
            user = await user_repo.get_by_telegram_id(telegram_id=str(telegram_id))
        
        if user:
            # Кэшируем пользователя в Redis
            user_dict = {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "picture": user.picture,
                "google_id": user.google_id,
                "telegram_id": user.telegram_id,
                "username": user.username,
                "is_active": user.is_active,
                "role": user.role.value if user.role else None,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None
            }
            await redis_service.set(cache_key, user_dict, ttl=_cache_ttl_seconds)
        
        return user
    except Exception:
        return None
