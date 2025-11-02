"""
Конфигурация для Telegram бота
"""
from pydantic_settings import BaseSettings


class BotSettings(BaseSettings):
    """Настройки бота"""
    telegram_bot_token: str = "7963592516:AAEZipr26SvCBTNZ-qKVM9uF21SDTUy_uvk"
    backend_url: str = "http://backend:8000"
    
    class Config:
        env_file = ".env"


settings = BotSettings()

