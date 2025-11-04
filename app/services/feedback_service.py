"""
Сервис для работы с отзывами
"""
import math
from typing import Optional, List
from fastapi import HTTPException, status
from app.repositories.feedback_repository import FeedbackRepository
from app.repositories import UserRepository
from app.models.user import User, UserRole
from app.models.feedback import FeedbackStatus, FeedbackType
from app.schemas.feedback import (
    FeedbackCreate, FeedbackUpdate, FeedbackAdminUpdate,
    FeedbackResponse, FeedbackListResponse, FeedbackStats
)

class FeedbackService:
    """Сервис для работы с отзывами"""
    
    def __init__(self, feedback_repo: FeedbackRepository):
        self.feedback_repo = feedback_repo
    
    async def create_feedback(
        self,
        feedback_data: FeedbackCreate,
        current_user: User
    ) -> FeedbackResponse:
        """
        Создать новый отзыв
        
        Args:
            feedback_data: Данные для создания отзыва
            current_user: Текущий пользователь
            
        Returns:
            FeedbackResponse с данными отзыва
        """
        # Проверяем, есть ли уже отзыв от этого пользователя
        existing_feedback = await self.feedback_repo.get_user_feedback(current_user.id)
        if existing_feedback:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Вы уже оставили отзыв. Вы можете отредактировать существующий отзыв."
            )
        
        return await self.feedback_repo.create_feedback(feedback_data, current_user.id)
    
    async def get_public_feedbacks(
        self,
        skip: int = 0,
        limit: int = 100
    ) -> FeedbackListResponse:
        """
        Получить публичные отзывы (доступно без авторизации)
        
        Args:
            skip: Количество записей для пропуска
            limit: Максимальное количество записей
            
        Returns:
            FeedbackListResponse со списком отзывов
        """
        # Показываем все отзывы для всех пользователей
        feedbacks = await self.feedback_repo.get_all_feedbacks(
            skip=skip, 
            limit=limit,
            status=None,
            feedback_type=None
        )
        total = await self.feedback_repo.count_all_feedbacks(
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
    
    async def get_feedbacks(
        self,
        skip: int = 0,
        limit: int = 100,
        status_filter: Optional[FeedbackStatus] = None,
        type_filter: Optional[FeedbackType] = None,
        current_user: User = None
    ) -> FeedbackListResponse:
        """
        Получить все отзывы (доступно для авторизованных пользователей, фильтры только для администраторов)
        
        Args:
            skip: Количество записей для пропуска
            limit: Максимальное количество записей
            status_filter: Фильтр по статусу (только для администраторов)
            type_filter: Фильтр по типу (только для администраторов)
            current_user: Текущий пользователь
            
        Returns:
            FeedbackListResponse со списком отзывов
        """
        # Обычные пользователи не могут использовать фильтры
        if current_user and current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
            status_filter = None
            type_filter = None
        
        feedbacks = await self.feedback_repo.get_all_feedbacks(
            skip=skip, 
            limit=limit,
            status=status_filter,
            feedback_type=type_filter
        )
        total = await self.feedback_repo.count_all_feedbacks(
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
    
    async def get_user_feedbacks(
        self,
        current_user: User,
        skip: int = 0,
        limit: int = 100
    ) -> FeedbackListResponse:
        """
        Получить отзывы пользователя
        
        Args:
            current_user: Текущий пользователь
            skip: Количество записей для пропуска
            limit: Максимальное количество записей
            
        Returns:
            FeedbackListResponse со списком отзывов
        """
        feedbacks = await self.feedback_repo.get_user_feedbacks(current_user.id, skip, limit)
        total = await self.feedback_repo.count_user_feedbacks(current_user.id)
        
        return FeedbackListResponse(
            feedbacks=feedbacks,
            total=total,
            page=skip // limit + 1,
            per_page=limit,
            total_pages=math.ceil(total / limit) if total > 0 else 0
        )
    
    async def get_assigned_feedbacks(
        self,
        current_user: User,
        skip: int = 0,
        limit: int = 100
    ) -> FeedbackListResponse:
        """
        Получить отзывы, назначенные администратору
        
        Args:
            current_user: Текущий пользователь (должен быть администратором)
            skip: Количество записей для пропуска
            limit: Максимальное количество записей
            
        Returns:
            FeedbackListResponse со списком отзывов
        """
        feedbacks = await self.feedback_repo.get_assigned_feedbacks(current_user.id, skip, limit)
        total = await self.feedback_repo.count_assigned_feedbacks(current_user.id)
        
        return FeedbackListResponse(
            feedbacks=feedbacks,
            total=total,
            page=skip // limit + 1,
            per_page=limit,
            total_pages=math.ceil(total / limit) if total > 0 else 0
        )
    
    async def get_feedback_stats(self, current_user: User) -> FeedbackStats:
        """
        Получить статистику по отзывам
        
        Args:
            current_user: Текущий пользователь (должен быть администратором)
            
        Returns:
            FeedbackStats со статистикой
        """
        return await self.feedback_repo.get_stats()
    
    async def get_feedback(self, feedback_id: int) -> FeedbackResponse:
        """
        Получить отзыв по ID (доступно для всех авторизованных пользователей)
        
        Args:
            feedback_id: ID отзыва
            
        Returns:
            FeedbackResponse с данными отзыва
        """
        feedback = await self.feedback_repo.get_feedback_by_id(feedback_id)
        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Отзыв не найден"
            )
        
        # Все авторизованные пользователи могут просматривать отзывы
        return feedback
    
    async def update_feedback(
        self,
        feedback_id: int,
        feedback_data: FeedbackUpdate,
        current_user: User
    ) -> FeedbackResponse:
        """
        Обновить свой отзыв
        
        Args:
            feedback_id: ID отзыва
            feedback_data: Данные для обновления
            current_user: Текущий пользователь
            
        Returns:
            FeedbackResponse с обновленными данными отзыва
        """
        feedback = await self.feedback_repo.get_feedback_by_id(feedback_id)
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
        
        updated_feedback = await self.feedback_repo.update_feedback(feedback_id, feedback_data)
        return updated_feedback
    
    async def admin_update_feedback(
        self,
        feedback_id: int,
        feedback_data: FeedbackAdminUpdate,
        current_user: User,
        user_repo: UserRepository
    ) -> FeedbackResponse:
        """
        Обновить отзыв администратором
        
        Args:
            feedback_id: ID отзыва
            feedback_data: Данные для обновления
            current_user: Текущий пользователь (должен быть администратором)
            user_repo: Репозиторий пользователей
            
        Returns:
            FeedbackResponse с обновленными данными отзыва
        """
        feedback = await self.feedback_repo.get_feedback_by_id(feedback_id)
        if not feedback:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Отзыв не найден"
            )
        
        # Если назначается администратор, проверяем, что это действительно администратор
        if feedback_data.assigned_to_id is not None:
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
        
        updated_feedback = await self.feedback_repo.admin_update_feedback(feedback_id, feedback_data, current_user.id)
        return updated_feedback
    
    async def delete_feedback(
        self,
        feedback_id: int,
        current_user: User
    ) -> None:
        """
        Удалить отзыв
        
        Args:
            feedback_id: ID отзыва
            current_user: Текущий пользователь
        """
        feedback = await self.feedback_repo.get_feedback_by_id(feedback_id)
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
        
        success = await self.feedback_repo.delete_feedback(feedback_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Ошибка при удалении отзыва"
            )

