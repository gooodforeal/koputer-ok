"""
Точка входа в приложение
"""
from app.core.app_factory import create_app
from app.api.health import router as health_router

# Создание приложения
app = create_app()

# Подключение эндпоинтов состояния
app.include_router(health_router)
