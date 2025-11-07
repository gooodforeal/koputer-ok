"""
Фабрика для создания FastAPI приложения
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.core.lifespan import lifespan
from app.routers import auth, users, chat, feedback, builds, components, balance


def create_app() -> FastAPI:
    """Создание и настройка FastAPI приложения"""
    
    app = FastAPI(
        title="Komputer.ok API",
        description="API для сайта Komputer.ok",
        version="1.0.0",
        lifespan=lifespan
    )

    # Настройка CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",  # React dev server
            "http://127.0.0.1:3000",  # Alternative localhost
            "http://localhost:5173",  # Vite dev server (если используется)
            "http://127.0.0.1:5173",  # Alternative Vite localhost
            "http://frontend:3000",   # Docker контейнер фронтенда
            "http://oauth_frontend:3000",  # Docker контейнер фронтенда (имя контейнера)
        ],
        allow_credentials=True,  # Включаем credentials для авторизации
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Настройка Prometheus middleware
    instrumentator = Instrumentator()
    instrumentator.instrument(app).expose(app, endpoint="/metrics")

    # Подключение роутеров с общим префиксом /api
    app.include_router(auth.router, prefix="/api")
    app.include_router(users.router, prefix="/api")
    app.include_router(chat.router, prefix="/api")
    app.include_router(feedback.router, prefix="/api")
    app.include_router(builds.router, prefix="/api")
    app.include_router(components.router, prefix="/api")
    app.include_router(balance.router, prefix="/api")

    return app
