from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import List, Optional
from app.dependencies import (
    get_current_user, 
    get_user_repository, 
    require_super_admin,
    require_admin,
    require_admin_or_super_admin,
    require_role,
    require_any_role
)
from app.repositories import UserRepository
from app.schemas.user import UserResponse, UserStats, UserUpdate, UserSearchResponse
from app.models.user import User, UserRole

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/profile", response_model=UserResponse)
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """Получение профиля пользователя"""
    return current_user


@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    """Пример защищенного маршрута"""
    return {
        "message": f"Hello {current_user.name}!",
        "user_id": current_user.id,
        "email": current_user.email
    }


@router.get("/", response_model=List[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
    limit: int = Query(100, ge=1, le=1000, description="Максимальное количество записей"),
    current_user: User = Depends(require_super_admin),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Получить список всех пользователей (только для супер-администраторов)"""
    return await user_repo.get_all(skip=skip, limit=limit)


@router.get("/search", response_model=UserSearchResponse)
async def search_users(
    q: str = Query("", description="Поисковый запрос"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(15, ge=1, le=100, description="Количество записей на странице"),
    role: Optional[UserRole] = Query(None, description="Фильтр по роли"),
    is_active: Optional[bool] = Query(None, description="Фильтр по статусу активности"),
    current_user: User = Depends(require_super_admin),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Поиск пользователей с пагинацией (только для супер-администраторов)"""
    skip = (page - 1) * per_page
    
    # Получаем пользователей с поиском и фильтрами
    users = await user_repo.search_users(
        query=q,
        skip=skip,
        limit=per_page,
        role=role,
        is_active=is_active
    )
    
    # Получаем общее количество для пагинации
    total = await user_repo.count_search_results(
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


@router.get("/stats", response_model=UserStats)
async def get_user_stats(user_repo: UserRepository = Depends(get_user_repository)):
    """Получить статистику пользователей"""
    total = await user_repo.count()
    active = await user_repo.count_active()
    return UserStats(
        total_users=total,
        active_users=active,
        inactive_users=total - active
    )


@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    profile_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Обновить профиль текущего пользователя"""

    updated_user = await user_repo.update_profile(current_user, profile_update)
    return updated_user


@router.put("/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: int,
    role_update: UserUpdate,
    current_user: User = Depends(require_super_admin),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Обновить роль пользователя (только для супер-администраторов)"""
    # Получаем пользователя для обновления
    target_user = await user_repo.get_by_id(user_id)
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
    updated_user = await user_repo.update_role(target_user, role_update.role)
    return updated_user
