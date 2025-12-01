#!/usr/bin/env python3
"""
Скрипт для автоматической настройки первого администратора
Используется при первом запуске системы
"""

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.user import User, UserRole
from app.config import settings


async def setup_first_admin():
    """Автоматически создает первого администратора если его нет"""
    try:
        # Заменяем postgresql:// на postgresql+asyncpg:// для использования asyncpg
        database_url = settings.database_url.replace(
            "postgresql://", "postgresql+asyncpg://"
        )

        # Создаем async движок
        engine = create_async_engine(database_url, echo=False)

        # Создаем сессию
        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )

        async with async_session() as db:
            from app.repositories.user_repository import UserRepository

            user_repo = UserRepository(db)

            # Проверяем, есть ли уже администраторы
            admins = await user_repo.get_admins()
            if admins:
                print(f"✅ В системе уже есть {len(admins)} администратор(ов)")
                for admin in admins:
                    print(f"   - {admin.email} ({admin.role.value})")
                return

            # Получаем данные из настроек или используем значения по умолчанию
            admin_email = settings.first_admin_email or "admin@example.com"
            admin_name = settings.first_admin_name or "System Administrator"
            admin_google_id = (
                settings.first_admin_google_id
                or f"admin_{admin_email.replace('@', '_').replace('.', '_')}"
            )
            admin_role = (settings.first_admin_role or "SUPER_ADMIN").upper()

            # Валидируем роль
            try:
                role = UserRole(admin_role.upper())
            except ValueError:
                print(f"⚠️  Неверная роль {admin_role}, используется SUPER_ADMIN")
                role = UserRole.SUPER_ADMIN

            # Проверяем, существует ли пользователь с таким email
            existing_user = await user_repo.get_by_email(admin_email)
            if existing_user:
                print(f"⚠️  Пользователь с email {admin_email} уже существует")
                # Обновляем роль существующего пользователя
                updated_user = await user_repo.update_role(existing_user, role)
                print(f"✅ Роль пользователя {admin_email} обновлена на {role.value}")
                return

            # Создаем первого администратора
            admin_user = User(
                email=admin_email,
                name=admin_name,
                google_id=admin_google_id,
                role=role,
                is_active=True,
            )

            db.add(admin_user)
            await db.commit()
            await db.refresh(admin_user)

            print("🎉 Первый администратор успешно создан!")
            print(f"👤 Имя: {admin_user.name}")
            print(f"📧 Email: {admin_user.email}")
            print(f"🎭 Роль: {admin_user.role.value}")
            print(f"🆔 ID: {admin_user.id}")
            print(f"🔑 Google ID: {admin_user.google_id}")
            print("\n💡 Для входа в систему используйте этот Google ID в OAuth")

        await engine.dispose()

    except Exception as e:
        print(f"❌ Ошибка при создании первого администратора: {e}")
        # Не завершаем выполнение с ошибкой, так как это может быть частью инициализации
        print("⚠️  Продолжаем выполнение без создания администратора")


if __name__ == "__main__":
    asyncio.run(setup_first_admin())
