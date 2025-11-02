from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_, desc, update, insert, delete
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from typing import Optional, List, TYPE_CHECKING
from app.models.build import Build, BuildRating, BuildComment, BuildView, build_components
from app.models.component import Component, ComponentCategory
from app.schemas.build import BuildCreate, BuildUpdate, BuildRatingCreate, BuildCommentCreate

if TYPE_CHECKING:
    from app.services.redis_service import RedisService

# Обязательные категории компонентов для сборки
REQUIRED_CATEGORIES = {
    ComponentCategory.PROCESSORY,
    ComponentCategory.VIDEOKARTY,
    ComponentCategory.MATERINSKIE_PLATY,
    ComponentCategory.OPERATIVNAYA_PAMYAT,
    ComponentCategory.KORPUSA,
    ComponentCategory.BLOKI_PITANIYA,
    ComponentCategory.OHLAZHDENIE,
}

# Категории накопителей (хотя бы один должен быть)
STORAGE_CATEGORIES = {
    ComponentCategory.SSD_NAKOPITELI,
    ComponentCategory.ZHESTKIE_DISKI,
}

# Русские названия категорий для сообщений об ошибках
CATEGORY_NAMES = {
    ComponentCategory.PROCESSORY: "Процессор",
    ComponentCategory.VIDEOKARTY: "Видеокарта",
    ComponentCategory.MATERINSKIE_PLATY: "Материнская плата",
    ComponentCategory.OPERATIVNAYA_PAMYAT: "Оперативная память",
    ComponentCategory.KORPUSA: "Корпус",
    ComponentCategory.BLOKI_PITANIYA: "Блок питания",
    ComponentCategory.OHLAZHDENIE: "Охлаждение",
    ComponentCategory.SSD_NAKOPITELI: "SSD накопитель",
    ComponentCategory.ZHESTKIE_DISKI: "Жесткий диск",
}


def validate_component_categories(components: List[Component]) -> None:
    """Проверяет, что сборка содержит все обязательные категории компонентов"""
    from fastapi import HTTPException, status
    
    if not components:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Сборка должна содержать хотя бы один компонент"
        )
    
    # Получаем набор категорий из переданных компонентов
    component_categories = {comp.category for comp in components}
    
    # Проверяем обязательные категории
    missing_categories = REQUIRED_CATEGORIES - component_categories
    if missing_categories:
        missing_names = [CATEGORY_NAMES.get(cat, str(cat)) for cat in missing_categories]
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Сборка должна содержать все обязательные компоненты. Отсутствуют: {', '.join(missing_names)}"
        )
    
    # Проверяем наличие хотя бы одного накопителя
    has_storage = bool(component_categories & STORAGE_CATEGORIES)
    if not has_storage:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Сборка должна содержать хотя бы один накопитель (SSD или HDD)"
        )


class BuildRepository:
    """Репозиторий для работы со сборками"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # === Методы для Build ===
    
    async def get_build_author_id(self, build_id: int) -> Optional[int]:
        """Получить только author_id сборки (легкий запрос для проверки)"""
        result = await self.db.execute(
            select(Build.author_id).filter(Build.id == build_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_id(self, build_id: int) -> Optional[Build]:
        """Получить сборку по ID с загрузкой связанных данных"""
        result = await self.db.execute(
            select(Build)
            .options(
                selectinload(Build.author),
                selectinload(Build.ratings),
                selectinload(Build.components)
            )
            .filter(Build.id == build_id)
        )
        return result.scalar_one_or_none()
    
    async def get_with_view_tracking(
        self,
        build_id: int,
        user_id: Optional[int],
        client_ip: Optional[str],
        redis_service: Optional["RedisService"] = None
    ) -> Optional[Build]:
        """Получить сборку по ID с отслеживанием просмотров
        
        Args:
            build_id: ID сборки
            user_id: ID пользователя (если авторизован)
            client_ip: IP адрес клиента (для неавторизованных)
            redis_service: Сервис Redis для кеширования просмотров
        
        Returns:
            Build или None если сборка не найдена
        """
        # Проверяем существование сборки
        author_id = await self.get_build_author_id(build_id)
        if author_id is None:
            return None
        
        # Увеличиваем счетчик просмотров с использованием Redis
        if redis_service:
            if user_id is not None:
                # Для авторизованных пользователей - только если это не автор
                if user_id != author_id:
                    redis_key = f"build_view:{build_id}:user_{user_id}"
                    view_exists = await redis_service.exists(redis_key)
                    
                    if not view_exists:
                        await self.increment_views(build_id, None)
                        await redis_service.set(redis_key, True, ttl=300)
            elif client_ip:
                # Для неавторизованных пользователей - используем IP
                redis_key = f"build_view:{build_id}:{client_ip}"
                view_exists = await redis_service.exists(redis_key)
                
                if not view_exists:
                    await self.increment_views(build_id, None)
                    await redis_service.set(redis_key, True, ttl=300)
        else:
            # Если Redis недоступен, просто увеличиваем счетчик
            await self.increment_views(build_id, user_id)
        
        # Загружаем полный объект ПОСЛЕ increment_views (чтобы избежать detached state)
        return await self.get_by_id(build_id)
    
    async def get_all(self, skip: int = 0, limit: int = 20) -> List[Build]:
        """Получить все сборки с пагинацией"""
        result = await self.db.execute(
            select(Build)
            .options(
                selectinload(Build.author),
                selectinload(Build.ratings),
                selectinload(Build.components)
            )
            .order_by(desc(Build.created_at))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_by_author(self, author_id: int, skip: int = 0, limit: int = 20) -> List[Build]:
        """Получить сборки по автору"""
        result = await self.db.execute(
            select(Build)
            .options(
                selectinload(Build.author),
                selectinload(Build.ratings),
                selectinload(Build.components)
            )
            .filter(Build.author_id == author_id)
            .order_by(desc(Build.created_at))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def create(self, build_data: BuildCreate, author_id: int) -> Build:
        """Создать новую сборку"""
        from fastapi import HTTPException, status
        
        components = []
        
        # Проверяем, что указаны компоненты
        if not build_data.component_ids or len(build_data.component_ids) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Сборка должна содержать компоненты"
            )
        
        # Проверяем, что все компоненты существуют в базе
        components_result = await self.db.execute(
            select(Component).filter(Component.id.in_(build_data.component_ids))
        )
        components = list(components_result.scalars().all())
        
        # Проверяем, что найдено столько же компонентов, сколько запрошено
        if len(components) != len(build_data.component_ids):
            found_ids = {c.id for c in components}
            missing_ids = set(build_data.component_ids) - found_ids
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Невозможно создать сборку: компоненты с ID {missing_ids} не найдены в базе данных. Все компоненты должны быть из базы данных."
            )
        
        # Валидируем наличие всех обязательных категорий
        validate_component_categories(components)
        
        db_build = Build(
            title=build_data.title,
            description=build_data.description,
            additional_info=build_data.additional_info,
            author_id=author_id
        )
        self.db.add(db_build)
        await self.db.flush()  # Получаем ID сборки
        
        # Добавляем компоненты напрямую в промежуточную таблицу, чтобы избежать lazy loading
        await self.db.execute(
            insert(build_components).values(
                [{"build_id": db_build.id, "component_id": comp.id} for comp in components]
            )
        )
        
        await self.db.commit()
        await self.db.refresh(db_build)
        
        # Загружаем связанные данные
        return await self.get_by_id(db_build.id)
    
    async def update(self, build: Build, build_data: BuildUpdate) -> Build:
        """Обновить сборку"""
        from fastapi import HTTPException, status
        
        update_data = build_data.model_dump(exclude_unset=True)
        
        # Обрабатываем component_ids отдельно
        component_ids = update_data.pop('component_ids', None)
        
        # Обновляем остальные поля
        for key, value in update_data.items():
            if hasattr(build, key):
                setattr(build, key, value)
        
        # Обновляем компоненты, если они указаны
        if component_ids is not None:
            # Удаляем все существующие связи с компонентами
            await self.db.execute(
                delete(build_components).where(build_components.c.build_id == build.id)
            )
            
            if len(component_ids) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Сборка должна содержать компоненты"
                )
            
            # Проверяем, что все компоненты существуют
            components_result = await self.db.execute(
                select(Component).filter(Component.id.in_(component_ids))
            )
            components = list(components_result.scalars().all())
            
            # Проверяем, что найдено столько же компонентов, сколько запрошено
            if len(components) != len(component_ids):
                found_ids = {c.id for c in components}
                missing_ids = set(component_ids) - found_ids
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Невозможно обновить сборку: компоненты с ID {missing_ids} не найдены в базе данных. Все компоненты должны быть из базы данных."
                )
            
            # Валидируем наличие всех обязательных категорий
            validate_component_categories(components)
            
            # Добавляем новые связи напрямую в промежуточную таблицу
            await self.db.execute(
                insert(build_components).values(
                    [{"build_id": build.id, "component_id": comp.id} for comp in components]
                )
            )
        else:
            # Если компоненты не указаны, проверяем существующие компоненты сборки
            # Загружаем компоненты сборки напрямую
            if not build.components:
                # Если компоненты не загружены, загружаем их
                await self.db.refresh(build, ['components'])
                # Если все еще не загружены, получаем через запрос
                if not build.components:
                    components_result = await self.db.execute(
                        select(Component)
                        .join(build_components)
                        .filter(build_components.c.build_id == build.id)
                    )
                    build.components = list(components_result.scalars().all())
            
            if not build.components:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Сборка должна содержать компоненты"
                )
            # Валидируем существующие компоненты
            validate_component_categories(build.components)
        
        await self.db.commit()
        await self.db.refresh(build)
        return await self.get_by_id(build.id)
    
    async def delete(self, build: Build) -> bool:
        """Удалить сборку"""
        try:
            await self.db.delete(build)
            await self.db.commit()
            return True
        except Exception:
            await self.db.rollback()
            return False
    
    async def increment_views(self, build_id: int, user_id: Optional[int] = None) -> bool:
        """Увеличить счетчик просмотров
        
        Для авторизованных пользователей - только один раз для каждого пользователя.
        Для неавторизованных - каждый раз увеличивается счетчик.
        
        Args:
            build_id: ID сборки
            user_id: ID пользователя (опционально, None для неавторизованных)
        
        Returns:
            bool: True если просмотр засчитан, False если авторизованный пользователь уже просматривал
        """
        # Для авторизованных пользователей проверяем уникальность
        if user_id is not None:
            # Проверяем, просматривал ли пользователь уже эту сборку
            existing_view_result = await self.db.execute(
                select(BuildView).filter(
                    BuildView.build_id == build_id,
                    BuildView.user_id == user_id
                )
            )
            existing_view = existing_view_result.scalar_one_or_none()
            
            if existing_view:
                # Пользователь уже просматривал эту сборку
                return False
            
            try:
                # Создаем запись о просмотре
                build_view = BuildView(build_id=build_id, user_id=user_id)
                self.db.add(build_view)
                
                # Увеличиваем счетчик атомарной операцией
                await self.db.execute(
                    update(Build)
                    .where(Build.id == build_id)
                    .values(views_count=Build.views_count + 1)
                )
                await self.db.commit()
                return True
            except IntegrityError:
                # На случай race condition
                await self.db.rollback()
                return False
        else:
            # Для неавторизованных пользователей просто увеличиваем счетчик
            try:
                await self.db.execute(
                    update(Build)
                    .where(Build.id == build_id)
                    .values(views_count=Build.views_count + 1)
                )
                await self.db.commit()
                return True
            except Exception:
                await self.db.rollback()
                return False
    
    async def count(self) -> int:
        """Получить общее количество сборок"""
        result = await self.db.execute(select(func.count(Build.id)))
        return result.scalar() or 0
    
    async def count_by_author(self, author_id: int) -> int:
        """Получить количество сборок автора"""
        result = await self.db.execute(
            select(func.count(Build.id)).filter(Build.author_id == author_id)
        )
        return result.scalar() or 0
    
    async def search(
        self,
        query: str = "",
        author_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 20,
        sort_by: str = "created_at",
        order: str = "desc"
    ) -> List[Build]:
        """Поиск сборок с фильтрами и сортировкой
        
        Args:
            query: Поисковый запрос по названию или описанию
            author_id: ID автора для фильтрации
            skip: Количество пропускаемых записей
            limit: Максимальное количество записей
            sort_by: Поле для сортировки (created_at, views_count, average_rating, title)
            order: Порядок сортировки (asc или desc)
        """
        stmt = select(Build).options(
            selectinload(Build.author),
            selectinload(Build.ratings),
            selectinload(Build.components)
        )
        
        conditions = []
        
        # Поиск по названию или описанию
        if query:
            search_condition = or_(
                Build.title.ilike(f"%{query}%"),
                Build.description.ilike(f"%{query}%")
            )
            conditions.append(search_condition)
        
        # Фильтр по автору
        if author_id is not None:
            conditions.append(Build.author_id == author_id)
        
        # Применяем условия
        if conditions:
            stmt = stmt.filter(and_(*conditions))
        
        # Сортировка
        sort_column = Build.created_at  # по умолчанию
        
        if sort_by == "views_count":
            sort_column = Build.views_count
        elif sort_by == "average_rating":
            # Для сортировки по рейтингу используем вычисляемое поле
            sort_column = Build.average_rating
        elif sort_by == "title":
            sort_column = Build.title
        elif sort_by == "created_at":
            sort_column = Build.created_at
        
        # Применяем порядок сортировки
        if order.lower() == "asc":
            stmt = stmt.order_by(sort_column.asc())
        else:
            stmt = stmt.order_by(sort_column.desc())
        
        # Пагинация
        stmt = stmt.offset(skip).limit(limit)
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def count_search_results(
        self,
        query: str = "",
        author_id: Optional[int] = None
    ) -> int:
        """Подсчет результатов поиска"""
        stmt = select(func.count(Build.id))
        
        conditions = []
        
        if query:
            search_condition = or_(
                Build.title.ilike(f"%{query}%"),
                Build.description.ilike(f"%{query}%")
            )
            conditions.append(search_condition)
        
        if author_id is not None:
            conditions.append(Build.author_id == author_id)
        
        if conditions:
            stmt = stmt.filter(and_(*conditions))
        
        result = await self.db.execute(stmt)
        return result.scalar() or 0
    
    async def get_top_builds(self, limit: int = 10) -> List[Build]:
        """Получить топ сборок по рейтингу"""
        # Подзапрос для вычисления среднего рейтинга
        avg_rating_subq = (
            select(
                BuildRating.build_id,
                func.avg(BuildRating.score).label('avg_rating'),
                func.count(BuildRating.id).label('ratings_count')
            )
            .group_by(BuildRating.build_id)
            .subquery()
        )
        
        # Основной запрос с сортировкой по рейтингу
        stmt = (
            select(Build)
            .options(
                selectinload(Build.author),
                selectinload(Build.ratings),
                selectinload(Build.components)
            )
            .join(avg_rating_subq, Build.id == avg_rating_subq.c.build_id)
            .filter(avg_rating_subq.c.ratings_count >= 1)  # Минимум 1 оценка
            .order_by(
                desc(avg_rating_subq.c.avg_rating),
                desc(avg_rating_subq.c.ratings_count),
                desc(Build.created_at)
            )
            .limit(limit)
        )
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    # === Методы для BuildRating ===
    
    async def get_rating_by_id(self, rating_id: int) -> Optional[BuildRating]:
        """Получить оценку по ID"""
        result = await self.db.execute(
            select(BuildRating).filter(BuildRating.id == rating_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_rating(self, build_id: int, user_id: int) -> Optional[BuildRating]:
        """Получить оценку пользователя для конкретной сборки"""
        result = await self.db.execute(
            select(BuildRating).filter(
                BuildRating.build_id == build_id,
                BuildRating.user_id == user_id
            )
        )
        return result.scalar_one_or_none()
    
    async def create_rating(self, build_id: int, user_id: int, rating_data: BuildRatingCreate) -> BuildRating:
        """Создать оценку"""
        db_rating = BuildRating(
            build_id=build_id,
            user_id=user_id,
            score=rating_data.score
        )
        self.db.add(db_rating)
        await self.db.commit()
        await self.db.refresh(db_rating)
        return db_rating
    
    async def update_rating(self, rating: BuildRating, score: int) -> BuildRating:
        """Обновить оценку"""
        rating.score = score
        await self.db.commit()
        await self.db.refresh(rating)
        return rating
    
    async def delete_rating(self, rating: BuildRating) -> bool:
        """Удалить оценку"""
        try:
            await self.db.delete(rating)
            await self.db.commit()
            return True
        except Exception:
            await self.db.rollback()
            return False
    
    async def get_build_ratings(self, build_id: int) -> List[BuildRating]:
        """Получить все оценки для сборки"""
        result = await self.db.execute(
            select(BuildRating).filter(BuildRating.build_id == build_id)
        )
        return list(result.scalars().all())
    
    # === Методы для BuildComment ===
    
    async def get_comment_by_id(self, comment_id: int) -> Optional[BuildComment]:
        """Получить комментарий по ID (с максимум 1 уровнем replies)"""
        result = await self.db.execute(
            select(BuildComment)
            .options(
                selectinload(BuildComment.user),
                selectinload(BuildComment.replies).selectinload(BuildComment.user)
            )
            .filter(BuildComment.id == comment_id)
        )
        return result.scalar_one_or_none()
    
    async def get_build_comments(
        self,
        build_id: int,
        skip: int = 0,
        limit: int = 50
    ) -> List[BuildComment]:
        """Получить комментарии для сборки (только корневые + первый уровень ответов, максимум 2 уровня)"""
        result = await self.db.execute(
            select(BuildComment)
            .options(
                selectinload(BuildComment.user),
                selectinload(BuildComment.replies)
                .selectinload(BuildComment.user)
            )
            .filter(
                BuildComment.build_id == build_id,
                BuildComment.parent_id == None
            )
            .order_by(desc(BuildComment.created_at))
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def count_build_comments(self, build_id: int) -> int:
        """Получить количество комментариев для сборки"""
        result = await self.db.execute(
            select(func.count(BuildComment.id)).filter(BuildComment.build_id == build_id)
        )
        return result.scalar() or 0
    
    async def create_comment(
        self,
        build_id: int,
        user_id: int,
        comment_data: BuildCommentCreate
    ) -> BuildComment:
        """Создать комментарий"""
        db_comment = BuildComment(
            build_id=build_id,
            user_id=user_id,
            content=comment_data.content,
            parent_id=comment_data.parent_id
        )
        self.db.add(db_comment)
        await self.db.commit()
        await self.db.refresh(db_comment)
        
        # Загружаем связанные данные
        return await self.get_comment_by_id(db_comment.id)
    
    async def update_comment(self, comment: BuildComment, content: str) -> BuildComment:
        """Обновить комментарий"""
        comment.content = content
        await self.db.commit()
        await self.db.refresh(comment)
        return await self.get_comment_by_id(comment.id)
    
    async def delete_comment(self, comment: BuildComment) -> bool:
        """Удалить комментарий"""
        try:
            await self.db.delete(comment)
            await self.db.commit()
            return True
        except Exception:
            await self.db.rollback()
            return False
    
    # === Статистика ===
    
    async def get_stats(self) -> dict:
        """Получить общую статистику по сборкам"""
        total_builds = await self.count()
        
        # Общее количество оценок
        ratings_result = await self.db.execute(select(func.count(BuildRating.id)))
        total_ratings = ratings_result.scalar() or 0
        
        # Общее количество комментариев
        comments_result = await self.db.execute(select(func.count(BuildComment.id)))
        total_comments = comments_result.scalar() or 0
        
        # Средний рейтинг по всем сборкам
        avg_rating_result = await self.db.execute(select(func.avg(BuildRating.score)))
        average_rating = avg_rating_result.scalar() or 0.0
        
        return {
            "total_builds": total_builds,
            "total_ratings": total_ratings,
            "total_comments": total_comments,
            "average_rating": float(average_rating)
        }
    
    async def get_unique_components(self) -> dict:
        """Получить список доступных компонентов, сгруппированных по категориям"""
        from app.models.component import ComponentCategory
        from app.schemas.component import ComponentResponse
        
        # Получаем все компоненты, сгруппированные по категориям
        result = await self.db.execute(
            select(Component).order_by(Component.category, Component.name)
        )
        components = list(result.scalars().all())
        
        # Группируем по категориям
        components_by_category: dict[str, list] = {}
        for component in components:
            category_name = component.category.value
            if category_name not in components_by_category:
                components_by_category[category_name] = []
            components_by_category[category_name].append(ComponentResponse.model_validate(component))
        
        return {"components_by_category": components_by_category}


