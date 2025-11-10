"""
Сервис для работы со сборками
"""
import math
import io
import urllib.parse
from typing import Optional, List
from fastapi import HTTPException, status
from fastapi import Request as FastAPIRequest
from fastapi.responses import StreamingResponse
from app.repositories.build_repository import BuildRepository
from app.models.user import User
from app.schemas.build import (
    BuildCreate, BuildUpdate, BuildResponse, BuildListResponse, BuildTopResponse,
    BuildRatingCreate, BuildRatingUpdate, BuildRatingResponse,
    BuildCommentCreate, BuildCommentUpdate, BuildCommentResponse, 
    BuildCommentListResponse, BuildCommentSingleResponse, BuildStatsResponse,
    BuildComponentsResponse
)
from app.schemas.common import MessageResponse
from app.services.redis_service import RedisService
from app.services.pdf_generator import PDFGenerator
from app.utils.transliteration import safe_filename
import logging

logger = logging.getLogger(__name__)


class BuildService:
    """Сервис для работы со сборками"""
    
    def __init__(
        self, 
        build_repo: BuildRepository, 
        redis_service: RedisService,
        pdf_generator: PDFGenerator
    ):
        self.build_repo = build_repo
        self.redis_service = redis_service
        self.pdf_generator = pdf_generator
    
    async def create_build(
        self,
        build_data: BuildCreate,
        author_id: int
    ) -> BuildResponse:
        """
        Создать новую сборку
        
        Args:
            build_data: Данные для создания сборки
            author_id: ID автора сборки
            
        Returns:
            BuildResponse с данными созданной сборки
        """
        return await self.build_repo.create(build_data, author_id)
    
    async def get_builds(
        self,
        skip: int = 0,
        limit: int = 20,
        query: str = "",
        author_id: Optional[int] = None,
        sort_by: str = "created_at",
        order: str = "desc"
    ) -> BuildListResponse:
        """
        Получить список сборок с фильтрами, сортировкой и пагинацией
        
        Args:
            skip: Количество записей для пропуска
            limit: Максимальное количество записей
            query: Поиск по названию или описанию
            author_id: Фильтр по автору
            sort_by: Поле для сортировки
            order: Порядок сортировки (asc, desc)
            
        Returns:
            BuildListResponse со списком сборок
        """
        builds = await self.build_repo.search(
            query=query,
            author_id=author_id,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            order=order
        )
        
        total = await self.build_repo.count_search_results(
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
    
    async def get_top_builds(self, limit: int = 10) -> BuildTopResponse:
        """
        Получить топ сборок по рейтингу
        
        Args:
            limit: Количество сборок в топе
            
        Returns:
            BuildTopResponse с топ сборками
        """
        builds = await self.build_repo.get_top_builds(limit=limit)
        return BuildTopResponse(
            builds=builds,
            total=len(builds)
        )
    
    async def get_user_builds(
        self,
        author_id: int,
        skip: int = 0,
        limit: int = 20
    ) -> BuildListResponse:
        """
        Получить сборки пользователя
        
        Args:
            author_id: ID автора
            skip: Количество записей для пропуска
            limit: Максимальное количество записей
            
        Returns:
            BuildListResponse со списком сборок
        """
        builds = await self.build_repo.get_by_author(
            author_id=author_id,
            skip=skip,
            limit=limit
        )
        
        total = await self.build_repo.count_by_author(author_id)
        
        return BuildListResponse(
            builds=builds,
            total=total,
            page=skip // limit + 1,
            per_page=limit,
            total_pages=math.ceil(total / limit) if total > 0 else 0
        )
    
    async def get_builds_stats(self) -> BuildStatsResponse:
        """
        Получить статистику по сборкам
        
        Returns:
            BuildStatsResponse со статистикой
        """
        stats = await self.build_repo.get_stats()
        return BuildStatsResponse(**stats)
    
    async def get_unique_components(self) -> BuildComponentsResponse:
        """
        Получить список доступных компонентов, сгруппированных по категориям
        
        Returns:
            BuildComponentsResponse с компонентами
        """
        components = await self.build_repo.get_unique_components()
        return BuildComponentsResponse(**components)
    
    async def get_build(
        self,
        build_id: int,
        request: FastAPIRequest,
        current_user: Optional[User] = None
    ) -> BuildResponse:
        """
        Получить сборку по ID с отслеживанием просмотров
        
        Args:
            build_id: ID сборки
            request: Объект запроса для получения IP
            current_user: Текущий пользователь (опционально)
            
        Returns:
            BuildResponse с данными сборки
        """
        # Получаем IP адрес клиента для неавторизованных пользователей
        client_ip = request.client.host if request.client else None
        
        # Получаем сборку с отслеживанием просмотров
        build = await self.build_repo.get_with_view_tracking(
            build_id=build_id,
            user_id=current_user.id if current_user else None,
            client_ip=client_ip,
            redis_service=self.redis_service
        )
        
        if not build:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Сборка не найдена"
            )
        
        return build
    
    async def update_build(
        self,
        build_id: int,
        build_data: BuildUpdate,
        current_user: User
    ) -> BuildResponse:
        """
        Обновить сборку
        
        Args:
            build_id: ID сборки
            build_data: Данные для обновления
            current_user: Текущий пользователь
            
        Returns:
            BuildResponse с обновленными данными сборки
        """
        build = await self.build_repo.get_by_id(build_id)
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
        
        return await self.build_repo.update(build, build_data)
    
    async def delete_build(
        self,
        build_id: int,
        current_user: User
    ) -> MessageResponse:
        """
        Удалить сборку
        
        Args:
            build_id: ID сборки
            current_user: Текущий пользователь
            
        Returns:
            MessageResponse с сообщением об успехе
        """
        build = await self.build_repo.get_by_id(build_id)
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
        
        success = await self.build_repo.delete(build)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при удалении сборки"
            )
        
        return MessageResponse(message="Сборка успешно удалена")
    
    # ==================== Методы для оценок ====================
    
    async def create_rating(
        self,
        build_id: int,
        rating_data: BuildRatingCreate,
        current_user: User
    ) -> BuildRatingResponse:
        """
        Поставить оценку сборке
        
        Args:
            build_id: ID сборки
            rating_data: Данные оценки
            current_user: Текущий пользователь
            
        Returns:
            BuildRatingResponse с данными оценки
        """
        # Проверяем, существует ли сборка
        build = await self.build_repo.get_by_id(build_id)
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
        existing_rating = await self.build_repo.get_user_rating(build_id, current_user.id)
        if existing_rating:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Вы уже оценили эту сборку. Используйте PUT для обновления оценки."
            )
        
        return await self.build_repo.create_rating(build_id, current_user.id, rating_data)
    
    async def update_rating(
        self,
        build_id: int,
        rating_data: BuildRatingUpdate,
        current_user: User
    ) -> BuildRatingResponse:
        """
        Обновить оценку сборки
        
        Args:
            build_id: ID сборки
            rating_data: Данные для обновления оценки
            current_user: Текущий пользователь
            
        Returns:
            BuildRatingResponse с обновленными данными оценки
        """
        # Проверяем, существует ли сборка
        build = await self.build_repo.get_by_id(build_id)
        if not build:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Сборка не найдена"
            )
        
        # Получаем существующую оценку
        rating = await self.build_repo.get_user_rating(build_id, current_user.id)
        if not rating:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Вы еще не оценили эту сборку. Используйте POST для создания оценки."
            )
        
        return await self.build_repo.update_rating(rating, rating_data.score)
    
    async def delete_rating(
        self,
        build_id: int,
        current_user: User
    ) -> MessageResponse:
        """
        Удалить оценку сборки
        
        Args:
            build_id: ID сборки
            current_user: Текущий пользователь
            
        Returns:
            MessageResponse с сообщением об успехе
        """
        # Получаем существующую оценку
        rating = await self.build_repo.get_user_rating(build_id, current_user.id)
        if not rating:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Оценка не найдена"
            )
        
        success = await self.build_repo.delete_rating(rating)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при удалении оценки"
            )
        
        return MessageResponse(message="Оценка успешно удалена")
    
    async def get_user_rating(
        self,
        build_id: int,
        current_user: User
    ) -> BuildRatingResponse:
        """
        Получить оценку пользователя для сборки
        
        Args:
            build_id: ID сборки
            current_user: Текущий пользователь
            
        Returns:
            BuildRatingResponse с данными оценки
        """
        rating = await self.build_repo.get_user_rating(build_id, current_user.id)
        if not rating:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Вы еще не оценили эту сборку"
            )
        
        return rating
    
    # ==================== Методы для комментариев ====================
    
    async def create_comment(
        self,
        build_id: int,
        comment_data: BuildCommentCreate,
        current_user: User
    ) -> BuildCommentSingleResponse:
        """
        Создать комментарий к сборке
        
        Args:
            build_id: ID сборки
            comment_data: Данные комментария
            current_user: Текущий пользователь
            
        Returns:
            BuildCommentSingleResponse с данными комментария
        """
        # Проверяем, существует ли сборка
        build = await self.build_repo.get_by_id(build_id)
        if not build:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Сборка не найдена"
            )
        
        # Если это ответ на комментарий, проверяем его существование и вложенность
        if comment_data.parent_id:
            parent_comment = await self.build_repo.get_comment_by_id(comment_data.parent_id)
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
        
        return await self.build_repo.create_comment(build_id, current_user.id, comment_data)
    
    async def get_comments(
        self,
        build_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> BuildCommentListResponse:
        """
        Получить комментарии к сборке
        
        Args:
            build_id: ID сборки
            skip: Количество записей для пропуска
            limit: Максимальное количество записей
            
        Returns:
            BuildCommentListResponse со списком комментариев
        """
        # Проверяем, существует ли сборка
        build = await self.build_repo.get_by_id(build_id)
        if not build:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Сборка не найдена"
            )
        
        comments = await self.build_repo.get_build_comments(build_id, skip, limit)
        total = await self.build_repo.count_build_comments(build_id)
        
        return BuildCommentListResponse(
            comments=comments,
            total=total
        )
    
    async def update_comment(
        self,
        build_id: int,
        comment_id: int,
        comment_data: BuildCommentUpdate,
        current_user: User
    ) -> BuildCommentSingleResponse:
        """
        Обновить комментарий
        
        Args:
            build_id: ID сборки
            comment_id: ID комментария
            comment_data: Данные для обновления
            current_user: Текущий пользователь
            
        Returns:
            BuildCommentSingleResponse с обновленными данными комментария
        """
        comment = await self.build_repo.get_comment_by_id(comment_id)
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
        
        return await self.build_repo.update_comment(comment, comment_data.content)
    
    async def delete_comment(
        self,
        build_id: int,
        comment_id: int,
        current_user: User
    ) -> MessageResponse:
        """
        Удалить комментарий
        
        Args:
            build_id: ID сборки
            comment_id: ID комментария
            current_user: Текущий пользователь
            
        Returns:
            MessageResponse с сообщением об успехе
        """
        comment = await self.build_repo.get_comment_by_id(comment_id)
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
        
        success = await self.build_repo.delete_comment(comment)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при удалении комментария"
            )
        
        return MessageResponse(message="Комментарий успешно удален")
    
    # ==================== Метод для экспорта PDF ====================
    
    async def export_build_pdf(self, build_id: int) -> StreamingResponse:
        """
        Экспортировать сборку в PDF
        
        Args:
            build_id: ID сборки
            
        Returns:
            StreamingResponse с PDF файлом
        """
        # Получаем сборку с загруженными компонентами
        build = await self.build_repo.get_by_id(build_id)
        
        if not build:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Сборка не найдена"
            )
        
        try:
            # Создаем PDF в памяти
            pdf_buffer = io.BytesIO()
            await self.pdf_generator.create_build_pdf(build, pdf_buffer)
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

