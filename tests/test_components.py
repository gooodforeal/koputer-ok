"""
Тесты для эндпоинтов components
"""
import pytest
from fastapi import status
from unittest.mock import AsyncMock
from app.models.component import Component, ComponentCategory
from app.dependencies.services import get_component_parser_service


class TestGetComponents:
    """Тесты для получения списка компонентов"""
    
    @pytest.mark.asyncio
    async def test_get_components_empty_list(self, client):
        """Тест получения пустого списка компонентов"""
        response = client.get("/api/components/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    @pytest.mark.asyncio
    async def test_get_components_with_data(
        self, client, test_components
    ):
        """Тест получения списка компонентов с данными"""
        response = client.get("/api/components/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= len(test_components)
        
        # Проверяем структуру данных
        if data:
            component = data[0]
            assert "id" in component
            assert "name" in component
            assert "link" in component
            assert "category" in component
            assert "price" in component
            assert "created_at" in component
    
    @pytest.mark.asyncio
    async def test_get_components_with_pagination(
        self, client, test_components
    ):
        """Тест получения списка компонентов с пагинацией"""
        response = client.get("/api/components/?skip=0&limit=3")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 3
        
        # Проверяем, что пагинация работает
        if len(test_components) > 3:
            response2 = client.get("/api/components/?skip=3&limit=3")
            assert response2.status_code == status.HTTP_200_OK
            data2 = response2.json()
            assert len(data2) <= 3
            
            # Проверяем, что результаты разные
            if data and data2:
                assert data[0]["id"] != data2[0]["id"]
    
    @pytest.mark.asyncio
    async def test_get_components_unauthenticated(self, unauthenticated_client):
        """Тест получения компонентов неавторизованным пользователем"""
        response = unauthenticated_client.get("/api/components/")
        
        # Компоненты должны быть доступны всем
        assert response.status_code == status.HTTP_200_OK


class TestGetComponentStats:
    """Тесты для получения статистики компонентов"""
    
    @pytest.mark.asyncio
    async def test_get_component_stats_empty(self, client):
        """Тест получения статистики при отсутствии компонентов"""
        response = client.get("/api/components/stats")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 0
        assert "by_category" in data
        assert isinstance(data["by_category"], dict)
        
        # Проверяем, что все категории присутствуют
        for category in ComponentCategory:
            assert category.value in data["by_category"]
            assert data["by_category"][category.value] == 0
    
    @pytest.mark.asyncio
    async def test_get_component_stats_with_data(
        self, client, test_components
    ):
        """Тест получения статистики с данными"""
        response = client.get("/api/components/stats")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] >= len(test_components)
        assert "by_category" in data
        
        # Проверяем, что категории заполнены
        total_by_category = sum(data["by_category"].values())
        assert total_by_category == data["total"]
    
    @pytest.mark.asyncio
    async def test_get_component_stats_unauthenticated(self, unauthenticated_client):
        """Тест получения статистики неавторизованным пользователем"""
        response = unauthenticated_client.get("/api/components/stats")
        
        # Статистика должна быть доступна всем
        assert response.status_code == status.HTTP_200_OK


class TestGetComponentsByCategory:
    """Тесты для получения компонентов по категории"""
    
    @pytest.mark.asyncio
    async def test_get_components_by_category_empty(
        self, client, db_session
    ):
        """Тест получения пустого списка компонентов по категории"""
        response = client.get("/api/components/by-category?category=PROCESSORY")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    @pytest.mark.asyncio
    async def test_get_components_by_category_with_data(
        self, client, test_components
    ):
        """Тест получения компонентов по категории"""
        response = client.get("/api/components/by-category?category=PROCESSORY")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        
        # Проверяем, что все компоненты в нужной категории
        for component in data:
            assert component["category"] == "PROCESSORY"
    
    @pytest.mark.asyncio
    async def test_get_components_by_category_invalid_category(self, client):
        """Тест получения компонентов по несуществующей категории"""
        response = client.get("/api/components/by-category?category=INVALID_CATEGORY")
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "неизвестная категория" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_get_components_by_category_with_search(
        self, client, db_session
    ):
        """Тест поиска компонентов по категории"""
        from app.repositories.component_repository import ComponentRepository
        
        # Создаем тестовые компоненты
        component_repo = ComponentRepository(db_session)
        await component_repo.create(
            name="Intel Core i5-12400F",
            link="https://example.com/cpu1",
            price=15000,
            image=None,
            category=ComponentCategory.PROCESSORY
        )
        await component_repo.create(
            name="AMD Ryzen 5 5600X",
            link="https://example.com/cpu2",
            price=18000,
            image=None,
            category=ComponentCategory.PROCESSORY
        )
        
        # Ищем по части названия
        response = client.get("/api/components/by-category?category=PROCESSORY&query=Intel")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        
        # Проверяем, что найдены только компоненты с "Intel" в названии
        for component in data:
            assert "intel" in component["name"].lower()
    
    @pytest.mark.asyncio
    async def test_get_components_by_category_with_pagination(
        self, client, db_session
    ):
        """Тест пагинации компонентов по категории"""
        from app.repositories.component_repository import ComponentRepository
        
        # Создаем несколько компонентов в одной категории
        component_repo = ComponentRepository(db_session)
        for i in range(5):
            await component_repo.create(
                name=f"Processor {i+1}",
                link=f"https://example.com/cpu{i+1}",
                price=10000 + i * 1000,
                image=None,
                category=ComponentCategory.PROCESSORY
            )
        
        # Получаем первую страницу
        response = client.get("/api/components/by-category?category=PROCESSORY&skip=0&limit=2")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) <= 2
    
    @pytest.mark.asyncio
    async def test_get_components_by_category_unauthenticated(self, unauthenticated_client):
        """Тест получения компонентов по категории неавторизованным пользователем"""
        response = unauthenticated_client.get("/api/components/by-category?category=PROCESSORY")
        
        # Компоненты должны быть доступны всем
        assert response.status_code == status.HTTP_200_OK


class TestParseComponents:
    """Тесты для парсинга компонентов"""
    
    @pytest.mark.asyncio
    async def test_start_parsing_success(self, admin_client):
        """Тест успешного запуска парсинга"""
        # Мокируем component_parser_service
        mock_service = AsyncMock()
        mock_service.get_status = AsyncMock(return_value={"is_running": False})
        mock_service.start_parsing = AsyncMock()
        
        # Переопределяем dependency
        admin_client.app.dependency_overrides[get_component_parser_service] = lambda: mock_service
        
        try:
            response = admin_client.post("/api/components/parse")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "message" in data
            assert "status" in data
            assert data["status"] == "started"
        finally:
            # Очищаем переопределение
            admin_client.app.dependency_overrides.pop(get_component_parser_service, None)
    
    @pytest.mark.asyncio
    async def test_start_parsing_already_running(self, admin_client):
        """Тест запуска парсинга, когда он уже запущен"""
        mock_service = AsyncMock()
        mock_service.get_status = AsyncMock(return_value={"is_running": True})
        
        # Переопределяем dependency
        admin_client.app.dependency_overrides[get_component_parser_service] = lambda: mock_service
        
        try:
            response = admin_client.post("/api/components/parse")
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "уже запущен" in response.json()["detail"].lower()
        finally:
            # Очищаем переопределение
            admin_client.app.dependency_overrides.pop(get_component_parser_service, None)
    
    @pytest.mark.asyncio
    async def test_start_parsing_with_clear_existing(self, admin_client):
        """Тест запуска парсинга с очисткой существующих данных"""
        mock_service = AsyncMock()
        mock_service.get_status = AsyncMock(return_value={"is_running": False})
        mock_service.start_parsing = AsyncMock()
        
        # Переопределяем dependency
        admin_client.app.dependency_overrides[get_component_parser_service] = lambda: mock_service
        
        try:
            response = admin_client.post("/api/components/parse?clear_existing=true")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["status"] == "started"
        finally:
            # Очищаем переопределение
            admin_client.app.dependency_overrides.pop(get_component_parser_service, None)
    
    @pytest.mark.asyncio
    async def test_start_parsing_forbidden(self, client):
        """Тест запуска парсинга обычным пользователем"""
        response = client.post("/api/components/parse")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_start_parsing_unauthenticated(self, unauthenticated_client):
        """Тест запуска парсинга неавторизованным пользователем"""
        response = unauthenticated_client.post("/api/components/parse")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestGetParseStatus:
    """Тесты для получения статуса парсинга"""
    
    @pytest.mark.asyncio
    async def test_get_parse_status_not_running(self, admin_client):
        """Тест получения статуса, когда парсинг не запущен"""
        mock_service = AsyncMock()
        mock_service.get_status = AsyncMock(return_value={
            "is_running": False,
            "current_category": None,
            "processed_categories": 0,
            "total_categories": 0,
            "processed_products": 0,
            "errors": []
        })
        
        # Переопределяем dependency
        admin_client.app.dependency_overrides[get_component_parser_service] = lambda: mock_service
        
        try:
            response = admin_client.get("/api/components/parse/status")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["is_running"] is False
            assert "processed_categories" in data
            assert "total_categories" in data
            assert "processed_products" in data
            assert "errors" in data
        finally:
            # Очищаем переопределение
            admin_client.app.dependency_overrides.pop(get_component_parser_service, None)
    
    @pytest.mark.asyncio
    async def test_get_parse_status_running(self, admin_client):
        """Тест получения статуса, когда парсинг запущен"""
        mock_service = AsyncMock()
        mock_service.get_status = AsyncMock(return_value={
            "is_running": True,
            "current_category": "Процессоры",
            "processed_categories": 2,
            "total_categories": 9,
            "processed_products": 150,
            "errors": []
        })
        
        # Переопределяем dependency
        admin_client.app.dependency_overrides[get_component_parser_service] = lambda: mock_service
        
        try:
            response = admin_client.get("/api/components/parse/status")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["is_running"] is True
            assert data["current_category"] == "Процессоры"
            assert data["processed_categories"] == 2
            assert data["total_categories"] == 9
            assert data["processed_products"] == 150
        finally:
            # Очищаем переопределение
            admin_client.app.dependency_overrides.pop(get_component_parser_service, None)
    
    @pytest.mark.asyncio
    async def test_get_parse_status_with_errors(self, admin_client):
        """Тест получения статуса с ошибками"""
        mock_service = AsyncMock()
        mock_service.get_status = AsyncMock(return_value={
            "is_running": False,
            "current_category": None,
            "processed_categories": 5,
            "total_categories": 9,
            "processed_products": 200,
            "errors": ["Ошибка при парсинге категории Видеокарты"]
        })
        
        # Переопределяем dependency
        admin_client.app.dependency_overrides[get_component_parser_service] = lambda: mock_service
        
        try:
            response = admin_client.get("/api/components/parse/status")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert len(data["errors"]) > 0
        finally:
            # Очищаем переопределение
            admin_client.app.dependency_overrides.pop(get_component_parser_service, None)
    
    @pytest.mark.asyncio
    async def test_get_parse_status_forbidden(self, client):
        """Тест получения статуса парсинга обычным пользователем"""
        response = client.get("/api/components/parse/status")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_get_parse_status_unauthenticated(self, unauthenticated_client):
        """Тест получения статуса парсинга неавторизованным пользователем"""
        response = unauthenticated_client.get("/api/components/parse/status")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestStopParsing:
    """Тесты для остановки парсинга"""
    
    @pytest.mark.asyncio
    async def test_stop_parsing_success(self, admin_client):
        """Тест успешной остановки парсинга"""
        mock_service = AsyncMock()
        mock_service.stop_parsing = AsyncMock(return_value=True)
        
        # Переопределяем dependency
        admin_client.app.dependency_overrides[get_component_parser_service] = lambda: mock_service
        
        try:
            response = admin_client.post("/api/components/parse/stop")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert "message" in data
            assert "status" in data
            assert data["status"] == "stopping"
        finally:
            # Очищаем переопределение
            admin_client.app.dependency_overrides.pop(get_component_parser_service, None)
    
    @pytest.mark.asyncio
    async def test_stop_parsing_not_running(self, admin_client):
        """Тест остановки парсинга, когда он не запущен"""
        mock_service = AsyncMock()
        mock_service.stop_parsing = AsyncMock(return_value=False)
        
        # Переопределяем dependency
        admin_client.app.dependency_overrides[get_component_parser_service] = lambda: mock_service
        
        try:
            response = admin_client.post("/api/components/parse/stop")
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "не запущен" in response.json()["detail"].lower()
        finally:
            # Очищаем переопределение
            admin_client.app.dependency_overrides.pop(get_component_parser_service, None)
    
    @pytest.mark.asyncio
    async def test_stop_parsing_forbidden(self, client):
        """Тест остановки парсинга обычным пользователем"""
        response = client.post("/api/components/parse/stop")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_stop_parsing_unauthenticated(self, unauthenticated_client):
        """Тест остановки парсинга неавторизованным пользователем"""
        response = unauthenticated_client.post("/api/components/parse/stop")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

