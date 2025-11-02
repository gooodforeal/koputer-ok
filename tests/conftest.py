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
from unittest.mock import AsyncMock, MagicMock, patch, MagicMock as MockModule

# Мокируем зависимости ДО импорта приложения, чтобы избежать ошибок импорта
# если они не установлены
def _create_mock_modules():
    """Создает моки для модулей, которые могут отсутствовать"""
    
    # Мок для pdf_generator
    pdf_module = MockModule()
    async def mock_create_build_pdf(build, buffer):
        """Мок функция для генерации PDF"""
        buffer.write(b"%PDF-1.4\n")
        buffer.write(b"1 0 obj\n<< /Type /Catalog >>\nendobj\n")
        buffer.write(b"xref\n0 2\ntrailer\n<< /Size 2 >>\n")
        buffer.write(b"startxref\n25\n%%EOF\n")
        buffer.seek(0)
    pdf_module.create_build_pdf = mock_create_build_pdf
    sys.modules['app.services.pdf_generator'] = pdf_module
    
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
from app.dependencies.auth import get_current_user, get_optional_user
from app.services.redis_service import RedisService


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
def app(override_get_db, mock_redis_service):
    """Создает тестовое приложение FastAPI"""
    app = create_app()
    
    # Переопределяем зависимость базы данных
    app.dependency_overrides[get_db] = override_get_db
    
    # Мокаем Redis сервис
    with patch('app.services.redis_service.redis_service', mock_redis_service):
        yield app
    
    # Очищаем переопределения после теста
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def app2(override_get_db, mock_redis_service):
    """Создает тестовое приложение FastAPI"""
    app = create_app()
    
    # Переопределяем зависимость базы данных
    app.dependency_overrides[get_db] = override_get_db
    
    # Мокаем Redis сервис
    with patch('app.services.redis_service.redis_service', mock_redis_service):
        yield app
    
    # Очищаем переопределения после теста
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client(app, test_user):
    """Создает тестовый клиент FastAPI с авторизованным пользователем"""
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
def unauthenticated_client(app):
    """Создает неавторизованный тестовый клиент"""
    async def _get_optional_user():
        return None
    
    app.dependency_overrides[get_optional_user] = _get_optional_user
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def client_user2(app2, test_user2):
    """Создает тестовый клиент для второго пользователя"""
    async def _get_current_user():
        return test_user2
    
    async def _get_optional_user():
        return test_user2
    
    app2.dependency_overrides[get_current_user] = _get_current_user
    app2.dependency_overrides[get_optional_user] = _get_optional_user
    
    with TestClient(app2) as test_client:
        yield test_client
    
    app2.dependency_overrides.clear()


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
