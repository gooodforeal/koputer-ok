#!/usr/bin/env python3
"""
Скрипт для инициализации базы данных
"""

import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine
from app.database import Base

# Импортируем все модели, чтобы они были зарегистрированы в Base.metadata
from app.config import settings


async def init_database():
    """Создает все таблицы в базе данных"""
    try:
        print(settings.database_url)
        # Заменяем postgresql:// на postgresql+asyncpg:// для использования asyncpg
        database_url = settings.database_url.replace(
            "postgresql://", "postgresql+asyncpg://"
        )

        # Создаем async движок
        engine = create_async_engine(database_url, echo=True)

        # Создаем все таблицы
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        print("✅ База данных успешно инициализирована!")
        print(f"📊 Созданы таблицы: {list(Base.metadata.tables.keys())}")

        # Создаем первого администратора
        print("\n🔧 Настройка первого администратора...")
        from setup_admin import setup_first_admin

        await setup_first_admin()

        await engine.dispose()

    except Exception as e:
        print(f"❌ Ошибка при инициализации базы данных: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(init_database())
