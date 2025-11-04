from fastapi import APIRouter, Depends, Query, HTTPException, status
from typing import Optional
from app.dependencies import get_current_user, require_super_admin
from app.dependencies.repositories import get_user_service
from app.services.user_service import UserService
from app.schemas.user import UserResponse, UserStats, UserUpdate, UserSearchResponse
from app.models.user import User, UserRole

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/profile", response_model=UserResponse)
async def get_user_profile(
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """Получение профиля пользователя"""
    return await user_service.get_user_profile(current_user)


@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    """Пример защищенного маршрута"""
    return {
        "message": f"Hello {current_user.name}!",
        "user_id": current_user.id,
        "email": current_user.email
    }


@router.get("/", response_model=list[UserResponse])
async def get_users(
    skip: int = Query(0, ge=0, description="Количество записей для пропуска"),
    limit: int = Query(100, ge=1, le=1000, description="Максимальное количество записей"),
    current_user: User = Depends(require_super_admin),
    user_service: UserService = Depends(get_user_service)
):
    """Получить список всех пользователей (только для супер-администраторов)"""
    return await user_service.get_users(skip=skip, limit=limit)


@router.get("/search", response_model=UserSearchResponse)
async def search_users(
    q: str = Query("", description="Поисковый запрос"),
    page: int = Query(1, ge=1, description="Номер страницы"),
    per_page: int = Query(15, ge=1, le=100, description="Количество записей на странице"),
    role: Optional[UserRole] = Query(None, description="Фильтр по роли"),
    is_active: Optional[bool] = Query(None, description="Фильтр по статусу активности"),
    current_user: User = Depends(require_super_admin),
    user_service: UserService = Depends(get_user_service)
):
    """Поиск пользователей с пагинацией (только для супер-администраторов)"""
    return await user_service.search_users(
        q=q,
        page=page,
        per_page=per_page,
        role=role,
        is_active=is_active
    )


@router.get("/stats", response_model=UserStats)
async def get_user_stats(
    user_service: UserService = Depends(get_user_service)
):
    """Получить статистику пользователей"""
    return await user_service.get_user_stats()


@router.put("/profile", response_model=UserResponse)
async def update_user_profile(
    profile_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service)
):
    """Обновить профиль текущего пользователя"""
    return await user_service.update_user_profile(profile_update, current_user)


@router.put("/{user_id}/role", response_model=UserResponse)
async def update_user_role(
    user_id: int,
    role_update: UserUpdate,
    current_user: User = Depends(require_super_admin),
    user_service: UserService = Depends(get_user_service)
):
    """Обновить роль пользователя (только для супер-администраторов)"""
    return await user_service.update_user_role(user_id, role_update)
