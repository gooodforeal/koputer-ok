# Komputer.ok - Система подбора компьютерных сборок

Полнофункциональное веб-приложение для подбора и управления компьютерными сборками с поддержкой OAuth авторизации, Telegram бота, системы отзывов, чат-поддержки, интегрированной платежной системы для управления балансом пользователей и автоматической email рассылки.

## 📋 Содержание

- [Описание](#описание)
- [Архитектура](#архитектура)
- [Возможности](#возможности)
- [Технологический стек](#технологический-стек)
- [Требования](#требования)
- [Установка](#установка)
- [Конфигурация](#конфигурация)
- [Запуск](#запуск)
- [Использование](#использование)
- [API](#api)
- [Структура проекта](#структура-проекта)
- [Разработка](#разработка)
- [Тестирование](#тестирование)
- [Развертывание](#развертывание)
- [Troubleshooting](#troubleshooting)

## 🎯 Описание

Komputer.ok - это современная платформа для подбора компьютерных сборок, которая позволяет пользователям:
- Создавать и публиковать сборки ПК
- Искать оптимальные комплектующие по бюджету
- Получать рекомендации по совместимости компонентов
- Оставлять отзывы и оценки
- Общаться с администраторами через чат
- Получать поддержку через Telegram бота
- Управлять балансом и совершать платежи через интегрированную платежную систему
- Получать email уведомления о важных событиях (вход в систему, пополнение баланса)

## 🏗️ Архитектура

Ниже представлена схема архитектуры приложения:

![Схема архитектуры приложения](readme_assets/scheme1.png)

## ✨ Возможности

### Для пользователей
- 🔐 **Авторизация**: OAuth2 через Google и авторизация через Telegram бота
- 🖥️ **Сборки ПК**: Создание, просмотр и управление компьютерными сборками
  - Экспорт сборок в PDF
  - Рейтинги и комментарии к сборкам
  - Поиск и фильтрация сборок
  - Топ популярных сборок
- 🔍 **Компоненты**: Поиск и фильтрация комплектующих
- ⭐ **Отзывы**: Система отзывов и обратной связи
- 💬 **Чат-поддержка**: Общение с администраторами в реальном времени
- 💳 **Система баланса**: Пополнение баланса через Юкассу, просмотр истории транзакций и статистики
- 📊 **Профиль**: Личная панель управления со статистикой
- 📧 **Email уведомления**: Автоматические email уведомления о входе в систему и пополнении баланса

### Для администраторов
- 👥 **Управление пользователями**: Просмотр, поиск и редактирование пользователей, управление ролями
- 📝 **Обратная связь**: Просмотр и обработка отзывов пользователей
- 🔧 **Управление сборками**: Модерация контента
- 💬 **Чат-модерация**: Поддержка пользователей через встроенный чат, назначение администраторов на чаты
- 📈 **Статистика**: Аналитика использования системы
- 📦 **Управление компонентами**: Добавление и управление компонентами ПК

## 🛠 Технологический стек

### Backend
- **FastAPI** - современный веб-фреймворк для Python
- **SQLAlchemy** - ORM для работы с базой данных
- **Alembic** - миграции базы данных
- **PostgreSQL** - основная база данных
- **Redis** - кеширование и хранение сессий
- **RabbitMQ** - брокер сообщений для асинхронных задач
- **Celery** - распределенная система выполнения задач для фоновой обработки email
- **Python 3.11+** - язык программирования

### Frontend
- **React 18** - библиотека для построения пользовательского интерфейса
- **TypeScript** - типизированный JavaScript
- **Vite** - инструмент сборки
- **Tailwind CSS** - utility-first CSS фреймворк
- **React Router** - маршрутизация
- **Axios** - HTTP клиент

### Дополнительные сервисы
- **Telegram Bot API** - интеграция с Telegram
- **Google OAuth2** - авторизация через Google
- **YooKassa** - платежная система для приема платежей
- **SMTP** - отправка email уведомлений
- **Docker & Docker Compose** - контейнеризация
- **Prometheus** - сбор метрик приложения
- **Grafana** - визуализация метрик и логов
- **Loki** - агрегация логов
- **Promtail** - сбор логов из контейнеров

## 📦 Требования

Для локальной разработки:
- Python 3.11 или выше
- Node.js 20 или выше
- PostgreSQL 13+
- Redis 7+
- RabbitMQ 3+ (для email рассылки)
- Docker и Docker Compose (опционально, но рекомендуется)

## 🚀 Установка

### Клонирование репозитория

```bash
git clone <repository-url>
cd oauth-google
```

### Установка зависимостей Backend

```bash
# Создание виртуального окружения
python -m venv venv

# Активация виртуального окружения
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt
```

### Установка зависимостей Frontend

```bash
cd frontend
npm install
cd ..
```

## ⚙️ Конфигурация

Создайте файл `.env` в корне проекта со следующим содержимым:

```env
# База данных PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=dbname

# Google OAuth2
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_REDIRECT_URI=http://localhost:8000/api/auth/google/callback

# Telegram Bot
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_BOT_USERNAME=your_bot_username

# JWT настройки
SECRET_KEY=your_secret_key_here_min_32_chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# URLs
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000

# Окружение
ENVIRONMENT=development

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# Первый администратор (опционально)
FIRST_ADMIN_EMAIL=admin@example.com
FIRST_ADMIN_NAME=Admin Name
FIRST_ADMIN_GOOGLE_ID=google_id_here
FIRST_ADMIN_ROLE=SUPER_ADMIN

# YooKassa (Платежная система)
YOOKASSA_SHOP_ID=your_yookassa_shop_id
YOOKASSA_SECRET_KEY=your_yookassa_secret_key
YOOKASSA_TEST_MODE=true  # true для тестового режима, false для продакшена

# RabbitMQ (Брокер сообщений для email рассылки)
RABBITMQ_URL=amqp://guest:guest@localhost:5672/  # Опционально, можно указать полный URL
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest
RABBITMQ_HOST=localhost  # Используется в celery workers
RABBITMQ_PORT=5672

# Celery (Обработка фоновых задач)
CELERY_BACKEND_URL=redis://localhost:6379/1  # Redis для хранения результатов задач

# SMTP (Отправка email)
SMTP_HOST=smtp.gmail.com  # SMTP сервер
SMTP_PORT=587  # Порт SMTP (обычно 587 для TLS)
SMTP_USER=your_email@gmail.com  # Email для отправки
SMTP_PASSWORD=your_app_password  # Пароль приложения (для Gmail используйте App Password)
SMTP_FROM_EMAIL=your_email@gmail.com  # Email отправителя (по умолчанию используется SMTP_USER)
```

### Настройка Google OAuth2

1. Перейдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Создайте новый проект или выберите существующий
3. Включите Google+ API
4. Создайте OAuth 2.0 Client ID
5. Добавьте авторизованный redirect URI: `http://localhost:8000/api/auth/google/callback`
   - **Важно**: После добавления префикса `/api` ко всем роутерам, путь callback теперь `/api/auth/google/callback`
   - Если вы используете другой порт или домен, замените `http://localhost:8000` на ваш URL
6. Скопируйте Client ID и Client Secret в `.env`

### Настройка Telegram Bot

1. Создайте бота через [@BotFather](https://t.me/BotFather)
2. Получите токен бота
3. Добавьте токен и username в `.env`

### Настройка YooKassa

1. Зарегистрируйтесь в [YooKassa](https://yookassa.ru/)
2. Создайте магазин в личном кабинете
3. Получите Shop ID и Secret Key
4. Добавьте их в `.env`
5. Настройте вебхук для уведомлений о платежах:
   - URL вебхука: `http://your-domain.com/api/balance/payment/webhook`
   - Включите события: `payment.succeeded`, `payment.cancelled`
6. Для тестирования используйте тестовые данные и установите `YOOKASSA_TEST_MODE=true`

### Настройка RabbitMQ

При использовании Docker Compose RabbitMQ настраивается автоматически. Для локальной разработки:

1. Установите RabbitMQ локально или используйте Docker:
   ```bash
   docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management-alpine
   ```
2. Веб-интерфейс управления доступен по адресу: http://localhost:15672
   - Логин по умолчанию: `guest`
   - Пароль по умолчанию: `guest`
3. Добавьте настройки в `.env` (значения по умолчанию для локальной разработки)

### Настройка SMTP для Email рассылки

1. **Для Gmail:**
   - Включите двухфакторную аутентификацию в вашем Google аккаунте
   - Создайте пароль приложения: [Google App Passwords](https://myaccount.google.com/apppasswords)
   - Используйте пароль приложения в `SMTP_PASSWORD`
   - `SMTP_HOST=smtp.gmail.com`
   - `SMTP_PORT=587`

2. **Для других почтовых сервисов:**
   - Узнайте SMTP настройки вашего провайдера
   - Обновите `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` в `.env`

3. **Для локальной разработки без реальной отправки:**
   - Можно использовать тестовый SMTP сервер (например, MailHog или MailCatcher)
   - Или временно отключить отправку email, оставив SMTP настройки пустыми

## 🏃 Запуск

### Запуск через Docker Compose (рекомендуется)

```bash
docker-compose up --build
```

Это запустит все сервисы:
- Backend на порту 8000
- Frontend на порту 3000
- PostgreSQL на порту 5432
- Redis на порту 6379
- RabbitMQ на порту 5672 (веб-интерфейс на 15672)
- Celery workers для обработки email задач
- Telegram бот
- Prometheus на порту 9090 (сбор метрик)
- Grafana на порту 3001 (визуализация метрик и логов)
- Loki на порту 3100 (агрегация логов)
- Promtail на порту 9080 (сбор логов)

### Локальный запуск

#### 1. Запуск PostgreSQL, Redis и RabbitMQ

Убедитесь, что PostgreSQL, Redis и RabbitMQ запущены локально или используйте Docker:

```bash
docker run -d --name postgres -e POSTGRES_PASSWORD=password -e POSTGRES_DB=dbname -p 5432:5432 postgres:13
docker run -d --name redis -p 6379:6379 redis:7-alpine
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management-alpine
```

#### 2. Инициализация базы данных

```bash
# Запуск миграций
alembic upgrade head

# Или инициализация с созданием первого администратора
python init_db.py
```

#### 3. Запуск Backend

```bash
# Из корня проекта
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 4. Запуск Frontend

```bash
cd frontend
npm run dev
```

#### 5. Запуск Celery workers для email рассылки

```bash
# Из корня проекта
celery -A celery_workers.celery_app worker --loglevel=info --queues=celery_login,celery_balance
```

#### 6. Запуск Telegram бота (опционально)

```bash
python telegram_bot/main.py
```

## 📖 Использование

### Создание администратора

После первого запуска создайте администратора:

```bash
python make_admin.py email@example.com "Имя Администратора" SUPER_ADMIN
```

Доступные роли:
- `USER` - обычный пользователь
- `ADMIN` - администратор
- `SUPER_ADMIN` - супер-администратор

### Доступ к приложению

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API документация**: http://localhost:8000/docs (Swagger UI)
- **API альтернативная документация**: http://localhost:8000/redoc (ReDoc)
- **Health Check**: http://localhost:8000/api/health
- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090
- **RabbitMQ Management**: http://localhost:15672 (guest/guest)

## 🔌 API

### Основные эндпоинты

#### Аутентификация
- `GET /api/auth/google` - Получить URL для авторизации через Google
- `GET /api/auth/google/callback` - Callback от Google OAuth2
- `GET /api/auth/telegram/init` - Инициализация авторизации через Telegram
- `GET /api/auth/telegram/check/{auth_token}` - Проверка статуса авторизации
- `POST /api/auth/telegram/authorize` - Завершение авторизации через Telegram
- `GET /api/auth/me` - Получить информацию о текущем пользователе
- `POST /api/auth/logout` - Выход из системы

#### Пользователи
- `GET /api/users/profile` - Получить профиль текущего пользователя
- `PUT /api/users/profile` - Обновить профиль пользователя
- `GET /api/users/` - Список всех пользователей (только для супер-администратора)
- `GET /api/users/search` - Поиск пользователей с фильтрами
- `GET /api/users/stats` - Статистика пользователей
- `GET /api/users/{user_id}` - Информация о пользователе
- `PUT /api/users/{user_id}/role` - Обновление роли пользователя (только для супер-администратора)

#### Сборки
- `GET /api/builds` - Список сборок с фильтрацией и пагинацией
- `GET /api/builds/top` - Топ популярных сборок
- `GET /api/builds/my` - Мои сборки (требует авторизации)
- `GET /api/builds/stats` - Статистика по сборкам
- `GET /api/builds/components/unique` - Получить уникальные компоненты из сборок
- `GET /api/builds/{build_id}` - Детали сборки
- `POST /api/builds` - Создание сборки (требует авторизации)
- `PUT /api/builds/{build_id}` - Обновление сборки
- `DELETE /api/builds/{build_id}` - Удаление сборки
- `GET /api/builds/{build_id}/export/pdf` - Экспорт сборки в PDF

#### Рейтинги сборок
- `POST /api/builds/{build_id}/ratings` - Создать/обновить оценку сборки
- `PUT /api/builds/{build_id}/ratings` - Обновить оценку сборки
- `DELETE /api/builds/{build_id}/ratings` - Удалить оценку сборки
- `GET /api/builds/{build_id}/ratings/my` - Получить мою оценку сборки

#### Комментарии к сборкам
- `GET /api/builds/{build_id}/comments` - Получить комментарии к сборке
- `POST /api/builds/{build_id}/comments` - Создать комментарий
- `PUT /api/builds/{build_id}/comments/{comment_id}` - Обновить комментарий
- `DELETE /api/builds/{build_id}/comments/{comment_id}` - Удалить комментарий

#### Компоненты
- `GET /api/components` - Список компонентов с фильтрацией
- `GET /api/components/{id}` - Детали компонента
- `POST /api/components` - Создание компонента (требует админ-прав)

#### Отзывы
- `GET /api/feedback` - Список отзывов
- `POST /api/feedback` - Создание отзыва
- `GET /api/feedback/{id}` - Детали отзыва

#### Чат
- `GET /api/chat/my` - Получить мой чат (требует авторизации)
- `POST /api/chat` - Создание чата
- `GET /api/chat/{chat_id}` - Получение чата
- `GET /api/chat/{chat_id}/messages` - Получить сообщения чата
- `POST /api/chat/{chat_id}/messages` - Отправка сообщения
- `GET /api/chat/admin/chats` - Список чатов для администратора
- `POST /api/chat/{chat_id}/assign` - Назначить администратора на чат
- `PUT /api/chat/{chat_id}/read` - Пометка чата как прочитанного
- `PUT /api/chat/{chat_id}/status` - Обновление статуса чата
- `POST /api/chat/{chat_id}/close` - Закрытие чата
- `POST /api/chat/{chat_id}/reopen` - Повторное открытие чата
- `POST /api/chat/{chat_id}/start-working` - Начало работы над чатом
- `GET /api/chat/summary` - Сводка моих чатов
- `GET /api/chat/admin/summary` - Сводка чатов для администратора
- `GET /api/chat/admin/status/{status}` - Получить чаты по статусу

#### Баланс и платежи
- `GET /api/balance` - Получить баланс текущего пользователя
- `GET /api/balance/stats` - Получить статистику по балансу
- `GET /api/balance/transactions` - Получить список транзакций с пагинацией
- `POST /api/balance/payment/create` - Создать платеж для пополнения баланса
- `POST /api/balance/payment/webhook` - Вебхук от Юкассы для обработки платежей
- `GET /api/balance/payment/{payment_id}/status` - Получить статус платежа

#### Health Check
- `GET /api/health` - Проверка состояния приложения
- `GET /api/` - Корневой эндпоинт API

Подробная документация доступна по адресу `/docs` после запуска сервера.

## 📁 Структура проекта

```
oauth-google/
├── app/                          # Backend приложение
│   ├── api/                      # API эндпоинты (health check)
│   ├── core/                     # Ядро приложения
│   │   ├── app_factory.py        # Фабрика приложения
│   │   ├── exception_handlers.py # Обработчики исключений
│   │   ├── lifespan.py          # Управление жизненным циклом
│   │   └── middleware.py         # Middleware (CORS, Prometheus)
│   ├── dependencies/             # FastAPI зависимости
│   │   ├── auth.py               # Зависимости аутентификации
│   │   ├── database.py           # Зависимости БД
│   │   ├── repositories.py       # Зависимости репозиториев
│   │   ├── roles.py              # Зависимости ролей
│   │   └── services.py           # Зависимости сервисов
│   ├── exceptions/                # Исключения приложения
│   ├── models/                   # SQLAlchemy модели
│   │   ├── user.py               # Модель пользователя
│   │   ├── build.py              # Модель сборки
│   │   ├── component.py          # Модель компонента
│   │   ├── chat.py               # Модель чата
│   │   ├── feedback.py           # Модель отзыва
│   │   └── balance.py             # Модель баланса
│   ├── repositories/             # Репозитории для работы с БД
│   ├── routers/                  # API роутеры
│   │   ├── auth.py               # Роутер аутентификации
│   │   ├── users.py              # Роутер пользователей
│   │   ├── builds.py             # Роутер сборок
│   │   ├── components.py         # Роутер компонентов
│   │   ├── chat.py               # Роутер чата
│   │   ├── feedback.py           # Роутер отзывов
│   │   └── balance.py            # Роутер баланса
│   ├── schemas/                  # Pydantic схемы
│   ├── services/                 # Бизнес-логика и сервисы
│   │   ├── build_service.py      # Сервис сборок
│   │   ├── user_service.py       # Сервис пользователей
│   │   ├── pdf_generator.py      # Генератор PDF
│   │   └── ...                   # Другие сервисы
│   ├── utils/                    # Утилиты
│   ├── auth.py                   # JWT аутентификация
│   ├── config.py                 # Конфигурация
│   ├── database.py               # Подключение к БД
│   └── main.py                   # Точка входа
├── frontend/                     # Frontend приложение
│   ├── src/
│   │   ├── components/           # React компоненты
│   │   ├── contexts/             # React контексты
│   │   ├── services/             # API сервисы
│   │   ├── types/               # TypeScript типы
│   │   ├── utils/                # Утилиты
│   │   ├── App.tsx               # Главный компонент
│   │   └── index.tsx             # Точка входа
│   └── package.json
├── telegram_bot/                 # Telegram бот
│   ├── bot.py                    # Основная логика бота
│   ├── config.py                 # Конфигурация бота
│   └── main.py                   # Запуск бота
├── celery_workers/               # Celery workers для фоновых задач
│   ├── celery_app.py             # Конфигурация Celery
│   ├── tasks.py                  # Задачи отправки email
│   ├── config.py                 # Настройки для workers
│   ├── template_loader.py        # Загрузка шаблонов email
│   └── templates/                # HTML и текстовые шаблоны email
├── grafana/                      # Конфигурация мониторинга
│   ├── datasources.yaml          # Источники данных Grafana
│   ├── prometheus.yml            # Конфигурация Prometheus
│   ├── loki-config.yaml          # Конфигурация Loki
│   ├── promtail-config.yaml      # Конфигурация Promtail
│   └── dashboards/               # Дашборды Grafana
├── alembic/                      # Миграции БД
│   └── versions/                 # Файлы миграций
├── tests/                        # Тесты
├── docker-compose.yml            # Docker Compose конфигурация
├── Dockerfile                    # Dockerfile для backend
├── requirements.txt              # Python зависимости
└── README.md                     # Этот файл
```

## 👨‍💻 Разработка

### Миграции базы данных

```bash
# Создание новой миграции
alembic revision --autogenerate -m "Описание изменений"

# Применение миграций
alembic upgrade head

# Откат миграции
alembic downgrade -1
```

### Добавление новых зависимостей

**Backend:**
```bash
pip install package_name
pip freeze > requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install package_name
```

### Структура кода

- **Models** (`app/models/`) - SQLAlchemy модели БД
- **Schemas** (`app/schemas/`) - Pydantic схемы для валидации
- **Routers** (`app/routers/`) - API эндпоинты
- **Repositories** (`app/repositories/`) - Слой работы с БД
- **Services** (`app/services/`) - Бизнес-логика
  - `build_service.py` - Сервис для работы со сборками
  - `user_service.py` - Сервис для работы с пользователями
  - `pdf_generator.py` - Генератор PDF для экспорта сборок
  - `email_publisher.py` - Публикация задач отправки email в RabbitMQ
  - `background_tasks.py` - Фоновые задачи приложения
- **Celery Workers** (`celery_workers/`) - Фоновые задачи для отправки email
  - `tasks.py` - Задачи отправки email (вход в систему, пополнение баланса)
  - `template_loader.py` - Загрузка и рендеринг шаблонов email
- **Monitoring** (`grafana/`) - Конфигурация мониторинга
  - Prometheus для сбора метрик
  - Grafana для визуализации
  - Loki для агрегации логов
  - Promtail для сбора логов из контейнеров

## 🧪 Тестирование

```bash
# Запуск тестов
pytest

# С покрытием
pytest --cov=app tests/

# Конкретный тест
pytest tests/test_builds.py
```

## 🚢 Развертывание

### Production настройки

1. Обновите `.env` файл с production значениями
2. Установите `ENVIRONMENT=production`
3. Настройте безопасные секретные ключи
4. Обновите CORS настройки в `app/core/middleware.py`
5. Используйте production-сборку Docker образов
6. Настройте HTTPS для всех сервисов
7. Настройте мониторинг и алерты в Grafana
8. Настройте резервное копирование базы данных

### Docker Compose Production

```bash
docker-compose -f docker-compose.prod.yml up -d
```

### Переменные окружения для Production

- Используйте сильные пароли для БД
- Генерируйте длинные SECRET_KEY
- Настройте HTTPS
- Ограничьте CORS origins
- Включите логирование
- Установите `YOOKASSA_TEST_MODE=false` для работы с реальными платежами
- Настройте вебхук Юкассы на production URL с HTTPS
- Убедитесь, что все платежные данные защищены и не попадают в логи
- Настройте production SMTP сервер для отправки email
- Используйте надежные учетные данные для RabbitMQ
- Настройте мониторинг Celery workers

## 🔧 Troubleshooting

### Проблемы с базой данных

```bash
# Проверка подключения
psql -h localhost -U user -d dbname

# Сброс миграций (осторожно!)
alembic downgrade base
alembic upgrade head
```

### Проблемы с Redis

```bash
# Проверка подключения
redis-cli ping
```

### Проблемы с OAuth

- Убедитесь, что redirect URI в Google Console совпадает с настройками
- Проверьте, что Client ID и Secret правильные
- Убедитесь, что фронтенд URL настроен корректно

### Проблемы с Telegram ботом

- Проверьте токен бота
- Убедитесь, что бот запущен
- Проверьте логи бота

### Проблемы с платежами (YooKassa)

- Убедитесь, что Shop ID и Secret Key правильные
- Проверьте, что вебхук настроен корректно в личном кабинете Юкассы
- Убедитесь, что URL вебхука доступен извне (для production используйте HTTPS)
- Проверьте логи приложения на наличие ошибок при обработке вебхуков
- Для тестирования используйте тестовый режим (`YOOKASSA_TEST_MODE=true`)
- Убедитесь, что баланс создается автоматически при первом обращении пользователя

### Проблемы с Email рассылкой

- **Проверьте SMTP настройки**: Убедитесь, что `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` правильно настроены
- **Для Gmail**: Используйте пароль приложения, а не обычный пароль аккаунта
- **Проверьте RabbitMQ**: Убедитесь, что RabbitMQ запущен и доступен
  ```bash
  # Проверка подключения
  rabbitmq-diagnostics ping
  ```
- **Проверьте Celery workers**: Убедитесь, что Celery workers запущены и обрабатывают задачи
  ```bash
  # Проверка статуса workers
  celery -A celery_workers.celery_app inspect active
  ```
- **Проверьте логи Celery**: Смотрите логи workers для выявления ошибок отправки
- **Проверьте очереди**: Убедитесь, что задачи попадают в очереди RabbitMQ (можно проверить через веб-интерфейс на порту 15672)
- **Проблемы с шаблонами**: Убедитесь, что шаблоны email находятся в `celery_workers/templates/`
- **Firewall/Security**: Убедитесь, что SMTP порт не заблокирован файрволом

### Проблемы с RabbitMQ

```bash
# Проверка подключения
rabbitmq-diagnostics ping

# Проверка статуса
rabbitmqctl status

# Просмотр очередей
rabbitmqctl list_queues
```

- Убедитесь, что RabbitMQ запущен и доступен на указанном порту
- Проверьте учетные данные (`RABBITMQ_USER`, `RABBITMQ_PASSWORD`)
- Для Docker убедитесь, что контейнер RabbitMQ запущен и здоров
- Проверьте веб-интерфейс RabbitMQ на порту 15672

### Проблемы с мониторингом

- **Grafana не отображает данные**: Проверьте, что Prometheus и Loki запущены и доступны
- **Метрики не собираются**: Убедитесь, что Prometheus может подключиться к backend (проверьте `/metrics` эндпоинт)
- **Логи не отображаются**: Проверьте, что Promtail собирает логи из контейнеров и отправляет их в Loki
- **Доступ к Grafana**: По умолчанию логин/пароль: admin/admin (измените в production!)

### Очистка и перезапуск

```bash
# Остановка всех контейнеров
docker-compose down

# Удаление volumes (осторожно - удалит данные!)
docker-compose down -v

# Пересборка
docker-compose up --build
```

## 📝 Лицензия

[Укажите вашу лицензию здесь]

## 👥 Авторы

[Укажите авторов проекта]

## 🙏 Благодарности

- FastAPI за отличный фреймворк
- React команде за React
- Всем контрибьюторам проекта

---

**Примечание**: Этот проект находится в активной разработке. Некоторые функции могут изменяться.
