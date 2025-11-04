from fastapi import APIRouter, Depends, Query
from fastapi.responses import RedirectResponse
from app.schemas.auth import (
    LogoutResponse,
    TelegramAuthorizeRequest,
    TelegramAuthorizeResponse,
    TelegramAuthCheckResponse
)
from app.schemas.user import UserResponse
from app.models.user import User
from app.dependencies import get_current_user
from app.dependencies.repositories import get_auth_service
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.get("/google")
async def google_auth(
    auth_service: AuthService = Depends(get_auth_service)
):
    """Инициация OAuth2 авторизации через Google"""
    return await auth_service.get_google_auth_url()


@router.get("/google/callback")
async def google_callback(
    code: str = Query(..., description="Authorization code from Google"),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Обработка callback от Google OAuth2"""
    return await auth_service.handle_google_callback(code)


@router.get("/telegram/init")
async def telegram_auth_init(
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Инициация авторизации через Telegram бот
    Создает временный токен и возвращает ссылку на бота
    """
    return await auth_service.init_telegram_auth()


@router.post("/telegram/authorize", response_model=TelegramAuthorizeResponse)
async def telegram_authorize(
    request: TelegramAuthorizeRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Обработка авторизации пользователя через Telegram бот
    Вызывается ботом после того, как пользователь нажал /start с токеном
    """
    return await auth_service.authorize_telegram_user(request)


@router.get("/telegram/check/{auth_token}", response_model=TelegramAuthCheckResponse)
async def telegram_auth_check(
    auth_token: str,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Проверка статуса авторизации по токену
    Используется для polling на клиенте
    """
    return await auth_service.check_telegram_auth(auth_token)


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Получение информации о текущем пользователе"""
    return current_user


@router.post("/logout", response_model=LogoutResponse)
async def logout():
    """Выход из системы (на клиенте нужно удалить токен)"""
    return LogoutResponse(message="Successfully logged out")
