from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import StreamingResponse
from typing import List, Optional
import io
import urllib.parse
from app.dependencies.auth import get_current_user, get_optional_user
from app.dependencies.repositories import get_build_repository
from app.models.user import User
from app.repositories.build_repository import BuildRepository
from app.schemas.build import (
    BuildCreate, BuildUpdate, BuildResponse, BuildListResponse, BuildTopResponse,
    BuildRatingCreate, BuildRatingUpdate, BuildRatingResponse,
    BuildCommentCreate, BuildCommentUpdate, BuildCommentResponse, BuildCommentListResponse,
    BuildCommentSingleResponse, BuildStatsResponse, BuildComponentsResponse
)
from app.schemas.common import MessageResponse
from app.services.redis_service import redis_service
from app.services.pdf_generator import create_build_pdf
from app.utils.transliteration import safe_filename
import math
import logging

logger = logging.getLogger(__name__)    

router = APIRouter(prefix="/builds", tags=["builds"])


# ==================== Endpoints для сборок ====================

@router.post("/", response_model=BuildResponse, status_code=status.HTTP_201_CREATED)
async def create_build(
    build_data: BuildCreate,
    current_user: User = Depends(get_current_user),
    build_repo: BuildRepository = Depends(get_build_repository)
):
    """Создать новую сборку"""
    return await build_repo.create(build_data, current_user.id)


@router.get("/", response_model=BuildListResponse)
async def get_builds(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    query: str = Query("", description="Поиск по названию или описанию"),
    author_id: Optional[int] = Query(None, description="Фильтр по автору"),
    sort_by: str = Query("created_at", description="Поле для сортировки (created_at, views_count, average_rating, title)"),
    order: str = Query("desc", description="Порядок сортировки (asc, desc)"),
    build_repo: BuildRepository = Depends(get_build_repository)
):
    """Получить список сборок с фильтрами, сортировкой и пагинацией"""
    builds = await build_repo.search(
        query=query,
        author_id=author_id,
        skip=skip,
        limit=limit,
        sort_by=sort_by,
        order=order
    )
    
    total = await build_repo.count_search_results(
        query=query,
        author_id=author_id
    )
    
    return BuildListResponse(
        builds=builds,
        total=total,
        page=skip // limit + 1,
        per_page=limit,
        total_pages=math.ceil(total / limit) if total > 0 else 0
    )


@router.get("/top", response_model=BuildTopResponse)
async def get_top_builds(
    limit: int = Query(10, ge=1, le=50, description="Количество сборок в топе"),
    build_repo: BuildRepository = Depends(get_build_repository)
):
    """Получить топ сборок по рейтингу"""
    builds = await build_repo.get_top_builds(limit=limit)
    return BuildTopResponse(
        builds=builds,
        total=len(builds)
    )


@router.get("/my", response_model=BuildListResponse)
async def get_my_builds(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    build_repo: BuildRepository = Depends(get_build_repository)
):
    """Получить мои сборки"""
    builds = await build_repo.get_by_author(
        author_id=current_user.id,
        skip=skip,
        limit=limit
    )
    
    total = await build_repo.count_by_author(current_user.id)
    
    return BuildListResponse(
        builds=builds,
        total=total,
        page=skip // limit + 1,
        per_page=limit,
        total_pages=math.ceil(total / limit) if total > 0 else 0
    )


@router.get("/stats", response_model=BuildStatsResponse)
async def get_builds_stats(
    build_repo: BuildRepository = Depends(get_build_repository)
):
    """Получить статистику по сборкам"""
    stats = await build_repo.get_stats()
    return BuildStatsResponse(**stats)


@router.get("/components/unique", response_model=BuildComponentsResponse)
async def get_unique_components(
    build_repo: BuildRepository = Depends(get_build_repository)
):
    """Получить список доступных компонентов, сгруппированных по категориям"""
    components = await build_repo.get_unique_components()
    return BuildComponentsResponse(**components)


@router.get("/{build_id}", response_model=BuildResponse)
async def get_build(
    build_id: int,
    request: Request,
    current_user: Optional[User] = Depends(get_optional_user),
    build_repo: BuildRepository = Depends(get_build_repository)
):
    """Получить сборку по ID"""
    # Получаем IP адрес клиента для неавторизованных пользователей
    client_ip = request.client.host if request.client else None
    
    # Получаем сборку с отслеживанием просмотров
    build = await build_repo.get_with_view_tracking(
        build_id=build_id,
        user_id=current_user.id if current_user else None,
        client_ip=client_ip,
        redis_service=redis_service
    )
    
    if not build:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сборка не найдена"
        )
    
    return build


@router.put("/{build_id}", response_model=BuildResponse)
async def update_build(
    build_id: int,
    build_data: BuildUpdate,
    current_user: User = Depends(get_current_user),
    build_repo: BuildRepository = Depends(get_build_repository)
):
    """Обновить сборку"""
    build = await build_repo.get_by_id(build_id)
    if not build:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сборка не найдена"
        )
    
    # Проверяем, что пользователь является автором
    if build.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав для редактирования этой сборки"
        )
    
    return await build_repo.update(build, build_data)


@router.delete("/{build_id}", response_model=MessageResponse)
async def delete_build(
    build_id: int,
    current_user: User = Depends(get_current_user),
    build_repo: BuildRepository = Depends(get_build_repository)
):
    """Удалить сборку"""
    build = await build_repo.get_by_id(build_id)
    if not build:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сборка не найдена"
        )
    
    # Проверяем, что пользователь является автором
    if build.author_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав для удаления этой сборки"
        )
    
    success = await build_repo.delete(build)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при удалении сборки"
        )
    
    return MessageResponse(message="Сборка успешно удалена")


# ==================== Endpoints для оценок ====================

@router.post("/{build_id}/ratings", response_model=BuildRatingResponse, status_code=status.HTTP_201_CREATED)
async def create_rating(
    build_id: int,
    rating_data: BuildRatingCreate,
    current_user: User = Depends(get_current_user),
    build_repo: BuildRepository = Depends(get_build_repository)
):
    """Поставить оценку сборке"""
    # Проверяем, существует ли сборка
    build = await build_repo.get_by_id(build_id)
    if not build:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сборка не найдена"
        )
    
    # Проверяем, что пользователь не оценивает свою сборку
    if build.author_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вы не можете оценивать свою собственную сборку"
        )
    
    # Проверяем, не поставил ли пользователь уже оценку
    existing_rating = await build_repo.get_user_rating(build_id, current_user.id)
    if existing_rating:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Вы уже оценили эту сборку. Используйте PUT для обновления оценки."
        )
    
    return await build_repo.create_rating(build_id, current_user.id, rating_data)


@router.put("/{build_id}/ratings", response_model=BuildRatingResponse)
async def update_rating(
    build_id: int,
    rating_data: BuildRatingUpdate,
    current_user: User = Depends(get_current_user),
    build_repo: BuildRepository = Depends(get_build_repository)
):
    """Обновить оценку сборки"""
    # Проверяем, существует ли сборка
    build = await build_repo.get_by_id(build_id)
    if not build:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сборка не найдена"
        )
    
    # Получаем существующую оценку
    rating = await build_repo.get_user_rating(build_id, current_user.id)
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Вы еще не оценили эту сборку. Используйте POST для создания оценки."
        )
    
    return await build_repo.update_rating(rating, rating_data.score)


@router.delete("/{build_id}/ratings", response_model=MessageResponse)
async def delete_rating(
    build_id: int,
    current_user: User = Depends(get_current_user),
    build_repo: BuildRepository = Depends(get_build_repository)
):
    """Удалить оценку сборки"""
    # Получаем существующую оценку
    rating = await build_repo.get_user_rating(build_id, current_user.id)
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Оценка не найдена"
        )
    
    success = await build_repo.delete_rating(rating)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при удалении оценки"
        )
    
    return MessageResponse(message="Оценка успешно удалена")


@router.get("/{build_id}/ratings/my", response_model=BuildRatingResponse)
async def get_my_rating(
    build_id: int,
    current_user: User = Depends(get_current_user),
    build_repo: BuildRepository = Depends(get_build_repository)
):
    """Получить мою оценку для сборки"""
    rating = await build_repo.get_user_rating(build_id, current_user.id)
    if not rating:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Вы еще не оценили эту сборку"
        )
    
    return rating


# ==================== Endpoints для комментариев ====================

@router.post("/{build_id}/comments", response_model=BuildCommentSingleResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    build_id: int,
    comment_data: BuildCommentCreate,
    current_user: User = Depends(get_current_user),
    build_repo: BuildRepository = Depends(get_build_repository)
):
    """Создать комментарий к сборке"""
    # Проверяем, существует ли сборка
    build = await build_repo.get_by_id(build_id)
    if not build:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сборка не найдена"
        )
    
    # Если это ответ на комментарий, проверяем его существование и вложенность
    if comment_data.parent_id:
        parent_comment = await build_repo.get_comment_by_id(comment_data.parent_id)
        if not parent_comment or parent_comment.build_id != build_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Родительский комментарий не найден"
            )
        
        # Проверяем вложенность (максимум 2 уровня)
        # Если у родительского комментария уже есть parent_id, это значит он второго уровня
        # и мы не можем создать ответ на него (это был бы 3 уровень)
        if parent_comment.parent_id is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя отвечать на комментарий второго уровня. Максимальная вложенность - 2 уровня."
            )
    
    return await build_repo.create_comment(build_id, current_user.id, comment_data)


@router.get("/{build_id}/comments", response_model=BuildCommentListResponse)
async def get_comments(
    build_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    build_repo: BuildRepository = Depends(get_build_repository)
):
    """Получить комментарии к сборке"""
    # Проверяем, существует ли сборка
    build = await build_repo.get_by_id(build_id)
    if not build:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сборка не найдена"
        )
    
    comments = await build_repo.get_build_comments(build_id, skip, limit)
    total = await build_repo.count_build_comments(build_id)
    
    return BuildCommentListResponse(
        comments=comments,
        total=total
    )


@router.put("/{build_id}/comments/{comment_id}", response_model=BuildCommentSingleResponse)
async def update_comment(
    build_id: int,
    comment_id: int,
    comment_data: BuildCommentUpdate,
    current_user: User = Depends(get_current_user),
    build_repo: BuildRepository = Depends(get_build_repository)
):
    """Обновить комментарий"""
    comment = await build_repo.get_comment_by_id(comment_id)
    if not comment or comment.build_id != build_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Комментарий не найден"
        )
    
    # Проверяем, что пользователь является автором комментария
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав для редактирования этого комментария"
        )
    
    return await build_repo.update_comment(comment, comment_data.content)


@router.delete("/{build_id}/comments/{comment_id}", response_model=MessageResponse)
async def delete_comment(
    build_id: int,
    comment_id: int,
    current_user: User = Depends(get_current_user),
    build_repo: BuildRepository = Depends(get_build_repository)
):
    """Удалить комментарий"""
    comment = await build_repo.get_comment_by_id(comment_id)
    if not comment or comment.build_id != build_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Комментарий не найден"
        )
    
    # Проверяем, что пользователь является автором комментария
    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="У вас нет прав для удаления этого комментария"
        )
    
    success = await build_repo.delete_comment(comment)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Ошибка при удалении комментария"
        )
    
    return MessageResponse(message="Комментарий успешно удален")


# ==================== Endpoint для экспорта PDF ====================

@router.get("/{build_id}/export/pdf")
async def export_build_pdf(
    build_id: int,
    build_repo: BuildRepository = Depends(get_build_repository)
):
    """Экспортировать сборку в PDF"""
    # Получаем сборку с загруженными компонентами
    build = await build_repo.get_by_id(build_id)
    
    if not build:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Сборка не найдена"
        )
    
    try:
        # Создаем PDF в памяти
        pdf_buffer = io.BytesIO()
        await create_build_pdf(build, pdf_buffer)
        pdf_buffer.seek(0)
        
        # Создаем безопасное имя файла с транслитерацией
        safe_title = safe_filename(build.title, max_length=80, prefix=f"build_{build_id}_")
        filename = f"{safe_title}.pdf"
        
        # Кодируем имя файла для заголовка (RFC 5987)
        filename_encoded = urllib.parse.quote(filename, safe='')
        
        # Читаем данные из буфера
        pdf_data = pdf_buffer.read()
        pdf_buffer.close()
        
        return StreamingResponse(
            io.BytesIO(pdf_data),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=\"{filename}\"; filename*=UTF-8''{filename_encoded}"
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка при генерации PDF: {str(e)}"
        )


