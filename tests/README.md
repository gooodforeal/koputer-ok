# Тесты для API эндпоинтов

## Описание

Этот модуль содержит тесты для всех эндпоинтов API на pytest. Тесты покрывают функциональность роутеров: authentication, users, builds, chat, feedback и components.

## Запуск тестов

### Установка зависимостей

```bash
pip install -r requirements-test.txt
```

### Запуск всех тестов

```bash
pytest tests/
```

### Запуск с выводом подробной информации

```bash
pytest tests/ -v
```

### Запуск конкретного тестового файла

```bash
pytest tests/test_auth.py -v
pytest tests/test_users.py -v
pytest tests/test_builds.py -v
pytest tests/test_chat.py -v
pytest tests/test_feedback.py -v
pytest tests/test_components.py -v
```

### Запуск конкретного теста

```bash
pytest tests/test_auth.py::TestGoogleAuth::test_google_auth_init -v
```

### Запуск с покрытием кода

```bash
pytest tests/ --cov=app/routers --cov-report=html
```

## Структура тестов

- `conftest.py` - общие фикстуры для тестов (БД, пользователи, компоненты, клиенты, моки Redis)
- `test_auth.py` - тесты для эндпоинтов аутентификации
- `test_users.py` - тесты для эндпоинтов пользователей
- `test_builds.py` - тесты для эндпоинтов сборок
- `test_chat.py` - тесты для эндпоинтов чатов
- `test_feedback.py` - тесты для эндпоинтов отзывов
- `test_components.py` - тесты для эндпоинтов компонентов

## Покрытие тестами

### Authentication (`/auth/*`)

#### Google OAuth авторизация
- ✅ GET `/auth/google` - инициация OAuth2 авторизации через Google
- ✅ GET `/auth/google/callback` - обработка callback от Google OAuth2
  - Успешная авторизация и создание пользователя
  - Обработка ошибок при обмене кода на токен
  - Обработка ошибок при получении информации о пользователе

#### Telegram авторизация
- ✅ GET `/auth/telegram/init` - инициация авторизации через Telegram бот
- ✅ POST `/auth/telegram/authorize` - обработка авторизации пользователя через Telegram
  - Успешная авторизация
  - Обработка несуществующего токена
  - Обработка уже использованного токена
  - Обработка ошибок привязки токена
  - Обработка ошибок сохранения JWT токена
- ✅ GET `/auth/telegram/check/{auth_token}` - проверка статуса авторизации
  - Статус ожидания (pending)
  - Статус завершено (completed)
  - Обработка несуществующего токена
  - Обработка использованного токена без JWT

#### Текущий пользователь
- ✅ GET `/auth/me` - получение информации о текущем пользователе
  - Успешное получение для авторизованного пользователя
  - Ошибка доступа для неавторизованного пользователя

#### Выход из системы
- ✅ POST `/auth/logout` - выход из системы
  - Успешный выход для авторизованного пользователя
  - Выход для неавторизованного пользователя

### Users (`/users/*`)

- ✅ GET `/users/profile` - получение профиля пользователя
- ✅ GET `/users/protected` - доступ к защищенному маршруту
- ✅ GET `/users/` - получение списка всех пользователей (только для супер-администратора)
- ✅ GET `/users/search` - поиск пользователей с фильтрами
- ✅ GET `/users/stats` - получение статистики пользователей
- ✅ PUT `/users/profile` - обновление профиля пользователя
- ✅ PUT `/users/{user_id}/role` - обновление роли пользователя (только для супер-администратора)

### Builds (`/api/builds/*`)

#### Основные эндпоинты сборок
- ✅ POST `/api/builds/` - создание сборки
- ✅ GET `/api/builds/` - получение списка сборок
- ✅ GET `/api/builds/top` - получение топа сборок
- ✅ GET `/api/builds/my` - получение моих сборок
- ✅ GET `/api/builds/stats` - получение статистики
- ✅ GET `/api/builds/components/unique` - получение уникальных компонентов
- ✅ GET `/api/builds/{build_id}` - получение сборки по ID
- ✅ PUT `/api/builds/{build_id}` - обновление сборки
- ✅ DELETE `/api/builds/{build_id}` - удаление сборки

#### Эндпоинты оценок
- ✅ POST `/api/builds/{build_id}/ratings` - создание оценки
- ✅ PUT `/api/builds/{build_id}/ratings` - обновление оценки
- ✅ DELETE `/api/builds/{build_id}/ratings` - удаление оценки
- ✅ GET `/api/builds/{build_id}/ratings/my` - получение моей оценки

#### Эндпоинты комментариев
- ✅ POST `/api/builds/{build_id}/comments` - создание комментария
- ✅ GET `/api/builds/{build_id}/comments` - получение комментариев
- ✅ PUT `/api/builds/{build_id}/comments/{comment_id}` - обновление комментария
- ✅ DELETE `/api/builds/{build_id}/comments/{comment_id}` - удаление комментария

#### Дополнительные эндпоинты
- ✅ GET `/api/builds/{build_id}/export/pdf` - экспорт PDF

### Chat (`/api/chat/*`)

- ✅ POST `/api/chat/` - создание чата
- ✅ GET `/api/chat/my` - получение моего чата
- ✅ GET `/api/chat/{chat_id}` - получение чата по ID
- ✅ GET `/api/chat/admin/chats` - получение списка чатов для администратора
- ✅ POST `/api/chat/{chat_id}/assign` - назначение администратора на чат
- ✅ POST `/api/chat/{chat_id}/messages` - отправка сообщения
- ✅ GET `/api/chat/{chat_id}/messages` - получение сообщений чата
- ✅ PUT `/api/chat/{chat_id}/read` - пометка чата как прочитанного
- ✅ GET `/api/chat/summary` - получение сводки моих чатов
- ✅ GET `/api/chat/admin/summary` - получение сводки чатов для администратора
- ✅ PUT `/api/chat/{chat_id}/status` - обновление статуса чата
- ✅ POST `/api/chat/{chat_id}/close` - закрытие чата
- ✅ POST `/api/chat/{chat_id}/reopen` - повторное открытие чата
- ✅ POST `/api/chat/{chat_id}/start-working` - начало работы над чатом
- ✅ GET `/api/chat/admin/status/{status}` - получение чатов по статусу

### Feedback (`/api/feedback/*`)

- ✅ POST `/api/feedback/` - создание отзыва
- ✅ GET `/api/feedback/public` - получение публичных отзывов
- ✅ GET `/api/feedback/` - получение всех отзывов (для администраторов)
- ✅ GET `/api/feedback/my` - получение моих отзывов
- ✅ GET `/api/feedback/assigned` - получение назначенных отзывов (для администраторов)
- ✅ GET `/api/feedback/stats` - получение статистики отзывов
- ✅ GET `/api/feedback/{feedback_id}` - получение отзыва по ID
- ✅ PUT `/api/feedback/{feedback_id}` - обновление отзыва
- ✅ PUT `/api/feedback/{feedback_id}/admin` - обновление отзыва администратором
- ✅ DELETE `/api/feedback/{feedback_id}` - удаление отзыва

### Components (`/api/components/*`)

- ✅ GET `/api/components/` - получение списка компонентов
- ✅ GET `/api/components/stats` - получение статистики компонентов
- ✅ GET `/api/components/category/{category}` - получение компонентов по категории
- ✅ POST `/api/components/parse` - запуск парсинга компонентов (только для администраторов)
- ✅ GET `/api/components/parse/status` - получение статуса парсинга
- ✅ POST `/api/components/parse/stop` - остановка парсинга (только для администраторов)

## Тестовые данные

Тесты используют:
- **Тестовую БД SQLite в памяти** - каждый тест выполняется в изолированной сессии базы данных
- **Моки для Redis сервиса** - все операции с Redis мокируются для избежания зависимости от внешнего сервиса
- **Тестовых пользователей** - создаются фикстуры для обычных пользователей, администраторов и супер-администраторов
- **Тестовые компоненты** - создаются 8 компонентов всех необходимых категорий для тестирования сборок
- **Моки внешних API** - Google OAuth API и Telegram Bot API мокируются в тестах аутентификации

## Фикстуры

В `conftest.py` определены следующие фикстуры:

### База данных
- `db_session` - тестовая сессия базы данных SQLite в памяти
- `override_get_db` - переопределение зависимости `get_db`

### Пользователи
- `test_user` - обычный пользователь
- `test_user2` - второй обычный пользователь
- `test_admin` - администратор
- `test_super_admin` - супер-администратор

### Клиенты для тестирования
- `client` - тестовый клиент с авторизованным пользователем
- `unauthenticated_client` - неавторизованный тестовый клиент
- `client_user2` - тестовый клиент для второго пользователя
- `admin_client` - тестовый клиент для администратора
- `super_admin_client` - тестовый клиент для супер-администратора

### Данные
- `test_components` - список из 8 тестовых компонентов
- `test_feedback` - тестовый отзыв
- `test_feedbacks` - список тестовых отзывов

### Моки
- `mock_redis_service` - мок для Redis сервиса

## Особенности тестирования

### Асинхронные тесты

Все тесты используют `@pytest.mark.asyncio` для поддержки асинхронных операций FastAPI.

### Мокирование внешних сервисов

Тесты используют мокирование для:
- Redis сервиса (все операции с кэшем)
- Google OAuth API (обмен кода на токен, получение информации о пользователе)
- Telegram Bot API (создание токенов авторизации)
- PDF генератора (для тестов экспорта)

### Тестирование авторизации

Тесты проверяют:
- Доступ к эндпоинтам для авторизованных пользователей
- Отклонение доступа для неавторизованных пользователей
- Правильность проверки ролей (USER, ADMIN, SUPER_ADMIN)

### Тестирование OAuth

Тесты для OAuth авторизации включают:
- Мокирование внешних API вызовов
- Проверку создания/обновления пользователей в БД
- Проверку генерации JWT токенов
- Обработку ошибок на различных этапах авторизации
