#!/usr/bin/env python3
"""
Скрипт для создания первого администратора в системе
"""

import asyncio
import sys
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.user import User, UserRole
from app.config import settings


async def create_first_admin():
    """Создает первого администратора в системе"""
    try:
        # Заменяем postgresql:// на postgresql+asyncpg:// для использования asyncpg
        database_url = settings.database_url.replace(
            "postgresql://", "postgresql+asyncpg://"
        )

        # Создаем async движок
        engine = create_async_engine(database_url, echo=True)

        # Создаем сессию
        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )

        async with async_session() as db:
            # Проверяем, есть ли уже администраторы
            from app.repositories.user_repository import UserRepository

            user_repo = UserRepository(db)

            admins = await user_repo.get_admins()
            if admins:
                print("⚠️  В системе уже есть администраторы:")
                for admin in admins:
                    print(f"   - {admin.email} ({admin.role.value})")
                print("\n❓ Хотите создать еще одного администратора? (y/n): ", end="")
                response = input().lower().strip()
                if response != "y":
                    print("❌ Создание администратора отменено")
                    return

            # Запрашиваем данные для администратора
            print("\n🔧 Создание нового администратора")
            print("=" * 40)

            email = input("📧 Email администратора: ").strip()
            if not email:
                print("❌ Email не может быть пустым")
                return

            name = input("👤 Имя администратора: ").strip()
            if not name:
                print("❌ Имя не может быть пустым")
                return

            google_id = input(
                "🔑 Google ID (или оставьте пустым для тестового): "
            ).strip()
            if not google_id:
                google_id = f"admin_{email.replace('@', '_').replace('.', '_')}"
                print(f"🔑 Используется тестовый Google ID: {google_id}")

            # Выбираем роль
            print("\n🎭 Выберите роль:")
            print("1. ADMIN - обычный администратор")
            print("2. SUPER_ADMIN - супер-администратор")
            role_choice = input("Введите номер (1-2): ").strip()

            if role_choice == "1":
                role = UserRole.ADMIN
            elif role_choice == "2":
                role = UserRole.SUPER_ADMIN
            else:
                print("❌ Неверный выбор, устанавливается роль ADMIN")
                role = UserRole.ADMIN

            # Проверяем, существует ли пользователь с таким email
            existing_user = await user_repo.get_by_email(email)
            if existing_user:
                print(f"\n⚠️  Пользователь с email {email} уже существует")
                print("❓ Обновить роль существующего пользователя? (y/n): ", end="")
                response = input().lower().strip()
                if response == "y":
                    updated_user = await user_repo.update_role(existing_user, role)
                    print(f"✅ Роль пользователя {email} обновлена на {role.value}")
                    print(f"👤 Пользователь: {updated_user.name}")
                    print(f"🎭 Роль: {updated_user.role.value}")
                    print(f"📧 Email: {updated_user.email}")
                else:
                    print("❌ Обновление отменено")
                return

            # Создаем нового администратора
            admin_user = User(
                email=email, name=name, google_id=google_id, role=role, is_active=True
            )

            db.add(admin_user)
            await db.commit()
            await db.refresh(admin_user)

            print("\n✅ Администратор успешно создан!")
            print(f"👤 Имя: {admin_user.name}")
            print(f"📧 Email: {admin_user.email}")
            print(f"🎭 Роль: {admin_user.role.value}")
            print(f"🆔 ID: {admin_user.id}")
            print(f"🔑 Google ID: {admin_user.google_id}")
            print(f"✅ Активен: {admin_user.is_active}")
            print(f"📅 Создан: {admin_user.created_at}")

        await engine.dispose()

    except Exception as e:
        print(f"❌ Ошибка при создании администратора: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(create_first_admin())
