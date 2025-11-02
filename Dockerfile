FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копирование и установка Python зависимостей
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копирование кода приложения
COPY . .

# Установка прав на entrypoint скрипт
RUN chmod +x /app/app/entrypoint.sh

# Открытие порта
EXPOSE 8000

# Команда по умолчанию
CMD ["/app/app/entrypoint.sh"]



