# Тесты для эндпоинтов builds

## Описание

Этот модуль содержит тесты для всех эндпоинтов `/api/builds` на pytest.

## Запуск тестов

### Установка зависимостей

```bash
pip install -r requirements-test.txt
```

### Запуск всех тестов

```bash
pytest tests/test_builds.py
```

### Запуск с выводом подробной информации

```bash
pytest tests/test_builds.py -v
```

### Запуск конкретного теста

```bash
pytest tests/test_builds.py::TestCreateBuild::test_create_build_success -v
```

### Запуск с покрытием кода

```bash
pytest tests/test_builds.py --cov=app/routers/builds --cov-report=html
```

## Структура тестов

- `conftest.py` - фикстуры для тестов (БД, пользователи, компоненты, клиенты)
- `test_builds.py` - тесты для всех эндпоинтов builds

## Покрытие тестами

Тесты покрывают следующие эндпоинты:

### Основные эндпоинты сборок
- ✅ POST `/api/builds/` - создание сборки
- ✅ GET `/api/builds/` - получение списка сборок
- ✅ GET `/api/builds/top` - получение топа сборок
- ✅ GET `/api/builds/my` - получение моих сборок
- ✅ GET `/api/builds/stats` - получение статистики
- ✅ GET `/api/builds/components/unique` - получение уникальных компонентов
- ✅ GET `/api/builds/{build_id}` - получение сборки по ID
- ✅ PUT `/api/builds/{build_id}` - обновление сборки
- ✅ DELETE `/api/builds/{build_id}` - удаление сборки

### Эндпоинты оценок
- ✅ POST `/api/builds/{build_id}/ratings` - создание оценки
- ✅ PUT `/api/builds/{build_id}/ratings` - обновление оценки
- ✅ DELETE `/api/builds/{build_id}/ratings` - удаление оценки
- ✅ GET `/api/builds/{build_id}/ratings/my` - получение моей оценки

### Эндпоинты комментариев
- ✅ POST `/api/builds/{build_id}/comments` - создание комментария
- ✅ GET `/api/builds/{build_id}/comments` - получение комментариев
- ✅ PUT `/api/builds/{build_id}/comments/{comment_id}` - обновление комментария
- ✅ DELETE `/api/builds/{build_id}/comments/{comment_id}` - удаление комментария

### Дополнительные эндпоинты
- ✅ GET `/api/builds/{build_id}/export/pdf` - экспорт PDF

## Тестовые данные

Тесты используют:
- Тестовую БД SQLite в памяти
- Моки для Redis сервиса
- Тестовых пользователей (2 пользователя для проверки прав доступа)
- Тестовые компоненты (8 компонентов всех необходимых категорий)

