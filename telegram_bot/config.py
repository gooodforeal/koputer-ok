"""
Конфигурация для Telegram бота
"""
from pydantic_settings import BaseSettings


class BotSettings(BaseSettings):
    """Настройки бота"""
    telegram_bot_token: str
    backend_url: str
    
    class Config:
        env_file = ".env"


settings = BotSettings()

