"""
Сервис для работы с Redis
"""
import json
import asyncio
from typing import Optional, Any, Dict
from datetime import datetime, timedelta
import redis.asyncio as redis
from app.config import settings
import logging

logger = logging.getLogger(__name__)


class RedisService:
    """Сервис для работы с Redis"""
    
    def __init__(self):
        self._redis: Optional[redis.Redis] = None
        self._connection_lock = asyncio.Lock()
    
    async def get_connection(self) -> redis.Redis:
        """Получить соединение с Redis"""
        if self._redis is None:
            async with self._connection_lock:
                if self._redis is None:
                    try:
                        # Создаем параметры подключения
                        connection_params = {
                            "host": settings.redis_host,
                            "port": settings.redis_port,
                            "db": settings.redis_db,
                            "decode_responses": True,
                            "socket_connect_timeout": 5,
                            "socket_timeout": 5,
                            "retry_on_timeout": True
                        }
                        
                        # Добавляем пароль только если он указан
                        if settings.redis_password:
                            connection_params["password"] = settings.redis_password
                        
                        self._redis = redis.Redis(**connection_params)
                        # Проверяем соединение
                        await self._redis.ping()
                        logger.info("Redis соединение установлено")
                    except Exception as e:
                        logger.error(f"Ошибка подключения к Redis: {e}")
                        raise
        return self._redis
    
    async def close(self):
        """Закрыть соединение с Redis"""
        if self._redis:
            await self._redis.close()
            self._redis = None
    
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """
        Установить значение в Redis
        
        Args:
            key: Ключ
            value: Значение (будет сериализовано в JSON)
            ttl: Время жизни в секундах
            
        Returns:
            bool: True если успешно
        """
        try:
            redis_client = await self.get_connection()
            serialized_value = json.dumps(value, default=str)
            result = await redis_client.set(key, serialized_value, ex=ttl)
            return result
        except Exception as e:
            logger.error(f"Ошибка при записи в Redis: {e}")
            return False
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Получить значение из Redis
        
        Args:
            key: Ключ
            
        Returns:
            Значение или None если не найдено
        """
        try:
            redis_client = await self.get_connection()
            value = await redis_client.get(key)
            if value is None:
                return None
            return json.loads(value)
        except Exception as e:
            logger.error(f"Ошибка при чтении из Redis: {e}")
            return None
    
    async def delete(self, key: str) -> bool:
        """
        Удалить ключ из Redis
        
        Args:
            key: Ключ
            
        Returns:
            bool: True если ключ был удален
        """
        try:
            redis_client = await self.get_connection()
            result = await redis_client.delete(key)
            return result > 0
        except Exception as e:
            logger.error(f"Ошибка при удалении из Redis: {e}")
            return False
    
    async def exists(self, key: str) -> bool:
        """
        Проверить существование ключа в Redis
        
        Args:
            key: Ключ
            
        Returns:
            bool: True если ключ существует
        """
        try:
            redis_client = await self.get_connection()
            result = await redis_client.exists(key)
            return result > 0
        except Exception as e:
            logger.error(f"Ошибка при проверке существования ключа в Redis: {e}")
            return False
    
    async def set_hash(self, key: str, mapping: Dict[str, Any], ttl: Optional[int] = None) -> bool:
        """
        Установить хеш в Redis
        
        Args:
            key: Ключ хеша
            mapping: Словарь для хеша
            ttl: Время жизни в секундах
            
        Returns:
            bool: True если успешно
        """
        try:
            redis_client = await self.get_connection()
            # Сериализуем значения в хеше
            serialized_mapping = {
                k: json.dumps(v, default=str) for k, v in mapping.items()
            }
            result = await redis_client.hset(key, mapping=serialized_mapping)
            if ttl:
                await redis_client.expire(key, ttl)
            return result >= 0
        except Exception as e:
            logger.error(f"Ошибка при записи хеша в Redis: {e}")
            return False
    
    async def get_hash(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Получить хеш из Redis
        
        Args:
            key: Ключ хеша
            
        Returns:
            Словарь или None если не найден
        """
        try:
            redis_client = await self.get_connection()
            hash_data = await redis_client.hgetall(key)
            if not hash_data:
                return None
            
            # Десериализуем значения
            result = {}
            for k, v in hash_data.items():
                try:
                    result[k] = json.loads(v)
                except (json.JSONDecodeError, TypeError):
                    result[k] = v
            return result
        except Exception as e:
            logger.error(f"Ошибка при чтении хеша из Redis: {e}")
            return None
    
    async def delete_hash_field(self, key: str, field: str) -> bool:
        """
        Удалить поле из хеша в Redis
        
        Args:
            key: Ключ хеша
            field: Поле для удаления
            
        Returns:
            bool: True если поле было удалено
        """
        try:
            redis_client = await self.get_connection()
            result = await redis_client.hdel(key, field)
            return result > 0
        except Exception as e:
            logger.error(f"Ошибка при удалении поля из хеша в Redis: {e}")
            return False
    
    async def get_keys(self, pattern: str = "*") -> list[str]:
        """
        Получить список ключей по паттерну
        
        Args:
            pattern: Паттерн для поиска ключей
            
        Returns:
            Список ключей
        """
        try:
            redis_client = await self.get_connection()
            keys = await redis_client.keys(pattern)
            return keys
        except Exception as e:
            logger.error(f"Ошибка при получении ключей из Redis: {e}")
            return []
    
    async def cleanup_expired_keys(self, pattern: str = "*") -> int:
        """
        Очистить истекшие ключи (Redis автоматически удаляет истекшие ключи)
        Этот метод возвращает количество активных ключей
        
        Args:
            pattern: Паттерн для поиска ключей
            
        Returns:
            Количество активных ключей
        """
        try:
            redis_client = await self.get_connection()
            keys = await redis_client.keys(pattern)
            active_count = 0
            for key in keys:
                if await redis_client.exists(key):
                    active_count += 1
            return active_count
        except Exception as e:
            logger.error(f"Ошибка при очистке ключей в Redis: {e}")
            return 0


# Глобальный экземпляр сервиса Redis
redis_service = RedisService()
