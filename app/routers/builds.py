from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse
from typing import List, Optional
from app.dependencies.auth import get_current_user, get_optional_user
from app.dependencies.repositories import get_build_service
from app.models.user import User
from app.services.build_service import BuildService
from app.schemas.build import (
    BuildCreate, BuildUpdate, BuildResponse, BuildListResponse, BuildTopResponse,
    BuildRatingCreate, BuildRatingUpdate, BuildRatingResponse,
    BuildCommentCreate, BuildCommentUpdate, BuildCommentResponse, BuildCommentListResponse,
    BuildCommentSingleResponse, BuildStatsResponse, BuildComponentsResponse
)
from app.schemas.common import MessageResponse

router = APIRouter(prefix="/builds", tags=["builds"])


# ==================== Endpoints для сборок ====================

@router.post("/", response_model=BuildResponse, status_code=201)
async def create_build(
    build_data: BuildCreate,
    current_user: User = Depends(get_current_user),
    build_service: BuildService = Depends(get_build_service)
):
    """Создать новую сборку"""
    return await build_service.create_build(build_data, current_user.id)


@router.get("/", response_model=BuildListResponse)
async def get_builds(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    query: str = Query("", description="Поиск по названию или описанию"),
    author_id: Optional[int] = Query(None, description="Фильтр по автору"),
    sort_by: str = Query("created_at", description="Поле для сортировки (created_at, views_count, average_rating, title)"),
    order: str = Query("desc", description="Порядок сортировки (asc, desc)"),
    build_service: BuildService = Depends(get_build_service)
):
    """Получить список сборок с фильтрами, сортировкой и пагинацией"""
    return await build_service.get_builds(
        skip=skip,
        limit=limit,
        query=query,
        author_id=author_id,
        sort_by=sort_by,
        order=order
    )


@router.get("/top", response_model=BuildTopResponse)
async def get_top_builds(
    limit: int = Query(10, ge=1, le=50, description="Количество сборок в топе"),
    build_service: BuildService = Depends(get_build_service)
):
    """Получить топ сборок по рейтингу"""
    return await build_service.get_top_builds(limit=limit)


@router.get("/my", response_model=BuildListResponse)
async def get_my_builds(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    build_service: BuildService = Depends(get_build_service)
):
    """Получить мои сборки"""
    return await build_service.get_user_builds(
        author_id=current_user.id,
        skip=skip,
        limit=limit
    )


@router.get("/stats", response_model=BuildStatsResponse)
async def get_builds_stats(
    build_service: BuildService = Depends(get_build_service)
):
    """Получить статистику по сборкам"""
    return await build_service.get_builds_stats()


@router.get("/components/unique", response_model=BuildComponentsResponse)
async def get_unique_components(
    build_service: BuildService = Depends(get_build_service)
):
    """Получить список доступных компонентов, сгруппированных по категориям"""
    return await build_service.get_unique_components()


@router.get("/{build_id}", response_model=BuildResponse)
async def get_build(
    build_id: int,
    request: Request,
    current_user: Optional[User] = Depends(get_optional_user),
    build_service: BuildService = Depends(get_build_service)
):
    """Получить сборку по ID"""
    return await build_service.get_build(build_id, request, current_user)


@router.put("/{build_id}", response_model=BuildResponse)
async def update_build(
    build_id: int,
    build_data: BuildUpdate,
    current_user: User = Depends(get_current_user),
    build_service: BuildService = Depends(get_build_service)
):
    """Обновить сборку"""
    return await build_service.update_build(build_id, build_data, current_user)


@router.delete("/{build_id}", response_model=MessageResponse)
async def delete_build(
    build_id: int,
    current_user: User = Depends(get_current_user),
    build_service: BuildService = Depends(get_build_service)
):
    """Удалить сборку"""
    return await build_service.delete_build(build_id, current_user)


# ==================== Endpoints для оценок ====================

@router.post("/{build_id}/ratings", response_model=BuildRatingResponse, status_code=201)
async def create_rating(
    build_id: int,
    rating_data: BuildRatingCreate,
    current_user: User = Depends(get_current_user),
    build_service: BuildService = Depends(get_build_service)
):
    """Поставить оценку сборке"""
    return await build_service.create_rating(build_id, rating_data, current_user)


@router.put("/{build_id}/ratings", response_model=BuildRatingResponse)
async def update_rating(
    build_id: int,
    rating_data: BuildRatingUpdate,
    current_user: User = Depends(get_current_user),
    build_service: BuildService = Depends(get_build_service)
):
    """Обновить оценку сборки"""
    return await build_service.update_rating(build_id, rating_data, current_user)


@router.delete("/{build_id}/ratings", response_model=MessageResponse)
async def delete_rating(
    build_id: int,
    current_user: User = Depends(get_current_user),
    build_service: BuildService = Depends(get_build_service)
):
    """Удалить оценку сборки"""
    return await build_service.delete_rating(build_id, current_user)


@router.get("/{build_id}/ratings/my", response_model=BuildRatingResponse)
async def get_my_rating(
    build_id: int,
    current_user: User = Depends(get_current_user),
    build_service: BuildService = Depends(get_build_service)
):
    """Получить мою оценку для сборки"""
    return await build_service.get_user_rating(build_id, current_user)


# ==================== Endpoints для комментариев ====================

@router.post("/{build_id}/comments", response_model=BuildCommentSingleResponse, status_code=201)
async def create_comment(
    build_id: int,
    comment_data: BuildCommentCreate,
    current_user: User = Depends(get_current_user),
    build_service: BuildService = Depends(get_build_service)
):
    """Создать комментарий к сборке"""
    return await build_service.create_comment(build_id, comment_data, current_user)


@router.get("/{build_id}/comments", response_model=BuildCommentListResponse)
async def get_comments(
    build_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    build_service: BuildService = Depends(get_build_service)
):
    """Получить комментарии к сборке"""
    return await build_service.get_comments(build_id, skip, limit)


@router.put("/{build_id}/comments/{comment_id}", response_model=BuildCommentSingleResponse)
async def update_comment(
    build_id: int,
    comment_id: int,
    comment_data: BuildCommentUpdate,
    current_user: User = Depends(get_current_user),
    build_service: BuildService = Depends(get_build_service)
):
    """Обновить комментарий"""
    return await build_service.update_comment(build_id, comment_id, comment_data, current_user)


@router.delete("/{build_id}/comments/{comment_id}", response_model=MessageResponse)
async def delete_comment(
    build_id: int,
    comment_id: int,
    current_user: User = Depends(get_current_user),
    build_service: BuildService = Depends(get_build_service)
):
    """Удалить комментарий"""
    return await build_service.delete_comment(build_id, comment_id, current_user)


# ==================== Endpoint для экспорта PDF ====================

@router.get("/{build_id}/export/pdf")
async def export_build_pdf(
    build_id: int,
    build_service: BuildService = Depends(get_build_service)
):
    """Экспортировать сборку в PDF"""
    return await build_service.export_build_pdf(build_id)


