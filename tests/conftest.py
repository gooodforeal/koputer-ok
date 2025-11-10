"""
Конфигурация и фикстуры для тестов
"""
import pytest
import pytest_asyncio
import sys
from typing import AsyncGenerator, Generator
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, MagicMock as MockModule

# Мокируем зависимости ДО импорта приложения, чтобы избежать ошибок импорта
# если они не установлены
def _create_mock_modules():
    """Создает моки для модулей, которые могут отсутствовать"""
    
    # Моки для парсера компонентов (не нужны для тестов builds)
    component_parser_module = MockModule()
    component_parser_module.component_parser_service = MockModule()
    sys.modules['app.services.component_parser'] = component_parser_module
    
    shop_parser_module = MockModule()
    shop_parser_module.ShopParser = MockModule()
    shop_parser_module.ComponentsCategory = MockModule()
    sys.modules['app.services.shop_parser'] = shop_parser_module
    
    # Мок для bs4 (BeautifulSoup)
    bs4_module = MockModule()
    bs4_module.BeautifulSoup = MockModule()
    sys.modules['bs4'] = bs4_module

# Устанавливаем моки ДО импорта
_create_mock_modules()

from app.database import Base, get_db
from app.core.app_factory import create_app
from app.models.user import User, UserRole
from app.models.component import Component, ComponentCategory
from app.models.build import Build
from app.models.feedback import Feedback, FeedbackType, FeedbackStatus
from app.dependencies.auth import get_current_user, get_optional_user
from app.services.redis_service import RedisService
from app.services.rabbitmq_service import RabbitMQService
from app.services.pdf_generator import PDFGenerator
from app.dependencies.services import (
    get_redis_service,
    get_rabbitmq_service,
    get_pdf_generator
)


# Тестовая база данных SQLite в памяти
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

# Создаем асинхронный движок для тестов
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False
)

# Создаем фабрику сессий
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Создает тестовую сессию базы данных"""
    # Создаем все таблицы
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    async with TestSessionLocal() as session:
        yield session
        await session.rollback()
    
    # Удаляем все таблицы после теста
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def override_get_db(db_session: AsyncSession):
    """Переопределяет зависимость get_db"""
    async def _get_db():
        yield db_session
    return _get_db


@pytest_asyncio.fixture(scope="function")
async def test_user(db_session: AsyncSession) -> User:
    """Создает тестового пользователя"""
    user = User(
        email="test@example.com",
        name="Test User",
        picture="https://example.com/pic.jpg",
        google_id="12345",
        is_active=True,
        role=UserRole.USER
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def test_user2(db_session: AsyncSession) -> User:
    """Создает второго тестового пользователя"""
    user = User(
        email="test2@example.com",
        name="Test User 2",
        picture="https://example.com/pic2.jpg",
        google_id="67890",
        is_active=True,
        role=UserRole.USER
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture(scope="function")
async def test_components(db_session: AsyncSession) -> list[Component]:
    """Создает тестовые компоненты для сборки"""
    components = [
        Component(
            name="Intel Core i5-12400F",
            link="https://example.com/cpu",
            price=15000,
            category=ComponentCategory.PROCESSORY
        ),
        Component(
            name="ASUS PRIME B660M-K",
            link="https://example.com/motherboard",
            price=8000,
            category=ComponentCategory.MATERINSKIE_PLATY
        ),
        Component(
            name="NVIDIA GeForce RTX 3060",
            link="https://example.com/gpu",
            price=35000,
            category=ComponentCategory.VIDEOKARTY
        ),
        Component(
            name="Kingston 16GB DDR4",
            link="https://example.com/ram",
            price=5000,
            category=ComponentCategory.OPERATIVNAYA_PAMYAT
        ),
        Component(
            name="Deepcool Matrexx 55",
            link="https://example.com/case",
            price=4000,
            category=ComponentCategory.KORPUSA
        ),
        Component(
            name="AeroCool VX-550",
            link="https://example.com/psu",
            price=3000,
            category=ComponentCategory.BLOKI_PITANIYA
        ),
        Component(
            name="Deepcool AK400",
            link="https://example.com/cooler",
            price=2000,
            category=ComponentCategory.OHLAZHDENIE
        ),
        Component(
            name="Samsung 980 500GB",
            link="https://example.com/ssd",
            price=6000,
            category=ComponentCategory.SSD_NAKOPITELI
        ),
    ]
    for component in components:
        db_session.add(component)
    await db_session.commit()
    for component in components:
        await db_session.refresh(component)
    return components


@pytest_asyncio.fixture(scope="function")
async def test_feedback(db_session: AsyncSession, test_user: User) -> Feedback:
    """Создает тестовый отзыв"""
    feedback = Feedback(
        title="Тестовый отзыв",
        description="Это тестовое описание отзыва длиной более 10 символов",
        type=FeedbackType.GENERAL,
        status=FeedbackStatus.NEW,
        rating=5,
        user_id=test_user.id
    )
    db_session.add(feedback)
    await db_session.commit()
    await db_session.refresh(feedback)
    return feedback


@pytest_asyncio.fixture(scope="function")
async def test_feedbacks(db_session: AsyncSession, test_user: User, test_user2: User, test_admin: User) -> list[Feedback]:
    """Создает несколько тестовых отзывов"""
    # Создаем дополнительные пользователи для отзывов, так как один пользователь может иметь только один отзыв
    user3 = User(
        email="user3@example.com",
        name="User 3",
        picture="https://example.com/pic3.jpg",
        google_id="user3",
        is_active=True,
        role=UserRole.USER
    )
    user4 = User(
        email="user4@example.com",
        name="User 4",
        picture="https://example.com/pic4.jpg",
        google_id="user4",
        is_active=True,
        role=UserRole.USER
    )
    db_session.add(user3)
    db_session.add(user4)
    await db_session.commit()
    await db_session.refresh(user3)
    await db_session.refresh(user4)
    
    feedbacks = [
        Feedback(
            title="Отзыв о баге",
            description="Обнаружен баг в системе, требуется исправление. Описание длинное.",
            type=FeedbackType.BUG,
            status=FeedbackStatus.NEW,
            rating=2,
            user_id=test_user.id
        ),
        Feedback(
            title="Предложение функции",
            description="Предлагаю добавить новую функцию для улучшения работы системы.",
            type=FeedbackType.FEATURE,
            status=FeedbackStatus.IN_REVIEW,
            rating=4,
            user_id=test_user2.id,
            assigned_to_id=test_admin.id
        ),
        Feedback(
            title="Улучшение интерфейса",
            description="Хотелось бы улучшить пользовательский интерфейс для удобства.",
            type=FeedbackType.IMPROVEMENT,
            status=FeedbackStatus.IN_PROGRESS,
            rating=5,
            user_id=user3.id,
            assigned_to_id=test_admin.id
        ),
        Feedback(
            title="Общий отзыв",
            description="Хороший сервис, но есть что улучшить. Это общий отзыв.",
            type=FeedbackType.GENERAL,
            status=FeedbackStatus.RESOLVED,
            rating=4,
            user_id=user4.id,
            admin_response="Спасибо за отзыв!"
        ),
    ]
    for feedback in feedbacks:
        db_session.add(feedback)
    await db_session.commit()
    for feedback in feedbacks:
        await db_session.refresh(feedback)
    return feedbacks


@pytest.fixture(scope="function")
def mock_redis_service():
    """Создает мок для Redis сервиса"""
    mock_redis = AsyncMock(spec=RedisService)
    mock_redis.get = AsyncMock(return_value=None)
    mock_redis.set = AsyncMock(return_value=True)
    mock_redis.delete = AsyncMock(return_value=True)
    mock_redis.get_keys = AsyncMock(return_value=[])
    mock_redis.cleanup_expired_keys = AsyncMock(return_value=0)
    return mock_redis


@pytest.fixture(scope="function")
def mock_rabbitmq_service():
    """Создает мок для RabbitMQ сервиса"""
    mock_rabbitmq = AsyncMock(spec=RabbitMQService)
    mock_rabbitmq.connect = AsyncMock(return_value=None)
    mock_rabbitmq.disconnect = AsyncMock(return_value=None)
    mock_rabbitmq.ensure_connected = AsyncMock(return_value=None)
    mock_rabbitmq.declare_exchange = AsyncMock()
    mock_rabbitmq.declare_queue = AsyncMock()
    mock_rabbitmq.bind_queue = AsyncMock()
    mock_rabbitmq.publish_message = AsyncMock(return_value=None)
    mock_rabbitmq.publish_json = AsyncMock(return_value=None)
    mock_rabbitmq.setup_celery_queue = AsyncMock()
    # Создаем моки для возвращаемых значений
    mock_exchange = MagicMock()
    mock_queue = MagicMock()
    mock_queue.name = "test_queue"
    mock_rabbitmq.setup_celery_queue.return_value = (mock_exchange, mock_queue)
    return mock_rabbitmq


@pytest.fixture(scope="function")
def mock_pdf_generator():
    """Создает мок для PDFGenerator"""
    mock_pdf = AsyncMock(spec=PDFGenerator)
    async def mock_create_build_pdf(build, buffer):
        """Мок метод для генерации PDF"""
        buffer.write(b"%PDF-1.4\n")
        buffer.write(b"1 0 obj\n<< /Type /Catalog >>\nendobj\n")
        buffer.write(b"xref\n0 2\ntrailer\n<< /Size 2 >>\n")
        buffer.write(b"startxref\n25\n%%EOF\n")
        buffer.seek(0)
    mock_pdf.create_build_pdf = mock_create_build_pdf
    return mock_pdf


def _create_test_app(override_get_db, mock_redis_service, mock_rabbitmq_service, mock_pdf_generator):
    """Вспомогательная функция для создания тестового приложения"""
    app = create_app()
    
    # Переопределяем зависимость базы данных
    app.dependency_overrides[get_db] = override_get_db
    
    # Переопределяем зависимости сервисов
    def _get_redis_service():
        return mock_redis_service
    
    def _get_rabbitmq_service():
        return mock_rabbitmq_service
    
    def _get_pdf_generator():
        return mock_pdf_generator
    
    app.dependency_overrides[get_redis_service] = _get_redis_service
    app.dependency_overrides[get_rabbitmq_service] = _get_rabbitmq_service
    app.dependency_overrides[get_pdf_generator] = _get_pdf_generator
    
    return app


@pytest.fixture(scope="function")
def client(override_get_db, mock_redis_service, mock_rabbitmq_service, mock_pdf_generator, test_user):
    """Создает тестовый клиент FastAPI с авторизованным пользователем"""
    # Создаем отдельный экземпляр приложения для этого клиента
    app = _create_test_app(override_get_db, mock_redis_service, mock_rabbitmq_service, mock_pdf_generator)
    
    # Переопределяем зависимость авторизации
    async def _get_current_user():
        return test_user
    
    async def _get_optional_user():
        return test_user
    
    app.dependency_overrides[get_current_user] = _get_current_user
    app.dependency_overrides[get_optional_user] = _get_optional_user
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def unauthenticated_client(override_get_db, mock_redis_service, mock_rabbitmq_service, mock_pdf_generator):
    """Создает неавторизованный тестовый клиент"""
    # Создаем отдельный экземпляр приложения для этого клиента
    app = _create_test_app(override_get_db, mock_redis_service, mock_rabbitmq_service, mock_pdf_generator)
    
    async def _get_optional_user():
        return None
    
    app.dependency_overrides[get_optional_user] = _get_optional_user
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client_user2(override_get_db, mock_redis_service, mock_rabbitmq_service, mock_pdf_generator, test_user2):
    """Создает тестовый клиент для второго пользователя"""
    # Создаем отдельный экземпляр приложения для этого клиента
    app = _create_test_app(override_get_db, mock_redis_service, mock_rabbitmq_service, mock_pdf_generator)
    
    async def _get_current_user():
        return test_user2
    
    async def _get_optional_user():
        return test_user2
    
    app.dependency_overrides[get_current_user] = _get_current_user
    app.dependency_overrides[get_optional_user] = _get_optional_user
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def test_admin(db_session: AsyncSession) -> User:
    """Создает тестового администратора"""
    user = User(
        email="admin@example.com",
        name="Admin User",
        picture="https://example.com/admin.jpg",
        google_id="admin123",
        is_active=True,
        role=UserRole.ADMIN
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def admin_client(override_get_db, mock_redis_service, mock_rabbitmq_service, mock_pdf_generator, test_admin):
    """Создает тестовый клиент для администратора"""
    # Создаем отдельный экземпляр приложения для этого клиента
    app = _create_test_app(override_get_db, mock_redis_service, mock_rabbitmq_service, mock_pdf_generator)
    
    async def _get_current_user():
        return test_admin
    
    async def _get_optional_user():
        return test_admin
    
    app.dependency_overrides[get_current_user] = _get_current_user
    app.dependency_overrides[get_optional_user] = _get_optional_user
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def test_super_admin(db_session: AsyncSession) -> User:
    """Создает тестового супер-администратора"""
    user = User(
        email="superadmin@example.com",
        name="Super Admin User",
        picture="https://example.com/superadmin.jpg",
        google_id="superadmin123",
        is_active=True,
        role=UserRole.SUPER_ADMIN
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def super_admin_client(override_get_db, mock_redis_service, mock_rabbitmq_service, mock_pdf_generator, test_super_admin):
    """Создает тестовый клиент для супер-администратора"""
    # Создаем отдельный экземпляр приложения для этого клиента
    app = _create_test_app(override_get_db, mock_redis_service, mock_rabbitmq_service, mock_pdf_generator)
    
    async def _get_current_user():
        return test_super_admin
    
    async def _get_optional_user():
        return test_super_admin
    
    app.dependency_overrides[get_current_user] = _get_current_user
    app.dependency_overrides[get_optional_user] = _get_optional_user
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


# Патч для исправления проблемы совместимости pytest-asyncio с pytest 8.2+
# В pytest 8.2+ был удален атрибут unittest из FixtureDef
def pytest_configure(config):
    """Настраивает pytest перед запуском тестов"""
    # Отключаем плагин unittest, если он активен
    try:
        unittest_plugin = config.pluginmanager.get_plugin("unittest")
        if unittest_plugin:
            config.pluginmanager.unregister(unittest_plugin)
    except Exception:
        pass


def pytest_sessionstart(session):
    """Патч для FixtureDef - добавляем отсутствующий атрибут unittest"""
    import _pytest.fixtures
    
    # Сохраняем оригинальный __init__
    original_init = _pytest.fixtures.FixtureDef.__init__
    
    def patched_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        # Добавляем отсутствующий атрибут unittest = False
        if not hasattr(self, 'unittest'):
            object.__setattr__(self, 'unittest', False)
    
    # Заменяем __init__
    _pytest.fixtures.FixtureDef.__init__ = patched_init
