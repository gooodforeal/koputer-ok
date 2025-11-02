from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import RedirectResponse
from datetime import timedelta
from app.repositories import UserRepository
from app.schemas.user import UserCreate, UserResponse
from app.schemas.auth import LogoutResponse, TelegramAuthorizeRequest, TelegramAuthorizeResponse
from app.auth import create_access_token
from app.oauth import exchange_code_for_token, get_google_user_info
from app.config import settings
from app.models.user import User
from app.dependencies import get_current_user, get_user_repository

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.get("/google")
async def google_auth():
    """Инициация OAuth2 авторизации через Google"""
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={settings.google_client_id}&"
        f"redirect_uri={settings.google_redirect_uri}&"
        f"scope=openid email profile&"
        f"response_type=code&"
        f"access_type=offline&"
        f"prompt=select_account"
    )
    return {"auth_url": google_auth_url}


@router.get("/google/callback")
async def google_callback(
    code: str = Query(..., description="Authorization code from Google"),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Обработка callback от Google OAuth2"""
    try:
        # Обмениваем код на access token
        access_token = await exchange_code_for_token(code)
        
        # Получаем информацию о пользователе
        google_user_info = await get_google_user_info(access_token)
        
        # Создаем или обновляем пользователя
        user_create = UserCreate(
            email=google_user_info.email,
            name=google_user_info.name,
            picture=google_user_info.picture,
            google_id=google_user_info.id
        )
        user = await user_repo.create_or_update(user_create)
        
        # Создаем JWT токен
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        jwt_token = create_access_token(
            data={"sub": str(user.id), "email": user.email},
            expires_delta=access_token_expires
        )
        
        # Перенаправляем на фронтенд с токеном
        frontend_url = f"{settings.frontend_url}/auth/callback?token={jwt_token}"
        return RedirectResponse(url=frontend_url)
        
    except Exception as e:
        # В случае ошибки перенаправляем на фронтенд с ошибкой
        error_url = f"{settings.frontend_url}/auth/error?message={str(e)}"
        return RedirectResponse(url=error_url)


@router.get("/telegram/init")
async def telegram_auth_init():
    """
    Инициация авторизации через Telegram бот
    Создает временный токен и возвращает ссылку на бота
    """
    from app.services.auth_tokens import auth_token_storage
    
    # Создаем временный токен авторизации (действует 5 минут)
    auth_token = await auth_token_storage.create_token(expires_in=300)
    
    # Формируем deep link на бота с токеном
    bot_url = f"https://t.me/{settings.telegram_bot_username}?start={auth_token}"
    
    return {
        "auth_token": auth_token,
        "bot_url": bot_url,
        "bot_username": settings.telegram_bot_username,
        "expires_in": 300  # секунд
    }


@router.post("/telegram/authorize", response_model=TelegramAuthorizeResponse)
async def telegram_authorize(
    request: TelegramAuthorizeRequest,
    user_repo: UserRepository = Depends(get_user_repository)
):
    """
    Обработка авторизации пользователя через Telegram бот
    Вызывается ботом после того, как пользователь нажал /start с токеном
    """
    from app.services.auth_tokens import auth_token_storage
    import logging
    
    logger = logging.getLogger(__name__)
    
    logger.info(f"Обработка авторизации через Telegram для пользователя {request.telegram_id} с токеном {request.auth_token[:10]}...")
    
    # Проверяем и получаем данные токена
    token_data = await auth_token_storage.get_token_data(request.auth_token)
    
    if not token_data:
        logger.warning(f"Токен {request.auth_token[:10]}... не найден или истек")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found or expired"
        )
    
    # Проверяем, не использован ли уже токен
    if token_data.get('used', False):
        logger.warning(f"Токен {request.auth_token[:10]}... уже был использован")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token already used"
        )
    
    # Связываем токен с пользователем Telegram
    success = await auth_token_storage.link_telegram_user(
        token=request.auth_token,
        telegram_id=int(request.telegram_id),
        username=request.username,
        first_name=request.first_name,
        last_name=request.last_name,
        photo_url=request.photo_url
    )
    
    if not success:
        logger.warning(f"Не удалось связать токен {request.auth_token[:10]}... с пользователем {request.telegram_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to link token with user"
        )
    
    # Формируем полное имя
    full_name = request.first_name or "Пользователь"
    if request.last_name:
        full_name += f" {request.last_name}"
    
    # Создаем или обновляем пользователя в базе данных
    user_create = UserCreate(
        name=full_name,
        picture=request.photo_url,
        telegram_id=request.telegram_id,
        username=request.username
    )
    
    db_user = await user_repo.create_or_update_telegram(user_create)
    logger.info(f"Пользователь создан/обновлен в БД: {db_user.id}")
    
    # Создаем JWT токен
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    jwt_token = create_access_token(
        data={"sub": str(db_user.id), "telegram_id": str(db_user.telegram_id)},
        expires_delta=access_token_expires
    )
    
    # Сохраняем JWT токен в хранилище
    token_updated = await auth_token_storage.update_token_data(request.auth_token, jwt_token=jwt_token)
    logger.info(f"JWT токен сохранен для токена {request.auth_token[:10]}...: {token_updated}")
    
    if not token_updated:
        logger.error(f"Не удалось сохранить JWT токен для токена {request.auth_token[:10]}...")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save JWT token"
        )
    
    return TelegramAuthorizeResponse(
        status="success",
        message="Authorization completed"
    )


@router.get("/telegram/check/{auth_token}")
async def telegram_auth_check(auth_token: str):
    """
    Проверка статуса авторизации по токену
    Используется для polling на клиенте
    """
    from app.services.auth_tokens import auth_token_storage
    import logging
    
    logger = logging.getLogger(__name__)
    
    logger.debug(f"Проверка токена {auth_token[:10]}...")
    token_data = await auth_token_storage.get_token_data(auth_token)
    
    if not token_data:
        logger.warning(f"Токен {auth_token[:10]}... не найден или истек")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token not found or expired"
        )
    
    used = token_data.get('used', False)
    has_jwt = bool(token_data.get('jwt_token'))
    telegram_id = token_data.get('telegram_id')
    
    logger.info(f"Проверка токена {auth_token[:10]}...: used={used}, has_jwt={has_jwt}, telegram_id={telegram_id}")
    
    # Проверяем, был ли токен использован (пользователь авторизовался в боте)
    if used and telegram_id:
        # Инвалидируем токен после получения JWT (одноразовое использование)
        jwt_token = token_data.get("jwt_token")
        if jwt_token:
            logger.info(f"Возвращаем JWT токен для {auth_token[:10]}...")
            await auth_token_storage.invalidate_token(auth_token)
            return {
                "status": "completed",
                "access_token": jwt_token,
                "telegram_id": token_data["telegram_id"],
                "username": token_data.get("username"),
                "first_name": token_data.get("first_name", ""),
                "last_name": token_data.get("last_name")
            }
        else:
            logger.warning(f"Токен {auth_token[:10]}... используется, но JWT токен отсутствует!")
            logger.warning(f"Данные токена: {token_data}")
            return {
                "status": "pending"
            }
    
    return {
        "status": "pending"
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Получение информации о текущем пользователе"""
    return current_user


@router.post("/logout", response_model=LogoutResponse)
async def logout():
    """Выход из системы (на клиенте нужно удалить токен)"""
    return LogoutResponse(message="Successfully logged out")
