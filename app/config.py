from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str

    postgres_host: str
    postgres_port: int
    postgres_user: str
    postgres_password: str
    postgres_db: str
    
    # Google OAuth2
    google_client_id: str
    google_client_secret: str
    google_redirect_uri: str 
    
    # Telegram Bot
    telegram_bot_token: str
    telegram_bot_username: str
    
    # JWT
    secret_key: str
    algorithm: str
    access_token_expire_minutes: int 
    
    # Frontend
    frontend_url: str 
    backend_url: str
    
    # Environment
    environment: str
    
    # Redis
    redis_host: str 
    redis_port: int 
    redis_db: int 
    redis_password: Optional[str] 
    
    # First Admin (optional)
    first_admin_email: Optional[str] = None
    first_admin_name: Optional[str] = None
    first_admin_google_id: Optional[str] = None
    first_admin_role: Optional[str] = None
    
    # YooKassa
    yookassa_shop_id: str
    yookassa_secret_key: str
    yookassa_test_mode: bool = False  # Режим тестирования
    
    class Config:
        env_file = ".env"


settings = Settings()
