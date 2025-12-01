"""
Middleware для FastAPI приложения
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator


def setup_cors_middleware(app: FastAPI) -> None:
    """
    Настройка CORS middleware для приложения

    Args:
        app: Экземпляр FastAPI приложения
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",  # React dev server
            "http://127.0.0.1:3000",  # Alternative localhost
            "http://localhost:5173",  # Vite dev server (если используется)
            "http://127.0.0.1:5173",  # Alternative Vite localhost
            "http://frontend:3000",  # Docker контейнер фронтенда
            "http://oauth_frontend:3000",  # Docker контейнер фронтенда (имя контейнера)
        ],
        allow_credentials=True,  # Включаем credentials для авторизации
        allow_methods=["*"],
        allow_headers=["*"],
    )


def setup_prometheus_middleware(app: FastAPI) -> None:
    """
    Настройка Prometheus middleware для мониторинга

    Args:
        app: Экземпляр FastAPI приложения
    """
    instrumentator = Instrumentator()
    instrumentator.instrument(app).expose(app, endpoint="/metrics")


def setup_all_middleware(app: FastAPI) -> None:
    """
    Настройка всех middleware для приложения

    Args:
        app: Экземпляр FastAPI приложения
    """
    setup_cors_middleware(app)
    setup_prometheus_middleware(app)
