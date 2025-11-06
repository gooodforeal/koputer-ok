# Celery Workers

Сервис для асинхронной отправки email через Celery и RabbitMQ.

## Описание

Этот сервис обрабатывает задачи отправки email, которые публикуются из основного бекенда через RabbitMQ. Использует Celery для управления задачами и RabbitMQ в качестве брокера сообщений.

## Структура

- `config.py` - Настройки с использованием Pydantic Settings
- `celery_app.py` - Конфигурация Celery приложения
- `tasks.py` - Определение задач Celery для отправки email
- `main.py` - Точка входа для запуска worker
- `Dockerfile` - Docker образ для контейнеризации

## Настройка

Для работы сервиса необходимо настроить следующие переменные окружения в `.env`:

### RabbitMQ
- `RABBITMQ_URL` - URL подключения к RabbitMQ (опционально, можно использовать отдельные параметры)
- `RABBITMQ_USER` - Пользователь RabbitMQ (по умолчанию: guest)
- `RABBITMQ_PASSWORD` - Пароль RabbitMQ (по умолчанию: guest)
- `RABBITMQ_HOST` - Хост RabbitMQ (по умолчанию: rabbitmq)
- `RABBITMQ_PORT` - Порт RabbitMQ (по умолчанию: 5672)

### Celery
- `CELERY_BACKEND_URL` - URL для backend Celery (по умолчанию: rpc://)

### SMTP
- `SMTP_HOST` - SMTP сервер (по умолчанию: smtp.gmail.com)
- `SMTP_PORT` - Порт SMTP (по умолчанию: 587)
- `SMTP_USER` - Пользователь SMTP (обязательно)
- `SMTP_PASSWORD` - Пароль SMTP (обязательно)
- `SMTP_FROM_EMAIL` - Email отправителя (по умолчанию: SMTP_USER)

## Задачи

### send_login_email

Отправляет email пользователю при входе в систему.

**Очередь:** `celery_login`

**Параметры:**
- `email` - Email адрес получателя
- `user_name` - Имя пользователя
- `login_time` - Время входа (опционально)

**Поведение:**
- Автоматически повторяет попытку при ошибках (до 3 раз)
- Логирует все операции
- Возвращает статус выполнения

### send_balance_email

Отправляет email пользователю при успешном пополнении баланса.

**Очередь:** `celery_balance`

**Параметры:**
- `email` - Email адрес получателя
- `user_name` - Имя пользователя
- `amount` - Сумма пополнения
- `new_balance` - Новый баланс после пополнения
- `payment_time` - Время пополнения (опционально)
- `transaction_id` - ID транзакции (опционально)

**Поведение:**
- Автоматически повторяет попытку при ошибках (до 3 раз)
- Логирует все операции
- Возвращает статус выполнения

## Запуск

Сервис запускается автоматически при старте docker-compose:

```bash
docker-compose up celery_workers
```

Или вручную для всех очередей:

```bash
celery -A celery_workers.celery_app worker --loglevel=info --concurrency=2
```

Для запуска воркеров для конкретных очередей:

```bash
# Только для email о входе
celery -A celery_workers.celery_app worker --loglevel=info --queues=celery_login

# Только для email о пополнении баланса
celery -A celery_workers.celery_app worker --loglevel=info --queues=celery_balance

# Для обеих очередей
celery -A celery_workers.celery_app worker --loglevel=info --queues=celery_login,celery_balance
```

## Мониторинг

Для мониторинга задач можно использовать:
- RabbitMQ Management UI: http://localhost:15672
- Celery Flower (если установлен)

