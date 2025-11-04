"""
Сервис для работы с пользователями
"""
from typing import List, Optional
from fastapi import HTTPException, status
from app.repositories import UserRepository
from app.models.user import User, UserRole
from app.schemas.user import UserResponse, UserStats, UserUpdate, UserSearchResponse

class UserService:
    """Сервис для работы с пользователями"""
    
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    async def get_user_profile(self, current_user: User) -> UserResponse:
        """
        Получить профиль пользователя
        
        Args:
            current_user: Текущий пользователь
            
        Returns:
            UserResponse с данными пользователя
        """
        return current_user
    
    async def get_users(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> List[UserResponse]:
        """
        Получить список всех пользователей (только для супер-администраторов)
        
        Args:
            skip: Количество записей для пропуска
            limit: Максимальное количество записей
            
        Returns:
            Список пользователей
        """
        return await self.user_repo.get_all(skip=skip, limit=limit)
    
    async def search_users(
        self,
        q: str = "",
        page: int = 1,
        per_page: int = 15,
        role: Optional[UserRole] = None,
        is_active: Optional[bool] = None
    ) -> UserSearchResponse:
        """
        Поиск пользователей с пагинацией (только для супер-администраторов)
        
        Args:
            q: Поисковый запрос
            page: Номер страницы
            per_page: Количество записей на странице
            role: Фильтр по роли
            is_active: Фильтр по статусу активности
            
        Returns:
            UserSearchResponse со списком пользователей
        """
        skip = (page - 1) * per_page
        
        # Получаем пользователей с поиском и фильтрами
        users = await self.user_repo.search_users(
            query=q,
            skip=skip,
            limit=per_page,
            role=role,
            is_active=is_active
        )
        
        # Получаем общее количество для пагинации
        total = await self.user_repo.count_search_results(
            query=q,
            role=role,
            is_active=is_active
        )
        
        total_pages = (total + per_page - 1) // per_page
        
        return UserSearchResponse(
            users=users,
            total=total,
            page=page,
            per_page=per_page,
            total_pages=total_pages
        )
    
    async def get_user_stats(self) -> UserStats:
        """
        Получить статистику пользователей
        
        Returns:
            UserStats со статистикой
        """
        total = await self.user_repo.count()
        active = await self.user_repo.count_active()
        return UserStats(
            total_users=total,
            active_users=active,
            inactive_users=total - active
        )
    
    async def update_user_profile(
        self,
        profile_update: UserUpdate,
        current_user: User
    ) -> UserResponse:
        """
        Обновить профиль текущего пользователя
        
        Args:
            profile_update: Данные для обновления профиля
            current_user: Текущий пользователь
            
        Returns:
            UserResponse с обновленными данными пользователя
        """
        updated_user = await self.user_repo.update_profile(current_user, profile_update)
        return updated_user
    
    async def update_user_role(
        self,
        user_id: int,
        role_update: UserUpdate
    ) -> UserResponse:
        """
        Обновить роль пользователя (только для супер-администраторов)
        
        Args:
            user_id: ID пользователя
            role_update: Данные для обновления роли
            
        Returns:
            UserResponse с обновленными данными пользователя
        """
        # Получаем пользователя для обновления
        target_user = await self.user_repo.get_by_id(user_id)
        if not target_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        # Проверяем, что нельзя назначить супер-администратора
        if role_update.role == UserRole.SUPER_ADMIN:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя назначать роль супер-администратора"
            )
        
        # Обновляем роль пользователя
        updated_user = await self.user_repo.update_role(target_user, role_update.role)
        return updated_user

