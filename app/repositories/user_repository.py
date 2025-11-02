from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from typing import Optional, List
from app.models.user import User, UserRole
from app.schemas.user import UserCreate


class UserRepository:
    """Репозиторий для работы с пользователями"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        result = await self.db.execute(select(User).filter(User.id == user_id))
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email"""
        result = await self.db.execute(select(User).filter(User.email == email))
        return result.scalar_one_or_none()
    
    async def get_by_google_id(self, google_id: str) -> Optional[User]:
        """Получить пользователя по Google ID"""
        result = await self.db.execute(select(User).filter(User.google_id == google_id))
        return result.scalar_one_or_none()
    
    async def get_by_telegram_id(self, telegram_id: str) -> Optional[User]:
        """Получить пользователя по Telegram ID"""
        result = await self.db.execute(select(User).filter(User.telegram_id == telegram_id))
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Получить всех пользователей с пагинацией"""
        result = await self.db.execute(select(User).offset(skip).limit(limit))
        return list(result.scalars().all())
    
    async def get_active_users(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Получить только активных пользователей"""
        result = await self.db.execute(select(User).filter(User.is_active == True).offset(skip).limit(limit))
        return list(result.scalars().all())
    
    async def create(self, user_data: UserCreate) -> User:
        """Создать нового пользователя"""
        db_user = User(
            email=user_data.email,
            name=user_data.name,
            picture=user_data.picture,
            google_id=user_data.google_id
        )
        self.db.add(db_user)
        await self.db.commit()
        await self.db.refresh(db_user)
        
        # Очищаем кэш для этого пользователя
        try:
            from app.dependencies.auth import clear_user_cache
            await clear_user_cache(user_email=db_user.email, telegram_id=db_user.telegram_id)
        except ImportError:
            # Если импорт не удался, игнорируем
            pass
            
        return db_user
    
    async def create_or_update(self, user_data: UserCreate) -> User:
        """Создать пользователя или обновить существующего по email"""
        try:
            # Сначала проверяем по Google ID
            existing_user = await self.get_by_google_id(user_data.google_id)
            if existing_user:
                return await self.update(
                    existing_user,
                    name=user_data.name,
                    picture=user_data.picture
                )
            
            # Затем проверяем по email
            existing_user = await self.get_by_email(user_data.email)
            if existing_user:
                return await self.update(
                    existing_user,
                    google_id=user_data.google_id,
                    name=user_data.name,
                    picture=user_data.picture
                )
            
            # Если пользователь не найден, создаем нового
            return await self.create(user_data)
        except Exception as e:
            # В случае ошибки откатываем транзакцию
            await self.db.rollback()
            raise e
    
    async def create_or_update_telegram(self, user_data: UserCreate) -> User:
        """Создать пользователя или обновить существующего через Telegram"""
        try:
            # Проверяем по Telegram ID
            existing_user = await self.get_by_telegram_id(user_data.telegram_id)
            if existing_user:
                return await self.update(
                    existing_user,
                    name=user_data.name,
                    picture=user_data.picture,
                    username=user_data.username
                )
            
            # Если пользователь не найден, создаем нового
            db_user = User(
                name=user_data.name,
                picture=user_data.picture,
                telegram_id=user_data.telegram_id,
                username=user_data.username
            )
            self.db.add(db_user)
            await self.db.commit()
            await self.db.refresh(db_user)
            
            return db_user
        except Exception as e:
            # В случае ошибки откатываем транзакцию
            await self.db.rollback()
            raise e
    
    async def update(self, user: User, **kwargs) -> User:
        """Обновить данные пользователя"""
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        await self.db.commit()
        await self.db.refresh(user)
        
        # Очищаем кэш для этого пользователя
        try:
            from app.dependencies.auth import clear_user_cache
            await clear_user_cache(user_email=user.email, telegram_id=user.telegram_id)
        except ImportError:
            # Если импорт не удался, игнорируем
            pass
            
        return user
    
    async def update_by_id(self, user_id: int, **kwargs) -> Optional[User]:
        """Обновить пользователя по ID"""
        user = await self.get_by_id(user_id)
        if user:
            return await self.update(user, **kwargs)
        return None
    
    async def deactivate(self, user: User) -> User:
        """Деактивировать пользователя"""
        return await self.update(user, is_active=False)
    
    async def activate(self, user: User) -> User:
        """Активировать пользователя"""
        return await self.update(user, is_active=True)
    
    async def delete(self, user: User) -> bool:
        """Удалить пользователя"""
        try:
            await self.db.delete(user)
            await self.db.commit()
            return True
        except Exception:
            await self.db.rollback()
            return False
    
    async def delete_by_id(self, user_id: int) -> bool:
        """Удалить пользователя по ID"""
        user = await self.get_by_id(user_id)
        if user:
            return await self.delete(user)
        return False
    
    async def count(self) -> int:
        """Получить общее количество пользователей"""
        result = await self.db.execute(select(User))
        users = list(result.scalars().all())
        return len(users)
    
    async def count_active(self) -> int:
        """Получить количество активных пользователей"""
        result = await self.db.execute(select(User).filter(User.is_active == True))
        users = list(result.scalars().all())
        return len(users)
    
    async def exists_by_email(self, email: str) -> bool:
        """Проверить существование пользователя по email"""
        user = await self.get_by_email(email)
        return user is not None
    
    async def exists_by_google_id(self, google_id: str) -> bool:
        """Проверить существование пользователя по Google ID"""
        user = await self.get_by_google_id(google_id)
        return user is not None
    
    async def get_by_role(self, role: UserRole, skip: int = 0, limit: int = 100) -> List[User]:
        """Получить пользователей по роли"""
        result = await self.db.execute(
            select(User).filter(User.role == role).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_admins(self, skip: int = 0, limit: int = 100) -> List[User]:
        """Получить всех администраторов"""
        result = await self.db.execute(
            select(User).filter(
                (User.role == UserRole.ADMIN) | (User.role == UserRole.SUPER_ADMIN)
            ).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
    
    async def update_role(self, user: User, role: UserRole) -> User:
        """Обновить роль пользователя"""
        return await self.update(user, role=role)
    
    async def update_role_by_id(self, user_id: int, role: UserRole) -> Optional[User]:
        """Обновить роль пользователя по ID"""
        return await self.update_by_id(user_id, role=role)
    
    async def update_profile(self, user: User, profile_data) -> User:
        """Обновить профиль пользователя"""
        # Получаем пользователя заново из базы данных, чтобы он был attached к сессии
        db_user = await self.get_by_id(user.id)
        if not db_user:
            raise ValueError("Пользователь не найден")
            
        update_data = {}
        
        # Обновляем только переданные поля
        if profile_data.name is not None:
            update_data['name'] = profile_data.name
        if profile_data.email is not None:
            update_data['email'] = profile_data.email
        if profile_data.picture is not None:
            update_data['picture'] = profile_data.picture
            
        return await self.update(db_user, **update_data)
    
    async def is_admin(self, user: User) -> bool:
        """Проверить, является ли пользователь администратором"""
        return user.role in [UserRole.ADMIN, UserRole.SUPER_ADMIN]
    
    async def is_super_admin(self, user: User) -> bool:
        """Проверить, является ли пользователь супер-администратором"""
        return user.role == UserRole.SUPER_ADMIN
    
    async def search_users(
        self, 
        query: str = "", 
        skip: int = 0, 
        limit: int = 15,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None
    ) -> List[User]:
        """Поиск пользователей с фильтрами"""
        # Базовый запрос
        stmt = select(User)
        
        # Условия фильтрации
        conditions = []
        
        # Поиск по имени или email
        if query:
            search_condition = or_(
                User.name.ilike(f"%{query}%"),
                User.email.ilike(f"%{query}%")
            )
            conditions.append(search_condition)
        
        # Фильтр по роли
        if role is not None:
            conditions.append(User.role == role)
        
        # Фильтр по статусу активности
        if is_active is not None:
            conditions.append(User.is_active == is_active)
        
        # Применяем условия
        if conditions:
            stmt = stmt.filter(and_(*conditions))
        
        # Сортировка по дате создания (новые сначала)
        stmt = stmt.order_by(User.created_at.desc())
        
        # Пагинация
        stmt = stmt.offset(skip).limit(limit)
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def count_search_results(
        self,
        query: str = "",
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None
    ) -> int:
        """Подсчет результатов поиска для пагинации"""
        # Базовый запрос для подсчета
        stmt = select(func.count(User.id))
        
        # Условия фильтрации (те же, что и в search_users)
        conditions = []
        
        if query:
            search_condition = or_(
                User.name.ilike(f"%{query}%"),
                User.email.ilike(f"%{query}%")
            )
            conditions.append(search_condition)
        
        if role is not None:
            conditions.append(User.role == role)
        
        if is_active is not None:
            conditions.append(User.is_active == is_active)
        
        # Применяем условия
        if conditions:
            stmt = stmt.filter(and_(*conditions))
        
        result = await self.db.execute(stmt)
        return result.scalar() or 0
