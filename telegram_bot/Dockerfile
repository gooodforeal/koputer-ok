FROM python:3.12-slim

WORKDIR /app

# Копируем файлы зависимостей
COPY telegram_bot/requirements.txt /app/requirements.txt

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем код бота
COPY telegram_bot/ /app/telegram_bot/

# Устанавливаем переменные окружения
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Запускаем бота
CMD ["python", "-m", "telegram_bot.main"]

