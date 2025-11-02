"""
Сервис для парсинга компонентов в фоновом режиме
Парсинг выполняется асинхронно с использованием aiohttp и BeautifulSoup
"""
import asyncio
import logging
from typing import Dict, Optional
from app.services.shop_parser import ShopParser, ComponentsCategory
from app.models.component import ComponentCategory
from app.repositories.component_repository import ComponentRepository
from app.services.redis_service import redis_service
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.config import settings

logger = logging.getLogger(__name__)

# Ключ для хранения статуса парсинга в Redis
PARSE_STATUS_KEY = "component_parser:status"
PARSE_STATUS_TIMESTAMP_KEY = "component_parser:status:timestamp"
PARSE_STOP_REQUESTED_KEY = "component_parser:stop_requested"

# Таймаут для парсинга одной категории (в секундах)
# Если парсинг категории занимает больше этого времени, он будет прерван
CATEGORY_PARSE_TIMEOUT = 600  # 10 минут на категорию

# Максимальное время для парсинга без обновления статуса (в секундах)
# Если статус не обновлялся больше этого времени, считаем парсинг зависшим
MAX_PARSE_IDLE_TIME = 1800  # 30 минут


class ComponentParserService:
    """Сервис для парсинга компонентов
    
    Парсинг выполняется асинхронно с использованием aiohttp и BeautifulSoup.
    """
    
    def __init__(self):
        self._parsing_task: Optional[asyncio.Task] = None
        self._parser: Optional[ShopParser] = None
    
    async def start_parsing(self, component_repo: ComponentRepository, clear_existing: bool = True) -> None:
        """
        Запустить парсинг всех категорий в фоновом режиме
        
        Args:
            component_repo: Репозиторий компонентов
            clear_existing: Очистить существующие данные перед парсингом
        """
        # Проверяем, не запущен ли уже парсинг
        status = await self.get_status()
        if status.get("is_running", False):
            logger.warning("Парсинг уже запущен")
            return
        
        # Запускаем асинхронный парсинг в фоновом режиме
        self._parsing_task = asyncio.create_task(
            self._parse_all_categories(component_repo, clear_existing)
        )
    
    async def _parse_all_categories(
        self, 
        component_repo: ComponentRepository, 
        clear_existing: bool = True
    ) -> None:
        """Парсинг всех категорий"""
        categories = list(ComponentsCategory)
        total_categories = len(categories)
        processed_categories = 0
        processed_products = 0
        errors = []
        
        try:
            # Инициализируем статус
            await redis_service.set(PARSE_STATUS_KEY, {
                "is_running": True,
                "current_category": None,
                "processed_categories": 0,
                "total_categories": total_categories,
                "processed_products": 0,
                "errors": []
            })
            # Устанавливаем timestamp начала парсинга
            await redis_service.set(PARSE_STATUS_TIMESTAMP_KEY, asyncio.get_event_loop().time())
            
            if clear_existing:
                logger.info("Очищаем существующие компоненты")
                deleted_count = await component_repo.delete_all()
                logger.info(f"Удалено компонентов: {deleted_count}")
            
            # Создаем отдельную сессию БД для парсинга
            database_url = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
            engine = create_async_engine(database_url, echo=False)
            async_session = async_sessionmaker(engine, expire_on_commit=False)
            
            try:
                # Инициализируем парсер один раз для всех категорий
                self._parser = ShopParser(use_cache=True)
                
                # Парсим каждую категорию
                for category in categories:
                    # Проверяем флаг остановки перед каждой категорией
                    stop_requested = await redis_service.get(PARSE_STOP_REQUESTED_KEY)
                    if stop_requested:
                        logger.info("Получен запрос на остановку парсинга")
                        await redis_service.delete(PARSE_STOP_REQUESTED_KEY)
                        errors.append("Парсинг остановлен пользователем")
                        # Обновляем статус перед выходом
                        await redis_service.set(PARSE_STATUS_KEY, {
                            "is_running": False,
                            "current_category": None,
                            "processed_categories": processed_categories,
                            "total_categories": total_categories,
                            "processed_products": processed_products,
                            "errors": errors
                        })
                        await redis_service.delete(PARSE_STATUS_TIMESTAMP_KEY)
                        logger.info(f"Парсинг остановлен пользователем. Обработано категорий: {processed_categories}/{total_categories}, товаров: {processed_products}")
                        # Закрываем парсер при остановке
                        if self._parser:
                            await self._parser.close()
                            self._parser = None
                        break
                    
                    try:
                        # Обновляем статус
                        await redis_service.set(PARSE_STATUS_KEY, {
                            "is_running": True,
                            "current_category": category.display_name,
                            "processed_categories": processed_categories,
                            "total_categories": total_categories,
                            "processed_products": processed_products,
                            "errors": errors
                        })
                        logger.info(f"Парсинг категории: {category.display_name}")
                        
                        # Обновляем timestamp статуса перед началом парсинга
                        await redis_service.set(PARSE_STATUS_TIMESTAMP_KEY, asyncio.get_event_loop().time())
                        
                        # Запускаем асинхронный парсинг с таймаутом
                        try:
                            products = await asyncio.wait_for(
                                self._parser.get_category(category),
                                timeout=CATEGORY_PARSE_TIMEOUT
                            )
                            logger.info(f"Получено {len(products)} товаров из категории {category.display_name}")
                        except asyncio.TimeoutError:
                            error_msg = f"Таймаут парсинга категории {category.display_name} (превышен лимит {CATEGORY_PARSE_TIMEOUT} секунд)"
                            logger.error(error_msg)
                            errors.append(error_msg)
                            products = []  # Продолжаем со следующей категорией
                        
                        # Сохраняем товары в базу асинхронно
                        async with async_session() as session:
                            parse_repo = ComponentRepository(session)
                            category_enum = self._map_category(category)
                            for product in products:
                                try:
                                    await parse_repo.create_or_update(
                                        name=product.get("name", ""),
                                        link=product.get("link", ""),
                                        price=product.get("price"),
                                        image=product.get("image"),
                                        category=category_enum
                                    )
                                    processed_products += 1
                                except Exception as e:
                                    error_msg = f"Ошибка при сохранении товара '{product.get('name', 'unknown')}': {str(e)}"
                                    logger.error(error_msg)
                                    errors.append(error_msg)
                        
                        processed_categories += 1
                        # Обновляем timestamp после обработки категории
                        await redis_service.set(PARSE_STATUS_TIMESTAMP_KEY, asyncio.get_event_loop().time())
                        logger.info(f"Обработано товаров из категории {category.display_name}: {len(products)}")
                        
                    except Exception as e:
                        error_msg = f"Ошибка при парсинге категории {category.display_name}: {str(e)}"
                        logger.error(error_msg)
                        errors.append(error_msg)
                        processed_categories += 1
                
                # Финальный статус
                await redis_service.set(PARSE_STATUS_KEY, {
                    "is_running": False,
                    "current_category": None,
                    "processed_categories": processed_categories,
                    "total_categories": total_categories,
                    "processed_products": processed_products,
                    "errors": errors
                })
                # Удаляем timestamp
                await redis_service.delete(PARSE_STATUS_TIMESTAMP_KEY)
                
                logger.info(f"Парсинг завершен. Обработано категорий: {processed_categories}/{total_categories}, товаров: {processed_products}")
                
            finally:
                await engine.dispose()
                # Закрываем парсер после завершения всех категорий
                if self._parser:
                    await self._parser.close()
                    self._parser = None
                
        except Exception as e:
            error_msg = f"Критическая ошибка при парсинге: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
            
            # Обновляем статус с ошибкой
            await redis_service.set(PARSE_STATUS_KEY, {
                "is_running": False,
                "current_category": None,
                "processed_categories": processed_categories,
                "total_categories": total_categories,
                "processed_products": processed_products,
                "errors": errors
            })
            # Удаляем timestamp
            await redis_service.delete(PARSE_STATUS_TIMESTAMP_KEY)
            # Закрываем парсер при ошибке
            if self._parser:
                await self._parser.close()
                self._parser = None
    
    def _map_category(self, category: ComponentsCategory) -> ComponentCategory:
        """Маппинг категории в ComponentCategory"""
        mapping = {
            ComponentsCategory.PROCESSORY: ComponentCategory.PROCESSORY,
            ComponentsCategory.MATERINSKIE_PLATY: ComponentCategory.MATERINSKIE_PLATY,
            ComponentsCategory.VIDEOKARTY: ComponentCategory.VIDEOKARTY,
            ComponentsCategory.OPERATIVNAYA_PAMYAT: ComponentCategory.OPERATIVNAYA_PAMYAT,
            ComponentsCategory.KORPUSA: ComponentCategory.KORPUSA,
            ComponentsCategory.BLOKI_PITANIYA: ComponentCategory.BLOKI_PITANIYA,
            ComponentsCategory.ZHESTKIE_DISKI: ComponentCategory.ZHESTKIE_DISKI,
            ComponentsCategory.OHLAZHDENIE: ComponentCategory.OHLAZHDENIE,
            ComponentsCategory.SSD_NAKOPITELI: ComponentCategory.SSD_NAKOPITELI,
        }
        return mapping.get(category, ComponentCategory.PROCESSORY)
    
    async def get_status(self) -> Dict:
        """Получить текущий статус парсинга"""
        status = await redis_service.get(PARSE_STATUS_KEY)
        if status is None:
            return {
                "is_running": False,
                "current_category": None,
                "processed_categories": 0,
                "total_categories": 0,
                "processed_products": 0,
                "errors": []
            }
        
        # Проверяем флаг остановки - если установлен, сразу обновляем статус
        stop_requested = await redis_service.get(PARSE_STOP_REQUESTED_KEY)
        if stop_requested and status.get("is_running", False):
            logger.info("Обнаружен флаг остановки парсинга при получении статуса")
            status["is_running"] = False
            status["current_category"] = None
            if "errors" not in status:
                status["errors"] = []
            if "Парсинг остановлен пользователем" not in status["errors"]:
                status["errors"].append("Парсинг остановлен пользователем")
            await redis_service.set(PARSE_STATUS_KEY, status)
            await redis_service.delete(PARSE_STATUS_TIMESTAMP_KEY)
        
        # Проверяем, не завис ли парсинг
        # Если статус показывает, что парсинг запущен, но timestamp не обновлялся слишком долго,
        # считаем парсинг зависшим и сбрасываем статус
        if status.get("is_running", False):
            timestamp = await redis_service.get(PARSE_STATUS_TIMESTAMP_KEY)
            if timestamp:
                current_time = asyncio.get_event_loop().time()
                idle_time = current_time - timestamp
                
                if idle_time > MAX_PARSE_IDLE_TIME:
                    logger.warning(f"Обнаружен зависший парсинг (idle_time={idle_time:.1f}с). Сбрасываем статус.")
                    # Сбрасываем статус
                    status["is_running"] = False
                    if "errors" not in status:
                        status["errors"] = []
                    status["errors"].append(f"Парсинг завис и был автоматически остановлен (не обновлялся {int(idle_time)} секунд)")
                    await redis_service.set(PARSE_STATUS_KEY, status)
                    await redis_service.delete(PARSE_STATUS_TIMESTAMP_KEY)
        
        return status
    
    async def stop_parsing(self) -> bool:
        """
        Остановить парсинг
        
        Устанавливает флаг остановки в Redis и немедленно обновляет статус,
        чтобы фронтенд сразу увидел изменение. Парсинг проверит этот флаг
        перед обработкой следующей категории и корректно завершится.
        
        Returns:
            bool: True если остановка запрошена, False если парсинг не запущен
        """
        status = await self.get_status()
        if not status.get("is_running", False):
            logger.warning("Попытка остановить парсинг, но парсинг не запущен")
            return False
        
        # Устанавливаем флаг остановки
        await redis_service.set(PARSE_STOP_REQUESTED_KEY, True)
        logger.info("Запрошена остановка парсинга")
        
        # Немедленно обновляем статус, чтобы фронтенд сразу увидел изменение
        # Сохраняем текущие данные о прогрессе
        status["is_running"] = False
        status["current_category"] = None
        if "Парсинг остановлен пользователем" not in status.get("errors", []):
            if "errors" not in status:
                status["errors"] = []
            status["errors"].append("Парсинг остановлен пользователем")
        
        await redis_service.set(PARSE_STATUS_KEY, status)
        await redis_service.delete(PARSE_STATUS_TIMESTAMP_KEY)
        logger.info(f"Статус парсинга обновлен: остановка запрошена. Прогресс: {status.get('processed_categories', 0)}/{status.get('total_categories', 0)} категорий, {status.get('processed_products', 0)} товаров")
        
        # Также пытаемся отменить asyncio.Task, если она еще выполняется
        if self._parsing_task and not self._parsing_task.done():
            self._parsing_task.cancel()
            try:
                await self._parsing_task
            except asyncio.CancelledError:
                logger.info("asyncio.Task отменена")
            except Exception as e:
                logger.warning(f"Ошибка при отмене asyncio.Task: {e}")
        
        return True


# Глобальный экземпляр сервиса
component_parser_service = ComponentParserService()

