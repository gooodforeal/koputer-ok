from pydantic import BaseModel
from typing import Optional
from .user import UserResponse


class Token(BaseModel):
    """Схема для JWT токена"""
    access_token: str
    token_type: str
    user: UserResponse


class GoogleUserInfo(BaseModel):
    """Схема для информации о пользователе от Google"""
    id: str
    email: str
    name: str
    picture: Optional[str] = None
    verified_email: bool


class LoginResponse(BaseModel):
    """Схема для ответа при успешном входе"""
    message: str
    user: UserResponse
    access_token: str


class LogoutResponse(BaseModel):
    """Схема для ответа при выходе"""
    message: str


class TelegramAuthorizeRequest(BaseModel):
    """Схема для запроса авторизации через Telegram"""
    auth_token: str
    telegram_id: str
    username: Optional[str] = None
    first_name: str = ""
    last_name: Optional[str] = None
    photo_url: Optional[str] = None


class TelegramAuthorizeResponse(BaseModel):
    """Схема для ответа при авторизации через Telegram"""
    status: str
    message: str


class GoogleAuthResponse(BaseModel):
    """Схема для ответа при инициации OAuth2 авторизации через Google"""
    auth_url: str


class TelegramAuthInitResponse(BaseModel):
    """Схема для ответа при инициации авторизации через Telegram"""
    auth_token: str
    bot_url: str
    bot_username: str
    expires_in: int


class TelegramAuthCheckResponse(BaseModel):
    """Схема для ответа при проверке статуса авторизации через Telegram"""
    status: str
    access_token: Optional[str] = None
    telegram_id: Optional[str] = None
    username: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None






