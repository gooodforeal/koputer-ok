from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.repositories.base import BaseRepository
from app.models.feedback import Feedback, FeedbackStatus, FeedbackType
from app.models.user import User
from app.schemas.feedback import FeedbackCreate, FeedbackUpdate, FeedbackAdminUpdate, FeedbackStats


class FeedbackRepository(BaseRepository[Feedback]):
    """Репозиторий для работы с отзывами"""
    
    def __init__(self, db: AsyncSession):
        super().__init__(db, Feedback)
    
    async def get_user_feedback(self, user_id: int) -> Optional[Feedback]:
        """Получить отзыв пользователя (если существует)"""
        result = await self.db.execute(
            select(Feedback)
            .filter(Feedback.user_id == user_id)
            .options(selectinload(Feedback.user), selectinload(Feedback.assigned_to))
        )
        return result.scalar_one_or_none()
    
    async def create_feedback(self, feedback_data: FeedbackCreate, user_id: int) -> Feedback:
        """Создать новый отзыв"""
        feedback = Feedback(
            title=feedback_data.title,
            description=feedback_data.description,
            type=feedback_data.type,
            rating=feedback_data.rating,
            user_id=user_id
        )
        self.db.add(feedback)
        await self.db.commit()
        await self.db.refresh(feedback)
        
        # Загружаем связанные объекты
        result = await self.db.execute(
            select(Feedback)
            .filter(Feedback.id == feedback.id)
            .options(selectinload(Feedback.user), selectinload(Feedback.assigned_to))
        )
        return result.scalar_one()
    
    async def get_feedback_by_id(self, feedback_id: int) -> Optional[Feedback]:
        """Получить отзыв по ID с загрузкой связей"""
        result = await self.db.execute(
            select(Feedback)
            .filter(Feedback.id == feedback_id)
            .options(selectinload(Feedback.user), selectinload(Feedback.assigned_to))
        )
        return result.scalar_one_or_none()
    
    async def get_all_feedbacks(
        self, 
        skip: int = 0, 
        limit: int = 100,
        status: Optional[FeedbackStatus] = None,
        feedback_type: Optional[FeedbackType] = None
    ) -> List[Feedback]:
        """Получить все отзывы с фильтрацией"""
        query = (
            select(Feedback)
            .options(selectinload(Feedback.user), selectinload(Feedback.assigned_to))
            .order_by(Feedback.created_at.desc())
        )
        
        if status:
            query = query.filter(Feedback.status == status)
        if feedback_type:
            query = query.filter(Feedback.type == feedback_type)
        
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def count_all_feedbacks(
        self,
        status: Optional[FeedbackStatus] = None,
        feedback_type: Optional[FeedbackType] = None
    ) -> int:
        """Подсчитать общее количество отзывов с фильтрацией"""
        query = select(func.count(Feedback.id))
        
        if status:
            query = query.filter(Feedback.status == status)
        if feedback_type:
            query = query.filter(Feedback.type == feedback_type)
        
        result = await self.db.execute(query)
        return result.scalar() or 0
    
    async def get_user_feedbacks(
        self, 
        user_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Feedback]:
        """Получить отзывы пользователя"""
        result = await self.db.execute(
            select(Feedback)
            .filter(Feedback.user_id == user_id)
            .options(selectinload(Feedback.user), selectinload(Feedback.assigned_to))
            .order_by(Feedback.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def count_user_feedbacks(self, user_id: int) -> int:
        """Подсчитать количество отзывов пользователя"""
        result = await self.db.execute(
            select(func.count(Feedback.id)).filter(Feedback.user_id == user_id)
        )
        return result.scalar() or 0
    
    async def get_assigned_feedbacks(
        self, 
        admin_id: int, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[Feedback]:
        """Получить отзывы, назначенные администратору"""
        result = await self.db.execute(
            select(Feedback)
            .filter(Feedback.assigned_to_id == admin_id)
            .options(selectinload(Feedback.user), selectinload(Feedback.assigned_to))
            .order_by(Feedback.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def count_assigned_feedbacks(self, admin_id: int) -> int:
        """Подсчитать количество отзывов, назначенных администратору"""
        result = await self.db.execute(
            select(func.count(Feedback.id)).filter(Feedback.assigned_to_id == admin_id)
        )
        return result.scalar() or 0
    
    async def update_feedback(
        self, 
        feedback_id: int, 
        feedback_data: FeedbackUpdate
    ) -> Optional[Feedback]:
        """Обновить отзыв пользователем"""
        feedback = await self.get_by_id(feedback_id)
        if not feedback:
            return None
        
        update_data = feedback_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(feedback, field, value)
        
        await self.db.commit()
        await self.db.refresh(feedback)
        
        # Загружаем связанные объекты
        return await self.get_feedback_by_id(feedback_id)
    
    async def admin_update_feedback(
        self, 
        feedback_id: int, 
        feedback_data: FeedbackAdminUpdate,
        admin_id: Optional[int] = None
    ) -> Optional[Feedback]:
        """Обновить отзыв администратором"""
        feedback = await self.get_by_id(feedback_id)
        if not feedback:
            return None
        
        update_data = feedback_data.model_dump(exclude_unset=True)
        
        # Если устанавливается статус "в работе" и не указан назначенный администратор,
        # автоматически назначаем текущего администратора
        if (update_data.get('status') == FeedbackStatus.IN_PROGRESS and 
            'assigned_to_id' not in update_data and 
            admin_id is not None):
            update_data['assigned_to_id'] = admin_id
        
        for field, value in update_data.items():
            setattr(feedback, field, value)
        
        await self.db.commit()
        await self.db.refresh(feedback)
        
        # Загружаем связанные объекты
        return await self.get_feedback_by_id(feedback_id)
    
    async def delete_feedback(self, feedback_id: int) -> bool:
        """Удалить отзыв"""
        feedback = await self.get_by_id(feedback_id)
        if not feedback:
            return False
        
        return await self.delete(feedback)
    
    async def get_stats(self) -> FeedbackStats:
        """Получить статистику по отзывам"""
        # Общее количество
        total_result = await self.db.execute(select(func.count(Feedback.id)))
        total = total_result.scalar()
        
        # Количество по статусам
        status_counts = {}
        for status in FeedbackStatus:
            result = await self.db.execute(
                select(func.count(Feedback.id)).filter(Feedback.status == status)
            )
            status_counts[status.value.lower()] = result.scalar()
        
        # Количество по типам
        type_counts = {}
        for feedback_type in FeedbackType:
            result = await self.db.execute(
                select(func.count(Feedback.id)).filter(Feedback.type == feedback_type)
            )
            type_counts[feedback_type.value] = result.scalar()
        
        # Средняя оценка
        avg_rating_result = await self.db.execute(
            select(func.avg(Feedback.rating)).filter(Feedback.rating.isnot(None))
        )
        avg_rating = avg_rating_result.scalar()
        
        return FeedbackStats(
            total=total or 0,
            new=status_counts.get('new', 0),
            in_review=status_counts.get('in_review', 0),
            in_progress=status_counts.get('in_progress', 0),
            resolved=status_counts.get('resolved', 0),
            rejected=status_counts.get('rejected', 0),
            by_type=type_counts,
            average_rating=float(avg_rating) if avg_rating else None
        )

