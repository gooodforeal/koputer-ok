#!/bin/bash
set -e

echo "⏳ Ожидание подключения к базе данных..."
# Ожидаем пока база данных не будет готова
until PGPASSWORD="${POSTGRES_PASSWORD}" psql -h "${POSTGRES_HOST:-postgres}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" -c '\q' 2>/dev/null; do
  echo "База данных недоступна - ожидание..."
  sleep 2
done

echo "✅ База данных готова!"

echo "📦 Запуск миграций Alembic..."
cd /app
alembic upgrade head

echo "🔧 Настройка первого администратора..."
python setup_admin.py

echo "🚀 Запуск FastAPI приложения..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

