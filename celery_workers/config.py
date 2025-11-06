"""
Настройки для Celery workers с использованием Pydantic Settings
"""
from pydantic_settings import BaseSettings
from typing import Optional


class CeleryWorkerSettings(BaseSettings):
    """Настройки для Celery workers"""
    
    # RabbitMQ настройки
    rabbitmq_url: Optional[str]
    rabbitmq_user: str
    rabbitmq_password: str
    rabbitmq_host: str
    rabbitmq_port: int
    
    # Celery настройки
    celery_backend_url: str
    
    # SMTP настройки
    smtp_host: str
    smtp_port: int 
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from_email: Optional[str] = None
    
    @property
    def rabbitmq_connection_url(self) -> str:
        """Формирует URL подключения к RabbitMQ"""
        if self.rabbitmq_url:
            return self.rabbitmq_url
        return f"amqp://{self.rabbitmq_user}:{self.rabbitmq_password}@{self.rabbitmq_host}:{self.rabbitmq_port}//"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = CeleryWorkerSettings()

