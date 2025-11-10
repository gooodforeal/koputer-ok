from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from typing import List
from app.dependencies import (
    require_admin_or_super_admin,
    get_component_repository,
    get_component_parser_service
)
from app.repositories.component_repository import ComponentRepository
from app.schemas.component import ComponentResponse, ParseStatusResponse, ParseStartResponse
from app.models.user import User
from app.services.component_parser import ComponentParserService

router = APIRouter(prefix="/components", tags=["components"])


@router.post("/parse", response_model=ParseStartResponse)
async def start_parsing(
    background_tasks: BackgroundTasks,
    clear_existing: bool = Query(True, description="Очистить существующие данные перед парсингом"),
    current_user: User = Depends(require_admin_or_super_admin),
    component_repo: ComponentRepository = Depends(get_component_repository),
    component_parser_service: ComponentParserService = Depends(get_component_parser_service)
):
    """
    Запустить парсинг компонентов в фоновом режиме (только для администраторов)
    
    Парсинг выполняется асинхронно с использованием aiohttp и BeautifulSoup.
    Задача запускается немедленно и не блокирует ответ API.
    
    Args:
        background_tasks: FastAPI BackgroundTasks для запуска фоновых задач
        clear_existing: Очистить существующие данные перед парсингом
        current_user: Текущий пользователь
        component_repo: Репозиторий компонентов
        component_parser_service: Сервис парсинга компонентов
    """
    # Проверяем статус
    parse_status = await component_parser_service.get_status()
    if parse_status.get("is_running", False):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Парсинг уже запущен"
        )
    
    # Запускаем парсинг в фоновом режиме
    # start_parsing создает asyncio.Task внутри себя, которая выполняется в фоне
    # Не используем await, чтобы не блокировать ответ API
    background_tasks.add_task(
        component_parser_service.start_parsing,
        component_repo,
        clear_existing
    )
    
    return ParseStartResponse(
        message="Парсинг запущен в фоновом режиме",
        status="started"
    )


@router.get("/parse/status", response_model=ParseStatusResponse)
async def get_parse_status(
    current_user: User = Depends(require_admin_or_super_admin),
    component_parser_service: ComponentParserService = Depends(get_component_parser_service)
):
    """
    Получить статус парсинга (только для администраторов)
    
    Args:
        current_user: Текущий пользователь
        component_parser_service: Сервис парсинга компонентов
    """
    status_data = await component_parser_service.get_status()
    return ParseStatusResponse(**status_data)


@router.post("/parse/stop")
async def stop_parsing(
    current_user: User = Depends(require_admin_or_super_admin),
    component_parser_service: ComponentParserService = Depends(get_component_parser_service)
):
    """
    Остановить запущенный парсинг (только для администраторов)
    
    Args:
        current_user: Текущий пользователь
        component_parser_service: Сервис парсинга компонентов
    """
    stopped = await component_parser_service.stop_parsing()
    if not stopped:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Парсинг не запущен"
        )
    
    return {"message": "Запрошена остановка парсинга", "status": "stopping"}


@router.get("/", response_model=List[ComponentResponse])
async def get_components(
    skip: int = 0,
    limit: int = 100,
    component_repo: ComponentRepository = Depends(get_component_repository)
):
    """
    Получить список компонентов
    
    Args:
        skip: Количество записей для пропуска
        limit: Максимальное количество записей
        component_repo: Репозиторий компонентов
    """
    components = await component_repo.get_all(skip=skip, limit=limit)
    return components


@router.get("/stats")
async def get_component_stats(
    component_repo: ComponentRepository = Depends(get_component_repository)
):
    """
    Получить статистику компонентов
    
    Args:
        component_repo: Репозиторий компонентов
    """
    from app.models.component import ComponentCategory
    
    total = await component_repo.count()
    stats = {
        "total": total,
        "by_category": {}
    }
    
    for category in ComponentCategory:
        count = await component_repo.count_by_category(category)
        stats["by_category"][category.value] = count
    
    return stats


@router.get("/by-category", response_model=List[ComponentResponse])
async def get_components_by_category(
    category: str = Query(..., description="Категория компонента"),
    query: str = Query("", description="Поиск по названию"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    component_repo: ComponentRepository = Depends(get_component_repository)
):
    """
    Получить компоненты по категории с поиском по названию
    
    Args:
        category: Категория компонента (значение ComponentCategory)
        query: Поисковый запрос по названию
        skip: Количество записей для пропуска
        limit: Максимальное количество записей
        component_repo: Репозиторий компонентов
    """
    from app.models.component import ComponentCategory
    
    # Пытаемся найти категорию по значению
    try:
        component_category = ComponentCategory(category)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Неизвестная категория: {category}"
        )
    
    # Получаем компоненты по категории с поиском
    components = await component_repo.get_by_category_with_search(
        category=component_category,
        query=query,
        skip=skip,
        limit=limit
    )
    
    return [ComponentResponse.model_validate(c) for c in components]

