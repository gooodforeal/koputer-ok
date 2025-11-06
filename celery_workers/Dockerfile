FROM python:3.11-slim

WORKDIR /app

# Устанавливаем зависимости
COPY celery_workers/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код worker
COPY celery_workers/ ./celery_workers/

# Запускаем Celery worker для обеих очередей
CMD ["celery", "-A", "celery_workers.celery_app", "worker", "--loglevel=info", "--concurrency=2", "--queues=celery_login,celery_balance"]

