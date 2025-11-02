#!/usr/bin/env python3
"""
Быстрый скрипт для создания администратора через командную строку
Использование: python make_admin.py email@example.com "Имя Администратора" [role]
"""

import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.user import User, UserRole
from app.config import settings

async def make_admin(email: str, name: str, role: str = "ADMIN"):
    """Создает администратора с указанными данными"""
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
            
            # Валидируем роль
            try:
                user_role = UserRole(role.upper())
            except ValueError:
                print(f"❌ Неверная роль: {role}")
                print("Доступные роли: USER, ADMIN, SUPER_ADMIN")
                return False
            
            # Проверяем, существует ли пользователь
            existing_user = await user_repo.get_by_email(email)
            if existing_user:
                print(f"⚠️  Пользователь с email {email} уже существует")
                # Обновляем роль
                updated_user = await user_repo.update_role(existing_user, user_role)
                print(f"✅ Роль пользователя {email} обновлена на {user_role.value}")
                print(f"👤 Имя: {updated_user.name}")
                print(f"🎭 Роль: {updated_user.role.value}")
                return True
            
            # Создаем Google ID
            google_id = f"admin_{email.replace('@', '_').replace('.', '_')}"
            
            # Создаем нового администратора
            admin_user = User(
                email=email,
                name=name,
                google_id=google_id,
                role=user_role,
                is_active=True
            )
            
            db.add(admin_user)
            await db.commit()
            await db.refresh(admin_user)
            
            print(f"✅ Администратор успешно создан!")
            print(f"👤 Имя: {admin_user.name}")
            print(f"📧 Email: {admin_user.email}")
            print(f"🎭 Роль: {admin_user.role.value}")
            print(f"🆔 ID: {admin_user.id}")
            print(f"🔑 Google ID: {admin_user.google_id}")
            
            return True
            
        await engine.dispose()
        
    except Exception as e:
        print(f"❌ Ошибка при создании администратора: {e}")
        return False

def main():
    if len(sys.argv) < 3:
        print("Использование: python make_admin.py email@example.com \"Имя Администратора\" [role]")
        print("Пример: python make_admin.py admin@example.com \"John Admin\" SUPER_ADMIN")
        print("Доступные роли: USER, ADMIN, SUPER_ADMIN")
        sys.exit(1)
    
    email = sys.argv[1]
    name = sys.argv[2]
    role = sys.argv[3] if len(sys.argv) > 3 else "ADMIN"
    
    print(f"🔧 Создание администратора...")
    print(f"📧 Email: {email}")
    print(f"👤 Имя: {name}")
    print(f"🎭 Роль: {role}")
    print("-" * 40)
    
    success = asyncio.run(make_admin(email, name, role))
    if success:
        print("\n🎉 Готово!")
    else:
        print("\n❌ Ошибка!")
        sys.exit(1)

if __name__ == "__main__":
    main()
