"""
Фабрика для создания FastAPI приложения
"""

from fastapi import FastAPI

from app.core.lifespan import lifespan
from app.core.middleware import setup_all_middleware
from app.core.exception_handlers import (
    domain_exception_handler,
    general_exception_handler,
)
from app.routers import auth, users, chat, feedback, builds, components, balance
from app.exceptions.base import BaseAppException


def create_app() -> FastAPI:
    """Создание и настройка FastAPI приложения"""

    app = FastAPI(
        title="Komputer.ok API",
        description="API для сайта Komputer.ok",
        version="1.0.0",
        lifespan=lifespan,
    )

    # Настройка middleware
    setup_all_middleware(app)

    # Подключение роутеров с общим префиксом /api
    app.include_router(auth.router, prefix="/api")
    app.include_router(users.router, prefix="/api")
    app.include_router(chat.router, prefix="/api")
    app.include_router(feedback.router, prefix="/api")
    app.include_router(builds.router, prefix="/api")
    app.include_router(components.router, prefix="/api")
    app.include_router(balance.router, prefix="/api")

    # Регистрация обработчиков исключений
    app.add_exception_handler(BaseAppException, domain_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    return app
