#!/usr/bin/env python3
"""
Скрипт для проверки ролей пользователей в системе
"""

import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.user import UserRole
from app.config import settings

async def check_roles():
    """Показывает всех пользователей и их роли"""
    try:
        # Заменяем postgresql:// на postgresql+asyncpg:// для использования asyncpg
        database_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
        
        # Создаем async движок
        engine = create_async_engine(database_url, echo=False)
        
        # Создаем сессию
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as db:
            from app.repositories.user_repository import UserRepository
            user_repo = UserRepository(db)
            
            # Получаем всех пользователей
            all_users = await user_repo.get_all()
            
            if not all_users:
                print("📭 В системе нет пользователей")
                return
            
            print(f"👥 Всего пользователей: {len(all_users)}")
            print("=" * 60)
            
            # Группируем по ролям
            role_counts = {}
            for user in all_users:
                role = user.role.value
                if role not in role_counts:
                    role_counts[role] = []
                role_counts[role].append(user)
            
            # Показываем статистику
            print("📊 Статистика по ролям:")
            for role, users in role_counts.items():
                print(f"   {role.upper()}: {len(users)} пользователей")
            
            print("\n" + "=" * 60)
            
            # Показываем детали по ролям
            for role in [UserRole.SUPER_ADMIN, UserRole.ADMIN, UserRole.USER]:
                role_name = role.value
                if role_name in role_counts:
                    users = role_counts[role_name]
                    print(f"\n🎭 {role_name.upper()} ({len(users)} пользователей):")
                    print("-" * 40)
                    
                    for user in users:
                        status = "✅ Активен" if user.is_active else "❌ Неактивен"
                        print(f"   👤 {user.name}")
                        print(f"      📧 {user.email}")
                        print(f"      🆔 ID: {user.id}")
                        print(f"      🔑 Google ID: {user.google_id}")
                        print(f"      {status}")
                        print(f"      📅 Создан: {user.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
                        print()
            
            # Показываем администраторов отдельно
            admins = await user_repo.get_admins()
            if admins:
                print("🔐 АДМИНИСТРАТОРЫ:")
                print("=" * 40)
                for admin in admins:
                    status = "✅ Активен" if admin.is_active else "❌ Неактивен"
                    print(f"👤 {admin.name} ({admin.role.value})")
                    print(f"   📧 {admin.email}")
                    print(f"   {status}")
                    print()
            
        await engine.dispose()
        
    except Exception as e:
        print(f"❌ Ошибка при проверке ролей: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(check_roles())
