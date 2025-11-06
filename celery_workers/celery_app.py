"""
Celery приложение для обработки задач отправки email
"""
from celery import Celery
from celery_workers.config import settings

# Создаем Celery приложение
celery_app = Celery(
    "celery_workers",
    broker=settings.rabbitmq_connection_url,
    backend=settings.celery_backend_url,
)

# Конфигурация Celery
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 минут
    task_soft_time_limit=25 * 60,  # 25 минут
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
    task_routes={
        "send_login_email": {"queue": "celery_login"},
        "send_balance_email": {"queue": "celery_balance"},
    },
)

# Импортируем задачи
from celery_workers import tasks  # noqa

