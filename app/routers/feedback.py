from fastapi import APIRouter, Depends, Query, status
from typing import Optional
from app.dependencies.auth import get_current_user
from app.dependencies.repositories import get_feedback_service, get_user_repository
from app.dependencies.roles import require_role
from app.models.user import User, UserRole
from app.models.feedback import FeedbackStatus, FeedbackType
from app.services.feedback_service import FeedbackService
from app.repositories import UserRepository
from app.schemas.feedback import (
    FeedbackCreate, FeedbackUpdate, FeedbackAdminUpdate,
    FeedbackResponse, FeedbackStats, FeedbackListResponse
)

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("/", response_model=FeedbackResponse, status_code=201)
async def create_feedback(
    feedback_data: FeedbackCreate,
    current_user: User = Depends(get_current_user),
    feedback_service: FeedbackService = Depends(get_feedback_service)
):
    """Создать новый отзыв"""
    return await feedback_service.create_feedback(feedback_data, current_user)


@router.get("/public", response_model=FeedbackListResponse)
async def get_public_feedbacks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    feedback_service: FeedbackService = Depends(get_feedback_service)
):
    """Получить публичные отзывы (доступно без авторизации)"""
    return await feedback_service.get_public_feedbacks(skip, limit)


@router.get("/", response_model=FeedbackListResponse)
async def get_feedbacks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    status_filter: Optional[FeedbackStatus] = None,
    type_filter: Optional[FeedbackType] = None,
    current_user: User = Depends(get_current_user),
    feedback_service: FeedbackService = Depends(get_feedback_service)
):
    """Получить все отзывы (доступно для авторизованных пользователей, фильтры только для администраторов)"""
    return await feedback_service.get_feedbacks(
        skip=skip,
        limit=limit,
        status_filter=status_filter,
        type_filter=type_filter,
        current_user=current_user
    )


@router.get("/my", response_model=FeedbackListResponse)
async def get_my_feedbacks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    feedback_service: FeedbackService = Depends(get_feedback_service)
):
    """Получить мои отзывы"""
    return await feedback_service.get_user_feedbacks(current_user, skip, limit)


@router.get("/assigned", response_model=FeedbackListResponse)
async def get_assigned_feedbacks(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])),
    feedback_service: FeedbackService = Depends(get_feedback_service)
):
    """Получить отзывы, назначенные мне"""
    return await feedback_service.get_assigned_feedbacks(current_user, skip, limit)


@router.get("/stats", response_model=FeedbackStats)
async def get_feedback_stats(
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])),
    feedback_service: FeedbackService = Depends(get_feedback_service)
):
    """Получить статистику по отзывам"""
    return await feedback_service.get_feedback_stats(current_user)


@router.get("/{feedback_id}", response_model=FeedbackResponse)
async def get_feedback(
    feedback_id: int,
    feedback_service: FeedbackService = Depends(get_feedback_service)
):
    """Получить отзыв по ID (доступно для всех авторизованных пользователей)"""
    return await feedback_service.get_feedback(feedback_id)


@router.put("/{feedback_id}", response_model=FeedbackResponse)
async def update_feedback(
    feedback_id: int,
    feedback_data: FeedbackUpdate,
    current_user: User = Depends(get_current_user),
    feedback_service: FeedbackService = Depends(get_feedback_service)
):
    """Обновить свой отзыв"""
    return await feedback_service.update_feedback(feedback_id, feedback_data, current_user)


@router.patch("/{feedback_id}/admin", response_model=FeedbackResponse)
async def admin_update_feedback(
    feedback_id: int,
    feedback_data: FeedbackAdminUpdate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])),
    feedback_service: FeedbackService = Depends(get_feedback_service),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Обновить отзыв администратором"""
    return await feedback_service.admin_update_feedback(
        feedback_id, feedback_data, current_user, user_repo
    )


@router.delete("/{feedback_id}", status_code=204)
async def delete_feedback(
    feedback_id: int,
    current_user: User = Depends(get_current_user),
    feedback_service: FeedbackService = Depends(get_feedback_service)
):
    """Удалить отзыв"""
    await feedback_service.delete_feedback(feedback_id, current_user)
