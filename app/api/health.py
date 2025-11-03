"""
Эндпоинты для проверки состояния приложения
"""
from fastapi import APIRouter

router = APIRouter(prefix="/api")


@router.get("/")
async def root():
    """Корневой эндпоинт"""
    return {"message": "Komputer.ok API"}


@router.get("/health")
async def health_check():
    """Проверка состояния приложения"""
    return {"status": "healthy"}
