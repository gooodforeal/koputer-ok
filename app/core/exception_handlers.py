"""
Обработчики исключений для FastAPI приложения
"""

import logging
import os
from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.exceptions.base import BaseAppException

logger = logging.getLogger(__name__)


async def domain_exception_handler(
    request: Request, exc: BaseAppException
) -> JSONResponse:
    """
    Обработчик доменных исключений.
    Преобразует доменные исключения в HTTP ответы с логированием.

    Args:
        request: Объект запроса FastAPI
        exc: Доменное исключение

    Returns:
        JSONResponse с деталями ошибки
    """
    # Логируем исключение с уровнем в зависимости от статус-кода
    if exc.status_code >= 500:
        logger.error(
            f"Server error: {exc.__class__.__name__} - {exc.message}",
            extra={
                "exception_type": exc.__class__.__name__,
                "status_code": exc.status_code,
                "detail": exc.detail,
                "path": str(request.url.path) if request else None,
                "method": request.method if request else None,
            },
            exc_info=True,
        )
    elif exc.status_code >= 400:
        logger.warning(
            f"Client error: {exc.__class__.__name__} - {exc.message}",
            extra={
                "exception_type": exc.__class__.__name__,
                "status_code": exc.status_code,
                "detail": exc.detail,
                "path": str(request.url.path) if request else None,
                "method": request.method if request else None,
            },
        )
    else:
        logger.info(
            f"Exception: {exc.__class__.__name__} - {exc.message}",
            extra={
                "exception_type": exc.__class__.__name__,
                "status_code": exc.status_code,
                "detail": exc.detail,
                "path": str(request.url.path) if request else None,
                "method": request.method if request else None,
            },
        )

    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Обработчик для всех остальных исключений, не являющихся доменными.
    Обрабатывает необработанные исключения с логированием.

    Args:
        request: Объект запроса FastAPI
        exc: Исключение

    Returns:
        JSONResponse с деталями ошибки
    """
    # Логируем необработанное исключение с полным traceback
    logger.error(
        f"Unhandled exception: {exc.__class__.__name__} - {str(exc)}",
        extra={
            "exception_type": exc.__class__.__name__,
            "exception_message": str(exc),
            "path": str(request.url.path) if request else None,
            "method": request.method if request else None,
            "query_params": dict(request.query_params)
            if request and hasattr(request, "query_params")
            else None,
        },
        exc_info=True,
    )

    # В продакшене не показываем детали исключения, только общее сообщение
    # В разработке можно показывать больше информации
    is_production = os.getenv("ENVIRONMENT", "development").lower() == "production"

    if is_production:
        detail = "Внутренняя ошибка сервера. Пожалуйста, обратитесь в поддержку."
    else:
        detail = f"Необработанное исключение: {exc.__class__.__name__}: {str(exc)}"

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": detail}
    )
