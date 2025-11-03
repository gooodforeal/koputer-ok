"""
Тесты для эндпоинтов users
"""
import pytest
from fastapi import status


class TestGetUserProfile:
    """Тесты для получения профиля пользователя"""
    
    @pytest.mark.asyncio
    async def test_get_user_profile_success(self, client, test_user):
        """Тест успешного получения профиля"""
        response = client.get("/users/profile")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["name"] == test_user.name
        assert data["role"] == test_user.role.value
        assert data["is_active"] == test_user.is_active
    
    @pytest.mark.asyncio
    async def test_get_user_profile_unauthenticated(self, unauthenticated_client):
        """Тест получения профиля неавторизованным пользователем"""
        response = unauthenticated_client.get("/users/profile")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestProtectedRoute:
    """Тесты для защищенного маршрута"""
    
    @pytest.mark.asyncio
    async def test_protected_route_success(self, client, test_user):
        """Тест успешного доступа к защищенному маршруту"""
        response = client.get("/users/protected")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == f"Hello {test_user.name}!"
        assert data["user_id"] == test_user.id
        assert data["email"] == test_user.email
    
    @pytest.mark.asyncio
    async def test_protected_route_unauthenticated(self, unauthenticated_client):
        """Тест доступа к защищенному маршруту неавторизованным пользователем"""
        response = unauthenticated_client.get("/users/protected")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestGetUsers:
    """Тесты для получения списка всех пользователей"""
    
    @pytest.mark.asyncio
    async def test_get_users_success(self, super_admin_client, test_user, test_user2):
        """Тест успешного получения списка пользователей"""
        response = super_admin_client.get("/users/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2
        
        # Проверяем структуру данных
        if data:
            user = data[0]
            assert "id" in user
            assert "email" in user
            assert "name" in user
            assert "role" in user
            assert "is_active" in user
    
    @pytest.mark.asyncio
    async def test_get_users_with_pagination(self, super_admin_client, test_user, test_user2):
        """Тест получения списка пользователей с пагинацией"""
        response = super_admin_client.get("/users/?skip=0&limit=1")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) <= 1
    
    @pytest.mark.asyncio
    async def test_get_users_forbidden_for_admin(self, admin_client):
        """Тест получения списка пользователей администратором"""
        response = admin_client.get("/users/")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_get_users_forbidden_for_user(self, client):
        """Тест получения списка пользователей обычным пользователем"""
        response = client.get("/users/")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_get_users_unauthenticated(self, unauthenticated_client):
        """Тест получения списка пользователей неавторизованным пользователем"""
        response = unauthenticated_client.get("/users/")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestSearchUsers:
    """Тесты для поиска пользователей"""
    
    @pytest.mark.asyncio
    async def test_search_users_success(self, super_admin_client, test_user, test_user2):
        """Тест успешного поиска пользователей"""
        response = super_admin_client.get("/users/search?q=Test")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "users" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
        assert "total_pages" in data
        assert isinstance(data["users"], list)
    
    @pytest.mark.asyncio
    async def test_search_users_with_pagination(self, super_admin_client, test_user, test_user2):
        """Тест поиска пользователей с пагинацией"""
        response = super_admin_client.get("/users/search?q=&page=1&per_page=1")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["page"] == 1
        assert data["per_page"] == 1
        assert len(data["users"]) <= 1
    
    @pytest.mark.asyncio
    async def test_search_users_with_role_filter(self, super_admin_client, test_user, test_user2):
        """Тест поиска пользователей с фильтром по роли"""
        response = super_admin_client.get("/users/search?role=USER")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data["users"], list)
        # Проверяем, что все пользователи имеют роль USER
        for user in data["users"]:
            assert user["role"] == "USER"
    
    @pytest.mark.asyncio
    async def test_search_users_with_active_filter(self, super_admin_client, test_user):
        """Тест поиска пользователей с фильтром по активности"""
        response = super_admin_client.get("/users/search?is_active=true")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data["users"], list)
        # Проверяем, что все пользователи активны
        for user in data["users"]:
            assert user["is_active"] is True
    
    @pytest.mark.asyncio
    async def test_search_users_forbidden_for_admin(self, admin_client):
        """Тест поиска пользователей администратором"""
        response = admin_client.get("/users/search")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_search_users_forbidden_for_user(self, client):
        """Тест поиска пользователей обычным пользователем"""
        response = client.get("/users/search")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_search_users_unauthenticated(self, unauthenticated_client):
        """Тест поиска пользователей неавторизованным пользователем"""
        response = unauthenticated_client.get("/users/search")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestGetUserStats:
    """Тесты для получения статистики пользователей"""
    
    @pytest.mark.asyncio
    async def test_get_user_stats_empty(self, client):
        """Тест получения статистики при отсутствии пользователей"""
        response = client.get("/users/stats")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "total_users" in data
        assert "active_users" in data
        assert "inactive_users" in data
        assert data["total_users"] >= 0
        assert data["active_users"] >= 0
        assert data["inactive_users"] >= 0
    
    @pytest.mark.asyncio
    async def test_get_user_stats_with_data(self, client, test_user, test_user2):
        """Тест получения статистики с данными"""
        response = client.get("/users/stats")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_users"] >= 2
        assert data["active_users"] >= 2
        assert data["total_users"] == data["active_users"] + data["inactive_users"]
    
    @pytest.mark.asyncio
    async def test_get_user_stats_unauthenticated(self, unauthenticated_client):
        """Тест получения статистики неавторизованным пользователем"""
        response = unauthenticated_client.get("/users/stats")
        
        # Статистика должна быть доступна всем
        assert response.status_code == status.HTTP_200_OK


class TestUpdateUserProfile:
    """Тесты для обновления профиля пользователя"""
    
    @pytest.mark.asyncio
    async def test_update_user_profile_success(self, client, test_user):
        """Тест успешного обновления профиля"""
        update_data = {
            "name": "Updated Name",
            "email": "updated@example.com"
        }
        
        response = client.put("/users/profile", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["email"] == update_data["email"]
        assert data["id"] == test_user.id
    
    @pytest.mark.asyncio
    async def test_update_user_profile_partial(self, client, test_user):
        """Тест частичного обновления профиля"""
        update_data = {
            "name": "New Name",
            "email": None,
            "picture": None
        }
        
        response = client.put("/users/profile", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == update_data["name"]
        assert data["id"] == test_user.id
    
    @pytest.mark.asyncio
    async def test_update_user_profile_with_picture(self, client, test_user):
        """Тест обновления профиля с картинкой"""
        update_data = {
            "name": test_user.name,  # Сохраняем текущее имя
            "picture": "https://example.com/new-pic.jpg",
            "email": test_user.email  # Сохраняем текущий email
        }
        
        response = client.put("/users/profile", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["picture"] == update_data["picture"]
    
    @pytest.mark.asyncio
    async def test_update_user_profile_invalid_email(self, client):
        """Тест обновления профиля с невалидным email"""
        update_data = {
            "email": "invalid-email"
        }
        
        response = client.put("/users/profile", json=update_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_update_user_profile_unauthenticated(self, unauthenticated_client):
        """Тест обновления профиля неавторизованным пользователем"""
        update_data = {
            "name": "New Name"
        }
        
        response = unauthenticated_client.put("/users/profile", json=update_data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestUpdateUserRole:
    """Тесты для обновления роли пользователя"""
    
    @pytest.mark.asyncio
    async def test_update_user_role_success(self, super_admin_client, test_user):
        """Тест успешного обновления роли пользователя"""
        update_data = {
            "role": "ADMIN",
            "name": None,
            "email": None,
            "picture": None,
            "is_active": None
        }
        
        response = super_admin_client.put(f"/users/{test_user.id}/role", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["role"] == "ADMIN"
        assert data["id"] == test_user.id
    
    @pytest.mark.asyncio
    async def test_update_user_role_to_user(self, super_admin_client, test_admin):
        """Тест изменения роли администратора на пользователя"""
        update_data = {
            "role": "USER",
            "name": None,
            "email": None,
            "picture": None,
            "is_active": None
        }
        
        response = super_admin_client.put(f"/users/{test_admin.id}/role", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["role"] == "USER"
    
    @pytest.mark.asyncio
    async def test_update_user_role_super_admin_forbidden(self, super_admin_client, test_user):
        """Тест попытки назначить роль супер-администратора"""
        update_data = {
            "role": "SUPER_ADMIN",
            "name": None,
            "email": None,
            "picture": None,
            "is_active": None
        }
        
        response = super_admin_client.put(f"/users/{test_user.id}/role", json=update_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "супер-администратора" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_update_user_role_not_found(self, super_admin_client):
        """Тест обновления роли несуществующего пользователя"""
        update_data = {
            "role": "ADMIN",
            "name": None,
            "email": None,
            "picture": None,
            "is_active": None
        }
        
        response = super_admin_client.put("/users/99999/role", json=update_data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        detail = response.json().get("detail", "").lower()
        assert "не найден" in detail or "not found" in detail
    
    @pytest.mark.asyncio
    async def test_update_user_role_forbidden_for_admin(self, admin_client, test_user):
        """Тест обновления роли администратором"""
        update_data = {
            "role": "ADMIN"
        }
        
        response = admin_client.put(f"/users/{test_user.id}/role", json=update_data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_update_user_role_forbidden_for_user(self, client, test_user2):
        """Тест обновления роли обычным пользователем"""
        update_data = {
            "role": "ADMIN"
        }
        
        response = client.put(f"/users/{test_user2.id}/role", json=update_data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_update_user_role_unauthenticated(self, unauthenticated_client, test_user):
        """Тест обновления роли неавторизованным пользователем"""
        update_data = {
            "role": "ADMIN"
        }
        
        response = unauthenticated_client.put(f"/users/{test_user.id}/role", json=update_data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

