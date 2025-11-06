"""
Точка входа для Celery worker
"""
import logging
from celery_workers.celery_app import celery_app

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

if __name__ == "__main__":
    celery_app.start()

