from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import TypeVar, Generic, Type, Optional, List

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """Базовый класс для всех репозиториев"""
    
    def __init__(self, db: AsyncSession, model: Type[T]):
        self.db = db
        self.model = model
    
    async def get_by_id(self, id: int) -> Optional[T]:
        """Получить запись по ID"""
        result = await self.db.execute(select(self.model).filter(self.model.id == id))
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Получить все записи с пагинацией"""
        result = await self.db.execute(select(self.model).offset(skip).limit(limit))
        return list(result.scalars().all())
    
    async def count(self) -> int:
        """Получить общее количество записей"""
        result = await self.db.execute(select(self.model))
        return len(list(result.scalars().all()))
    
    async def delete(self, entity: T) -> bool:
        """Удалить запись"""
        try:
            await self.db.delete(entity)
            await self.db.commit()
            return True
        except Exception:
            await self.db.rollback()
            return False


