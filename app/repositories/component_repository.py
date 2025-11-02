from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from typing import Optional, List
from app.models.component import Component, ComponentCategory


class ComponentRepository:
    """Репозиторий для работы с компонентами"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, component_id: int) -> Optional[Component]:
        """Получить компонент по ID"""
        result = await self.db.execute(select(Component).filter(Component.id == component_id))
        return result.scalar_one_or_none()
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[Component]:
        """Получить все компоненты с пагинацией"""
        result = await self.db.execute(select(Component).offset(skip).limit(limit))
        return list(result.scalars().all())
    
    async def get_by_category(self, category: ComponentCategory, skip: int = 0, limit: int = 100) -> List[Component]:
        """Получить компоненты по категории"""
        result = await self.db.execute(
            select(Component).filter(Component.category == category).offset(skip).limit(limit)
        )
        return list(result.scalars().all())
    
    async def create(self, name: str, link: str, price: Optional[int], image: Optional[str], category: ComponentCategory) -> Component:
        """Создать новый компонент"""
        component = Component(
            name=name,
            link=link,
            price=price,
            image=image,
            category=category
        )
        self.db.add(component)
        await self.db.commit()
        await self.db.refresh(component)
        return component
    
    async def create_or_update(self, name: str, link: str, price: Optional[int], image: Optional[str], category: ComponentCategory) -> Component:
        """Создать компонент или обновить существующий по ссылке"""
        # Проверяем, существует ли компонент с такой ссылкой
        result = await self.db.execute(select(Component).filter(Component.link == link))
        existing = result.scalar_one_or_none()
        
        if existing:
            # Обновляем существующий
            existing.name = name
            existing.price = price
            existing.image = image
            existing.category = category
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        else:
            # Создаем новый
            return await self.create(name, link, price, image, category)
    
    async def delete_all(self) -> int:
        """Удалить все компоненты"""
        try:
            result = await self.db.execute(select(Component))
            components = list(result.scalars().all())
            count = len(components)
            for component in components:
                await self.db.delete(component)
            await self.db.commit()
            return count
        except Exception:
            await self.db.rollback()
            return 0
    
    async def delete_by_category(self, category: ComponentCategory) -> int:
        """Удалить все компоненты категории"""
        try:
            result = await self.db.execute(select(Component).filter(Component.category == category))
            components = list(result.scalars().all())
            count = len(components)
            for component in components:
                await self.db.delete(component)
            await self.db.commit()
            return count
        except Exception:
            await self.db.rollback()
            return 0
    
    async def count(self) -> int:
        """Получить общее количество компонентов"""
        result = await self.db.execute(select(func.count(Component.id)))
        return result.scalar() or 0
    
    async def count_by_category(self, category: ComponentCategory) -> int:
        """Получить количество компонентов в категории"""
        result = await self.db.execute(select(func.count(Component.id)).filter(Component.category == category))
        return result.scalar() or 0
    
    async def get_by_category_with_search(
        self,
        category: ComponentCategory,
        query: str = "",
        skip: int = 0,
        limit: int = 100
    ) -> List[Component]:
        """Получить компоненты по категории с поиском по названию"""
        from sqlalchemy import select
        
        stmt = select(Component).filter(Component.category == category)
        
        # Добавляем поиск по названию, если указан
        if query:
            stmt = stmt.filter(Component.name.ilike(f"%{query}%"))
        
        # Применяем сортировку и пагинацию
        stmt = stmt.order_by(Component.name).offset(skip).limit(limit)
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

