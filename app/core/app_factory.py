"""
Фабрика для создания FastAPI приложения
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

    # Подключение роутеров
    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(chat.router)
    app.include_router(feedback.router)
    app.include_router(builds.router)
    app.include_router(components.router)
    app.include_router(balance.router)

    return app
