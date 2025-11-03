from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from app.dependencies.auth import get_current_user
from app.dependencies.repositories import get_feedback_repository
from app.dependencies.roles import require_role
from app.models.user import User, UserRole
from app.models.feedback import FeedbackStatus, FeedbackType
from app.repositories.feedback_repository import FeedbackRepository
from app.schemas.feedback import (
    FeedbackCreate, FeedbackUpdate, FeedbackAdminUpdate,
    FeedbackResponse, FeedbackListItem, FeedbackStats, FeedbackListResponse
)
import math

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("/", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def create_feedback(
    feedback_data: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    feedback_repo: FeedbackRepository = Depends(get_feedback_repository)
):
    """Создать новый отзыв"""
    # Проверяем, есть ли уже отзыв от этого пользователя
    existing_feedback = await feedback_repo.get_user_feedback(current_user.id)
    if existing_feedback:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вы уже оставили отзыв. Вы можете отредактировать существующий отзыв."
        )
    
    return await feedback_repo.create_feedback(feedback_data, current_user.id)


@router.get("/public", response_model=FeedbackListResponse)
async def get_public_feedbacks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    feedback_repo: FeedbackRepository = Depends(get_feedback_repository)
):
    """Получить публичные отзывы (доступно без авторизации)"""
    # Показываем все отзывы для всех пользователей
    feedbacks = await feedback_repo.get_all_feedbacks(
        skip=skip, 
        limit=limit,
        status=None,
        feedback_type=None
    )
    total = await feedback_repo.count_all_feedbacks(
        status=None,
        feedback_type=None
    )
    
    return FeedbackListResponse(
        feedbacks=feedbacks,
        total=total,
        page=skip // limit + 1,
        per_page=limit,
        total_pages=math.ceil(total / limit) if total > 0 else 0
    )


@router.get("/", response_model=FeedbackListResponse)
async def get_feedbacks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status_filter: Optional[FeedbackStatus] = None,
    type_filter: Optional[FeedbackType] = None,
    current_user: User = Depends(get_current_user),
    feedback_repo: FeedbackRepository = Depends(get_feedback_repository)
):
    """Получить все отзывы (доступно для авторизованных пользователей, фильтры только для администраторов)"""
    # Обычные пользователи не могут использовать фильтры
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        status_filter = None
        type_filter = None
    
    feedbacks = await feedback_repo.get_all_feedbacks(
        skip=skip, 
        limit=limit,
        status=status_filter,
        feedback_type=type_filter
    )
    total = await feedback_repo.count_all_feedbacks(
        status=status_filter,
        feedback_type=type_filter
    )
    
    return FeedbackListResponse(
        feedbacks=feedbacks,
        total=total,
        page=skip // limit + 1,
        per_page=limit,
        total_pages=math.ceil(total / limit) if total > 0 else 0
    )


@router.get("/my", response_model=FeedbackListResponse)
async def get_my_feedbacks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    feedback_repo: FeedbackRepository = Depends(get_feedback_repository)
):
    """Получить мои отзывы"""
    feedbacks = await feedback_repo.get_user_feedbacks(current_user.id, skip, limit)
    total = await feedback_repo.count_user_feedbacks(current_user.id)
    
    return FeedbackListResponse(
        feedbacks=feedbacks,
        total=total,
        page=skip // limit + 1,
        per_page=limit,
        total_pages=math.ceil(total / limit) if total > 0 else 0
    )


@router.get("/assigned", response_model=FeedbackListResponse)
async def get_assigned_feedbacks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])),
    feedback_repo: FeedbackRepository = Depends(get_feedback_repository)
):
    """Получить отзывы, назначенные мне"""
    feedbacks = await feedback_repo.get_assigned_feedbacks(current_user.id, skip, limit)
    total = await feedback_repo.count_assigned_feedbacks(current_user.id)
    
    return FeedbackListResponse(
        feedbacks=feedbacks,
        total=total,
        page=skip // limit + 1,
        per_page=limit,
        total_pages=math.ceil(total / limit) if total > 0 else 0
    )


@router.get("/stats", response_model=FeedbackStats)
async def get_feedback_stats(
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])),
    feedback_repo: FeedbackRepository = Depends(get_feedback_repository)
):
    """Получить статистику по отзывам"""
    return await feedback_repo.get_stats()


@router.get("/{feedback_id}", response_model=FeedbackResponse)
async def get_feedback(
    feedback_id: int,
    current_user: User = Depends(get_current_user),
    feedback_repo: FeedbackRepository = Depends(get_feedback_repository)
):
    """Получить отзыв по ID (доступно для всех авторизованных пользователей)"""
    feedback = await feedback_repo.get_feedback_by_id(feedback_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отзыв не найден"
        )
    
    # Все авторизованные пользователи могут просматривать отзывы
    return feedback


@router.put("/{feedback_id}", response_model=FeedbackResponse)
async def update_feedback(
    feedback_id: int,
    feedback_data: FeedbackUpdate,
    current_user: User = Depends(get_current_user),
    feedback_repo: FeedbackRepository = Depends(get_feedback_repository)
):
    """Обновить свой отзыв"""
    feedback = await feedback_repo.get_feedback_by_id(feedback_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отзыв не найден"
        )
    
    # Проверяем, что пользователь обновляет свой отзыв
    if feedback.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы можете обновлять только свои отзывы"
        )
    
    # Нельзя обновлять отзывы со статусом RESOLVED или REJECTED
    if feedback.status in [FeedbackStatus.RESOLVED, FeedbackStatus.REJECTED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Нельзя обновлять завершенные или отклоненные отзывы"
        )
    
    updated_feedback = await feedback_repo.update_feedback(feedback_id, feedback_data)
    return updated_feedback


@router.patch("/{feedback_id}/admin", response_model=FeedbackResponse)
async def admin_update_feedback(
    feedback_id: int,
    feedback_data: FeedbackAdminUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])),
    feedback_repo: FeedbackRepository = Depends(get_feedback_repository)
):
    """Обновить отзыв администратором"""
    feedback = await feedback_repo.get_feedback_by_id(feedback_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отзыв не найден"
        )
    
    # Если назначается администратор, проверяем, что это действительно администратор
    if feedback_data.assigned_to_id is not None:
        from app.repositories import UserRepository
        from app.dependencies.repositories import get_user_repository
        
        # Получаем репозиторий пользователей
        user_repo = UserRepository(feedback_repo.db)
        assigned_user = await user_repo.get_by_id(feedback_data.assigned_to_id)
        
        if not assigned_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )
        
        if assigned_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Можно назначить только администратора"
            )
    
    updated_feedback = await feedback_repo.admin_update_feedback(feedback_id, feedback_data, current_user.id)
    return updated_feedback


@router.delete("/{feedback_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_feedback(
    feedback_id: int,
    current_user: User = Depends(get_current_user),
    feedback_repo: FeedbackRepository = Depends(get_feedback_repository)
):
    """Удалить отзыв"""
    feedback = await feedback_repo.get_feedback_by_id(feedback_id)
    if not feedback:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Отзыв не найден"
        )
    
    # Проверяем права: пользователь может удалить свой отзыв или администратор любой
    if (feedback.user_id != current_user.id and 
        current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет прав на удаление этого отзыва"
        )
    
    success = await feedback_repo.delete_feedback(feedback_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при удалении отзыва"
        )

