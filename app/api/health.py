"""
Эндпоинты для проверки состояния приложения
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def root():
    """Корневой эндпоинт"""
    return {"message": "OAuth2 Google Authentication API"}


@router.get("/health")
async def health_check():
    """Проверка состояния приложения"""
    return {"status": "healthy"}
