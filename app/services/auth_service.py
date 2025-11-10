"""
Сервис для авторизации пользователей
"""
from datetime import timedelta, datetime
from typing import Optional
import logging
import httpx
from fastapi import HTTPException, status
from fastapi.responses import RedirectResponse
from app.repositories import UserRepository
from app.schemas.user import UserCreate
from app.schemas.auth import (
    GoogleAuthResponse,
    GoogleUserInfo,
    TelegramAuthInitResponse,
    TelegramAuthorizeRequest,
    TelegramAuthorizeResponse,
    TelegramAuthCheckResponse
)
from app.auth import create_access_token
from app.config import settings
from app.services.auth_tokens import AuthTokenStorage
from app.services.email_publisher import EmailPublisher

logger = logging.getLogger(__name__)


class AuthService:
    """Сервис для авторизации пользователей"""
    
    def __init__(
        self,
        user_repo: UserRepository,
        auth_token_storage: AuthTokenStorage,
        email_publisher: EmailPublisher
    ):
        self.user_repo = user_repo
        self.auth_token_storage = auth_token_storage
        self.email_publisher = email_publisher
    
    async def _exchange_code_for_token(self, code: str) -> str:
        """
        Обменивает код авторизации на access token
        
        Args:
            code: Код авторизации от Google
            
        Returns:
            str: Access token
            
        Raises:
            HTTPException: Если не удалось обменять код на токен
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    "https://oauth2.googleapis.com/token",
                    data={
                        "client_id": settings.google_client_id,
                        "client_secret": settings.google_client_secret,
                        "code": code,
                        "grant_type": "authorization_code",
                        "redirect_uri": settings.google_redirect_uri,
                    }
                )
                response.raise_for_status()
                token_data = response.json()
                return token_data["access_token"]
            except httpx.HTTPStatusError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to exchange code for token: {e.response.text}"
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error exchanging code for token: {str(e)}"
                )
    
    async def _get_google_user_info(self, access_token: str) -> GoogleUserInfo:
        """
        Получает информацию о пользователе от Google API
        
        Args:
            access_token: Access token от Google
            
        Returns:
            GoogleUserInfo: Информация о пользователе
            
        Raises:
            HTTPException: Если не удалось получить информацию о пользователе
        """
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    "https://www.googleapis.com/oauth2/v2/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                response.raise_for_status()
                user_info = response.json()
                
                return GoogleUserInfo(
                    id=user_info["id"],
                    email=user_info["email"],
                    name=user_info["name"],
                    picture=user_info.get("picture"),
                    verified_email=user_info.get("verified_email", False)
                )
            except httpx.HTTPStatusError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to get user info from Google: {e.response.text}"
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error getting user info: {str(e)}"
                )
    
    async def get_google_auth_url(self) -> GoogleAuthResponse:
        """
        Получить URL для авторизации через Google
        
        Returns:
            GoogleAuthResponse с URL для авторизации
        """
        google_auth_url = (
            f"https://accounts.google.com/o/oauth2/v2/auth?"
            f"client_id={settings.google_client_id}&"
            f"redirect_uri={settings.google_redirect_uri}&"
            f"scope=openid email profile&"
            f"response_type=code&"
            f"access_type=offline&"
            f"prompt=select_account"
        )
        return GoogleAuthResponse(auth_url=google_auth_url)
    
    async def handle_google_callback(self, code: str) -> RedirectResponse:
        """
        Обработать callback от Google OAuth2
        
        Args:
            code: Код авторизации от Google
            
        Returns:
            RedirectResponse с перенаправлением на фронтенд
        """
        try:
            # Обмениваем код на access token
            access_token = await self._exchange_code_for_token(code)
            
            # Получаем информацию о пользователе
            google_user_info = await self._get_google_user_info(access_token)
            
            # Создаем или обновляем пользователя
            user_create = UserCreate(
                email=google_user_info.email,
                name=google_user_info.name,
                picture=google_user_info.picture,
                google_id=google_user_info.id
            )
            user = await self.user_repo.create_or_update(user_create)
            
            # Создаем JWT токен
            access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
            jwt_token = create_access_token(
                data={"sub": str(user.id), "email": user.email},
                expires_delta=access_token_expires
            )
            
            # Отправляем email при входе (если email указан)
            if user.email:
                try:
                    login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    await self.email_publisher.publish_login_email(
                        email=user.email,
                        user_name=user.name,
                        login_time=login_time
                    )
                except Exception as e:
                    # Логируем ошибку, но не прерываем процесс входа
                    logger.error(f"Ошибка при отправке email при входе: {str(e)}")
            
            # Перенаправляем на фронтенд с токеном
            frontend_url = f"{settings.frontend_url}/auth/callback?token={jwt_token}"
            return RedirectResponse(url=frontend_url)
            
        except Exception as e:
            # В случае ошибки перенаправляем на фронтенд с ошибкой
            error_url = f"{settings.frontend_url}/auth/error?message={str(e)}"
            return RedirectResponse(url=error_url)
    
    async def init_telegram_auth(self) -> TelegramAuthInitResponse:
        """
        Инициировать авторизацию через Telegram бот
        Создает временный токен и возвращает ссылку на бота
        
        Returns:
            TelegramAuthInitResponse с данными для авторизации
        """
        # Создаем временный токен авторизации (действует 5 минут)
        auth_token = await self.auth_token_storage.create_token(expires_in=300)
        
        # Формируем deep link на бота с токеном
        bot_url = f"https://t.me/{settings.telegram_bot_username}?start={auth_token}"
        
        return TelegramAuthInitResponse(
            auth_token=auth_token,
            bot_url=bot_url,
            bot_username=settings.telegram_bot_username,
            expires_in=300  # секунд
        )
    
    async def authorize_telegram_user(
        self,
        request: TelegramAuthorizeRequest
    ) -> TelegramAuthorizeResponse:
        """
        Обработать авторизацию пользователя через Telegram бот
        Вызывается ботом после того, как пользователь нажал /start с токеном
        
        Args:
            request: Данные запроса на авторизацию
            
        Returns:
            TelegramAuthorizeResponse с результатом авторизации
        """
        logger.info(f"Обработка авторизации через Telegram для пользователя {request.telegram_id} с токеном {request.auth_token[:10]}...")
        
        # Проверяем и получаем данные токена
        token_data = await self.auth_token_storage.get_token_data(request.auth_token)
        
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
        success = await self.auth_token_storage.link_telegram_user(
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
        
        db_user = await self.user_repo.create_or_update_telegram(user_create)
        logger.info(f"Пользователь создан/обновлен в БД: {db_user.id}")
        
        # Создаем JWT токен
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        jwt_token = create_access_token(
            data={"sub": str(db_user.id), "telegram_id": str(db_user.telegram_id)},
            expires_delta=access_token_expires
        )
        
        # Сохраняем JWT токен в хранилище
        token_updated = await self.auth_token_storage.update_token_data(request.auth_token, jwt_token=jwt_token)
        logger.info(f"JWT токен сохранен для токена {request.auth_token[:10]}...: {token_updated}")
        
        if not token_updated:
            logger.error(f"Не удалось сохранить JWT токен для токена {request.auth_token[:10]}...")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save JWT token"
            )
        
        # Отправляем email при входе (если email указан)
        if db_user.email:
            try:
                login_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                await self.email_publisher.publish_login_email(
                    email=db_user.email,
                    user_name=db_user.name,
                    login_time=login_time
                )
            except Exception as e:
                # Логируем ошибку, но не прерываем процесс входа
                logger.error(f"Ошибка при отправке email при входе: {str(e)}")
        
        return TelegramAuthorizeResponse(
            status="success",
            message="Authorization completed"
        )
    
    async def check_telegram_auth(self, auth_token: str) -> TelegramAuthCheckResponse:
        """
        Проверить статус авторизации по токену
        Используется для polling на клиенте
        
        Args:
            auth_token: Токен авторизации
            
        Returns:
            TelegramAuthCheckResponse с результатом проверки
        """
        logger.debug(f"Проверка токена {auth_token[:10]}...")
        token_data = await self.auth_token_storage.get_token_data(auth_token)
        
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
                await self.auth_token_storage.invalidate_token(auth_token)
                return TelegramAuthCheckResponse(
                    status="completed",
                    access_token=jwt_token,
                    telegram_id=str(telegram_id),
                    username=token_data.get("username"),
                    first_name=token_data.get("first_name", ""),
                    last_name=token_data.get("last_name")
                )
            else:
                logger.warning(f"Токен {auth_token[:10]}... используется, но JWT токен отсутствует!")
                logger.warning(f"Данные токена: {token_data}")
                return TelegramAuthCheckResponse(status="pending")
        
        return TelegramAuthCheckResponse(status="pending")

