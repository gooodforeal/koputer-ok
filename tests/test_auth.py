"""
Тесты для эндпоинтов auth
"""
import pytest
from fastapi import status
from unittest.mock import patch, AsyncMock, MagicMock
from datetime import timedelta
from app.models.user import UserRole
from app.schemas.auth import GoogleUserInfo


class TestGoogleAuth:
    """Тесты для Google OAuth авторизации"""
    
    @pytest.mark.asyncio
    async def test_google_auth_init(self, unauthenticated_client):
        """Тест инициации Google OAuth авторизации"""
        response = unauthenticated_client.get("/auth/google")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "auth_url" in data
        assert "accounts.google.com" in data["auth_url"]
        assert "oauth2" in data["auth_url"]
        assert "client_id" in data["auth_url"]
        assert "redirect_uri" in data["auth_url"]
    
    @pytest.mark.asyncio
    async def test_google_callback_success(self, unauthenticated_client, db_session):
        """Тест успешного callback от Google"""
        # Мокируем внешние API
        mock_google_user = GoogleUserInfo(
            id="12345",
            email="test@example.com",
            name="Test User",
            picture="https://example.com/pic.jpg",
            verified_email=True
        )
        
        with patch("app.routers.auth.exchange_code_for_token", new_callable=AsyncMock) as mock_exchange:
            with patch("app.routers.auth.get_google_user_info", new_callable=AsyncMock) as mock_get_user:
                with patch("app.config.settings") as mock_settings:
                    mock_settings.frontend_url = "http://localhost:3000"
                    mock_exchange.return_value = "access_token_123"
                    mock_get_user.return_value = mock_google_user
                    
                    response = unauthenticated_client.get("/auth/google/callback?code=test_code", follow_redirects=False)
                    
                    # Должно быть редирект
                    assert response.status_code in [status.HTTP_307_TEMPORARY_REDIRECT, status.HTTP_302_FOUND, status.HTTP_303_SEE_OTHER]
                    location = response.headers.get("location", "")
                    assert location
                    assert "token=" in location or "/auth/callback" in location
        
        # Проверяем, что пользователь был создан в БД
        from app.repositories import UserRepository
        user_repo = UserRepository(db_session)
        user = await user_repo.get_by_email(email="test@example.com")
        assert user is not None
        assert user.email == "test@example.com"
        assert user.google_id == "12345"
    
    @pytest.mark.asyncio
    async def test_google_callback_error_exchange_token(self, unauthenticated_client):
        """Тест обработки ошибки при обмене кода на токен"""
        with patch("app.routers.auth.exchange_code_for_token", new_callable=AsyncMock) as mock_exchange:
            with patch("app.config.settings") as mock_settings:
                mock_settings.frontend_url = "http://localhost:3000"
                mock_exchange.side_effect = Exception("Token exchange failed")
                
                response = unauthenticated_client.get("/auth/google/callback?code=test_code", follow_redirects=False)
                
                # Должен быть редирект на страницу ошибки
                assert response.status_code in [status.HTTP_307_TEMPORARY_REDIRECT, status.HTTP_302_FOUND, status.HTTP_303_SEE_OTHER]
                location = response.headers.get("location", "")
                assert location
                assert "error" in location.lower() or "/auth/error" in location
    
    @pytest.mark.asyncio
    async def test_google_callback_error_get_user_info(self, unauthenticated_client):
        """Тест обработки ошибки при получении информации о пользователе"""
        with patch("app.routers.auth.exchange_code_for_token", new_callable=AsyncMock) as mock_exchange:
            with patch("app.routers.auth.get_google_user_info", new_callable=AsyncMock) as mock_get_user:
                with patch("app.config.settings") as mock_settings:
                    mock_settings.frontend_url = "http://localhost:3000"
                    mock_exchange.return_value = "access_token_123"
                    mock_get_user.side_effect = Exception("Failed to get user info")
                    
                    response = unauthenticated_client.get("/auth/google/callback?code=test_code", follow_redirects=False)
                    
                    # Должен быть редирект на страницу ошибки
                    assert response.status_code in [status.HTTP_307_TEMPORARY_REDIRECT, status.HTTP_302_FOUND, status.HTTP_303_SEE_OTHER]
                    location = response.headers.get("location", "")
                    assert location
                    assert "error" in location.lower() or "/auth/error" in location


class TestTelegramAuth:
    """Тесты для Telegram авторизации"""
    
    @pytest.mark.asyncio
    async def test_telegram_auth_init(self, unauthenticated_client, mock_redis_service):
        """Тест инициации Telegram авторизации"""
        # Мокируем auth_token_storage
        mock_token = "test_auth_token_123"
        
        with patch("app.routers.auth.auth_token_storage.create_token", new_callable=AsyncMock) as mock_create:
            mock_create.return_value = mock_token
            
            response = unauthenticated_client.get("/auth/telegram/init")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["auth_token"] == mock_token
            assert "bot_url" in data
            assert "https://t.me" in data["bot_url"]
            assert mock_token in data["bot_url"]
            assert "bot_username" in data
            assert data["expires_in"] == 300
    
    @pytest.mark.asyncio
    async def test_telegram_authorize_success(self, unauthenticated_client, db_session, mock_redis_service):
        """Тест успешной авторизации через Telegram"""
        auth_token = "test_auth_token_123"
        telegram_id = "123456789"
        
        # Создаем данные токена
        token_data = {
            "created_at": "2024-01-01T00:00:00",
            "expires_at": "2024-01-01T00:10:00",
            "telegram_id": None,
            "used": False
        }
        
        # Мокируем методы auth_token_storage
        with patch("app.routers.auth.auth_token_storage.get_token_data", new_callable=AsyncMock) as mock_get_token:
            with patch("app.routers.auth.auth_token_storage.link_telegram_user", new_callable=AsyncMock) as mock_link:
                with patch("app.routers.auth.auth_token_storage.update_token_data", new_callable=AsyncMock) as mock_update:
                    mock_get_token.return_value = token_data
                    mock_link.return_value = True
                    mock_update.return_value = True
                    
                    request_data = {
                        "auth_token": auth_token,
                        "telegram_id": telegram_id,
                        "username": "testuser",
                        "first_name": "Test",
                        "last_name": "User",
                        "photo_url": "https://example.com/photo.jpg"
                    }
                    
                    response = unauthenticated_client.post("/auth/telegram/authorize", json=request_data)
                    
                    assert response.status_code == status.HTTP_200_OK
                    data = response.json()
                    assert data["status"] == "success"
                    assert data["message"] == "Authorization completed"
        
        # Проверяем, что пользователь был создан в БД
        from app.repositories import UserRepository
        user_repo = UserRepository(db_session)
        user = await user_repo.get_by_telegram_id(telegram_id=telegram_id)
        assert user is not None
        assert user.telegram_id == telegram_id  # telegram_id хранится как строка
    
    @pytest.mark.asyncio
    async def test_telegram_authorize_token_not_found(self, unauthenticated_client, mock_redis_service):
        """Тест авторизации с несуществующим токеном"""
        auth_token = "invalid_token"
        
        with patch("app.routers.auth.auth_token_storage.get_token_data", new_callable=AsyncMock) as mock_get_token:
            mock_get_token.return_value = None
            
            request_data = {
                "auth_token": auth_token,
                "telegram_id": "123456789",
                "first_name": "Test"
            }
            
            response = unauthenticated_client.post("/auth/telegram/authorize", json=request_data)
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert "Token not found or expired" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_telegram_authorize_token_already_used(self, unauthenticated_client, mock_redis_service):
        """Тест авторизации с уже использованным токеном"""
        auth_token = "used_token"
        
        token_data = {
            "created_at": "2024-01-01T00:00:00",
            "expires_at": "2024-01-01T00:10:00",
            "telegram_id": None,
            "used": True
        }
        
        with patch("app.routers.auth.auth_token_storage.get_token_data", new_callable=AsyncMock) as mock_get_token:
            mock_get_token.return_value = token_data
            
            request_data = {
                "auth_token": auth_token,
                "telegram_id": "123456789",
                "first_name": "Test"
            }
            
            response = unauthenticated_client.post("/auth/telegram/authorize", json=request_data)
            
            assert response.status_code == status.HTTP_400_BAD_REQUEST
            assert "Token already used" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_telegram_authorize_link_failed(self, unauthenticated_client, mock_redis_service):
        """Тест авторизации при неудачной привязке токена к пользователю"""
        auth_token = "test_token"
        
        token_data = {
            "created_at": "2024-01-01T00:00:00",
            "expires_at": "2024-01-01T00:10:00",
            "telegram_id": None,
            "used": False
        }
        
        with patch("app.routers.auth.auth_token_storage.get_token_data", new_callable=AsyncMock) as mock_get_token:
            with patch("app.routers.auth.auth_token_storage.link_telegram_user", new_callable=AsyncMock) as mock_link:
                mock_get_token.return_value = token_data
                mock_link.return_value = False
                
                request_data = {
                    "auth_token": auth_token,
                    "telegram_id": "123456789",
                    "first_name": "Test"
                }
                
                response = unauthenticated_client.post("/auth/telegram/authorize", json=request_data)
                
                assert response.status_code == status.HTTP_400_BAD_REQUEST
                assert "Failed to link token" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_telegram_authorize_save_jwt_failed(self, unauthenticated_client, db_session, mock_redis_service):
        """Тест авторизации при неудачном сохранении JWT токена"""
        auth_token = "test_token"
        
        token_data = {
            "created_at": "2024-01-01T00:00:00",
            "expires_at": "2024-01-01T00:10:00",
            "telegram_id": None,
            "used": False
        }
        
        with patch("app.routers.auth.auth_token_storage.get_token_data", new_callable=AsyncMock) as mock_get_token:
            with patch("app.routers.auth.auth_token_storage.link_telegram_user", new_callable=AsyncMock) as mock_link:
                with patch("app.routers.auth.auth_token_storage.update_token_data", new_callable=AsyncMock) as mock_update:
                    mock_get_token.return_value = token_data
                    mock_link.return_value = True
                    mock_update.return_value = False  # Не удалось сохранить JWT
                    
                    request_data = {
                        "auth_token": auth_token,
                        "telegram_id": "123456789",
                        "first_name": "Test"
                    }
                    
                    response = unauthenticated_client.post("/auth/telegram/authorize", json=request_data)
                    
                    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
                    assert "Failed to save JWT token" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_telegram_auth_check_pending(self, unauthenticated_client, mock_redis_service):
        """Тест проверки статуса авторизации - ожидание"""
        auth_token = "test_token"
        
        token_data = {
            "created_at": "2024-01-01T00:00:00",
            "expires_at": "2024-01-01T00:10:00",
            "telegram_id": None,
            "used": False
        }
        
        with patch("app.routers.auth.auth_token_storage.get_token_data", new_callable=AsyncMock) as mock_get_token:
            mock_get_token.return_value = token_data
            
            response = unauthenticated_client.get(f"/auth/telegram/check/{auth_token}")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["status"] == "pending"
            assert data["access_token"] is None
    
    @pytest.mark.asyncio
    async def test_telegram_auth_check_completed(self, unauthenticated_client, mock_redis_service):
        """Тест проверки статуса авторизации - завершено"""
        auth_token = "completed_token"
        
        token_data = {
            "created_at": "2024-01-01T00:00:00",
            "expires_at": "2024-01-01T00:10:00",
            "telegram_id": 123456789,
            "username": "testuser",
            "first_name": "Test",
            "last_name": "User",
            "used": True,
            "jwt_token": "jwt_token_123"
        }
        
        with patch("app.routers.auth.auth_token_storage.get_token_data", new_callable=AsyncMock) as mock_get_token:
            with patch("app.routers.auth.auth_token_storage.invalidate_token", new_callable=AsyncMock) as mock_invalidate:
                mock_get_token.return_value = token_data
                mock_invalidate.return_value = True
                
                response = unauthenticated_client.get(f"/auth/telegram/check/{auth_token}")
                
                assert response.status_code == status.HTTP_200_OK
                data = response.json()
                assert data["status"] == "completed"
                assert data["access_token"] == "jwt_token_123"
                assert data["telegram_id"] == "123456789"
                assert data["username"] == "testuser"
                assert data["first_name"] == "Test"
                assert data["last_name"] == "User"
    
    @pytest.mark.asyncio
    async def test_telegram_auth_check_token_not_found(self, unauthenticated_client, mock_redis_service):
        """Тест проверки несуществующего токена"""
        auth_token = "invalid_token"
        
        with patch("app.routers.auth.auth_token_storage.get_token_data", new_callable=AsyncMock) as mock_get_token:
            mock_get_token.return_value = None
            
            response = unauthenticated_client.get(f"/auth/telegram/check/{auth_token}")
            
            assert response.status_code == status.HTTP_404_NOT_FOUND
            assert "Token not found or expired" in response.json()["detail"]
    
    @pytest.mark.asyncio
    async def test_telegram_auth_check_used_but_no_jwt(self, unauthenticated_client, mock_redis_service):
        """Тест проверки токена который использован, но без JWT"""
        auth_token = "used_token_no_jwt"
        
        token_data = {
            "created_at": "2024-01-01T00:00:00",
            "expires_at": "2024-01-01T00:10:00",
            "telegram_id": 123456789,
            "used": True,
            "jwt_token": None
        }
        
        with patch("app.routers.auth.auth_token_storage.get_token_data", new_callable=AsyncMock) as mock_get_token:
            mock_get_token.return_value = token_data
            
            response = unauthenticated_client.get(f"/auth/telegram/check/{auth_token}")
            
            assert response.status_code == status.HTTP_200_OK
            data = response.json()
            assert data["status"] == "pending"


class TestGetCurrentUser:
    """Тесты для получения информации о текущем пользователе"""
    
    @pytest.mark.asyncio
    async def test_get_current_user_success(self, client, test_user):
        """Тест успешного получения информации о текущем пользователе"""
        response = client.get("/auth/me")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_user.id
        assert data["email"] == test_user.email
        assert data["name"] == test_user.name
        assert data["role"] == test_user.role.value
        assert data["is_active"] == test_user.is_active
    
    @pytest.mark.asyncio
    async def test_get_current_user_unauthenticated(self, unauthenticated_client):
        """Тест получения информации о текущем пользователе без авторизации"""
        response = unauthenticated_client.get("/auth/me")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestLogout:
    """Тесты для выхода из системы"""
    
    @pytest.mark.asyncio
    async def test_logout_success(self, client):
        """Тест успешного выхода из системы"""
        response = client.post("/auth/logout")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Successfully logged out"
    
    @pytest.mark.asyncio
    async def test_logout_unauthenticated(self, unauthenticated_client):
        """Тест выхода из системы без авторизации"""
        # Логаут должен работать для всех пользователей
        response = unauthenticated_client.post("/auth/logout")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["message"] == "Successfully logged out"

