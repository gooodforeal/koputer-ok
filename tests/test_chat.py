"""
Тесты для эндпоинтов chat
"""
import pytest
from fastapi import status
from app.models.chat import Chat, Message, ChatStatus
from app.repositories.chat_repository import ChatRepository
from app.schemas.chat import ChatCreate, MessageCreate, MessageCreateWithChatId


class TestCreateChat:
    """Тесты для создания чата"""
    
    @pytest.mark.asyncio
    async def test_create_chat_success(self, client, test_user):
        """Тест успешного создания чата"""
        chat_data = {
            "user_id": test_user.id,
            "status": "OPEN"
        }
        
        response = client.post("/api/chat/", json=chat_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["user_id"] == test_user.id
        assert data["status"] == "OPEN"
        assert data["is_active"] is True
        assert "id" in data
        assert "created_at" in data
        assert "messages" in data
    
    @pytest.mark.asyncio
    async def test_create_chat_when_exists(self, client, test_user, db_session):
        """Тест создания чата, когда он уже существует"""
        # Создаем чат напрямую в БД
        chat_repo = ChatRepository(db_session)
        existing_chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.OPEN
        ))
        await db_session.flush()
        
        # Пытаемся создать еще один чат
        chat_data = {
            "user_id": test_user.id,
            "status": "OPEN"
        }
        
        response = client.post("/api/chat/", json=chat_data)
        
        # Должен вернуться существующий чат
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == existing_chat.id
    
    @pytest.mark.asyncio
    async def test_create_chat_for_other_user_forbidden(self, client, test_user, test_user2):
        """Тест создания чата для другого пользователя"""
        chat_data = {
            "user_id": test_user2.id,
            "status": "OPEN"
        }
        
        response = client.post("/api/chat/", json=chat_data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "только для себя" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_create_chat_unauthenticated(self, unauthenticated_client, test_user):
        """Тест создания чата неавторизованным пользователем"""
        chat_data = {
            "user_id": test_user.id,
            "status": "OPEN"
        }
        
        response = unauthenticated_client.post("/api/chat/", json=chat_data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestGetMyChat:
    """Тесты для получения моего чата"""
    
    @pytest.mark.asyncio
    async def test_get_my_chat_success(self, client, test_user, db_session):
        """Тест успешного получения моего чата"""
        # Создаем чат
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.OPEN
        ))
        await db_session.flush()
        
        response = client.get("/api/chat/my")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == chat.id
        assert data["user_id"] == test_user.id
    
    @pytest.mark.asyncio
    async def test_get_my_chat_not_found(self, client):
        """Тест получения несуществующего чата"""
        response = client.get("/api/chat/my")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "не найден" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_get_my_chat_unauthenticated(self, unauthenticated_client):
        """Тест получения чата неавторизованным пользователем"""
        response = unauthenticated_client.get("/api/chat/my")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestGetChat:
    """Тесты для получения чата по ID"""
    
    @pytest.mark.asyncio
    async def test_get_chat_success(self, client, test_user, db_session):
        """Тест успешного получения чата по ID"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.OPEN
        ))
        await db_session.flush()
        
        response = client.get(f"/api/chat/{chat.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == chat.id
        assert data["user_id"] == test_user.id
    
    @pytest.mark.asyncio
    async def test_get_chat_not_found(self, client):
        """Тест получения несуществующего чата"""
        response = client.get("/api/chat/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_get_chat_forbidden_other_user(self, client, test_user, test_user2, db_session):
        """Тест получения чужого чата"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user2.id,
            status=ChatStatus.OPEN
        ))
        await db_session.flush()
        
        response = client.get(f"/api/chat/{chat.id}")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "нет доступа" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_get_chat_by_admin_success(self, admin_client, test_user, test_admin, db_session):
        """Тест получения чата администратором"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.OPEN
        ))
        await db_session.flush()
        
        response = admin_client.get(f"/api/chat/{chat.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == chat.id


class TestGetAdminChats:
    """Тесты для получения чатов администратора"""
    
    @pytest.mark.asyncio
    async def test_get_admin_chats_success(self, admin_client, test_user, test_admin, db_session):
        """Тест получения чатов администратора"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.OPEN
        ))
        await chat_repo.assign_admin_to_chat(chat.id, test_admin.id)
        await db_session.flush()
        
        response = admin_client.get("/api/chat/admin")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    @pytest.mark.asyncio
    async def test_get_admin_chats_super_admin(self, super_admin_client, test_user, db_session):
        """Тест получения всех активных чатов супер-админом"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.OPEN
        ))
        await db_session.flush()
        
        response = super_admin_client.get("/api/chat/admin")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    @pytest.mark.asyncio
    async def test_get_admin_chats_empty(self, admin_client):
        """Тест получения пустого списка чатов"""
        response = admin_client.get("/api/chat/admin")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_get_admin_chats_forbidden_for_user(self, client):
        """Тест получения чатов администратора обычным пользователем"""
        response = client.get("/api/chat/admin")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_get_admin_chats_unauthenticated(self, unauthenticated_client):
        """Тест получения чатов неавторизованным пользователем"""
        response = unauthenticated_client.get("/api/chat/admin")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestAssignAdminToChat:
    """Тесты для назначения администратора к чату"""
    
    @pytest.mark.asyncio
    async def test_assign_admin_success(self, admin_client, test_user, test_admin, db_session):
        """Тест успешного назначения администратора"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.OPEN
        ))
        await db_session.flush()
        
        assign_data = {
            "admin_id": test_admin.id
        }
        
        response = admin_client.post(f"/api/chat/{chat.id}/assign", json=assign_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["admin_id"] == test_admin.id
    
    @pytest.mark.asyncio
    async def test_assign_admin_not_found(self, admin_client, test_admin):
        """Тест назначения администратора несуществующему чату"""
        assign_data = {
            "admin_id": test_admin.id
        }
        
        response = admin_client.post("/api/chat/99999/assign", json=assign_data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_assign_admin_forbidden_for_user(self, client, test_user, test_admin, db_session):
        """Тест назначения администратора обычным пользователем"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.OPEN
        ))
        await db_session.flush()
        
        assign_data = {
            "admin_id": test_admin.id
        }
        
        response = client.post(f"/api/chat/{chat.id}/assign", json=assign_data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_assign_admin_unauthenticated(self, unauthenticated_client, test_user, db_session):
        """Тест назначения администратора неавторизованным пользователем"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.OPEN
        ))
        await db_session.flush()
        
        assign_data = {
            "admin_id": 1
        }
        
        response = unauthenticated_client.post(f"/api/chat/{chat.id}/assign", json=assign_data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestSendMessage:
    """Тесты для отправки сообщения"""
    
    @pytest.mark.asyncio
    async def test_send_message_success(self, client, test_user, db_session):
        """Тест успешной отправки сообщения"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.OPEN
        ))
        await db_session.flush()
        
        message_data = {
            "content": "Привет, это тестовое сообщение",
            "message_type": "text"
        }
        
        response = client.post(f"/api/chat/{chat.id}/messages", json=message_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["content"] == message_data["content"]
        assert data["chat_id"] == chat.id
        assert data["sender_id"] == test_user.id
        assert data["is_read"] is False
    
    @pytest.mark.asyncio
    async def test_send_message_chat_not_found(self, client):
        """Тест отправки сообщения в несуществующий чат"""
        message_data = {
            "content": "Тестовое сообщение",
            "message_type": "text"
        }
        
        response = client.post("/api/chat/99999/messages", json=message_data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_send_message_forbidden(self, client, test_user, test_user2, db_session):
        """Тест отправки сообщения в чужой чат"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user2.id,
            status=ChatStatus.OPEN
        ))
        await db_session.flush()
        
        message_data = {
            "content": "Тестовое сообщение",
            "message_type": "text"
        }
        
        response = client.post(f"/api/chat/{chat.id}/messages", json=message_data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_send_message_by_admin(self, admin_client, test_user, test_admin, db_session):
        """Тест отправки сообщения администратором"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.OPEN
        ))
        await chat_repo.assign_admin_to_chat(chat.id, test_admin.id)
        await db_session.flush()
        
        message_data = {
            "content": "Ответ администратора",
            "message_type": "text"
        }
        
        response = admin_client.post(f"/api/chat/{chat.id}/messages", json=message_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["sender_id"] == test_admin.id
    
    @pytest.mark.asyncio
    async def test_send_message_unauthenticated(self, unauthenticated_client, test_user, db_session):
        """Тест отправки сообщения неавторизованным пользователем"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.OPEN
        ))
        await db_session.flush()
        
        message_data = {
            "content": "Тестовое сообщение",
            "message_type": "text"
        }
        
        response = unauthenticated_client.post(f"/api/chat/{chat.id}/messages", json=message_data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestGetChatMessages:
    """Тесты для получения сообщений чата"""
    
    @pytest.mark.asyncio
    async def test_get_messages_success(self, client, test_user, db_session):
        """Тест успешного получения сообщений"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.OPEN
        ))
        
        # Создаем несколько сообщений
        await chat_repo.create_message(
            MessageCreateWithChatId(
                chat_id=chat.id,
                content="Первое сообщение",
                message_type="text"
            ),
            test_user.id
        )
        await chat_repo.create_message(
            MessageCreateWithChatId(
                chat_id=chat.id,
                content="Второе сообщение",
                message_type="text"
            ),
            test_user.id
        )
        await db_session.flush()
        
        response = client.get(f"/api/chat/{chat.id}/messages")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 2
    
    @pytest.mark.asyncio
    async def test_get_messages_with_pagination(self, client, test_user, db_session):
        """Тест получения сообщений с пагинацией"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.OPEN
        ))
        
        # Создаем несколько сообщений
        for i in range(5):
            await chat_repo.create_message(
                MessageCreateWithChatId(
                    chat_id=chat.id,
                    content=f"Сообщение {i+1}",
                    message_type="text"
                ),
                test_user.id
            )
        await db_session.flush()
        
        response = client.get(f"/api/chat/{chat.id}/messages?limit=2&offset=0")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) <= 2
    
    @pytest.mark.asyncio
    async def test_get_messages_chat_not_found(self, client):
        """Тест получения сообщений несуществующего чата"""
        response = client.get("/api/chat/99999/messages")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_get_messages_forbidden(self, client, test_user, test_user2, db_session):
        """Тест получения сообщений чужого чата"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user2.id,
            status=ChatStatus.OPEN
        ))
        await db_session.flush()
        
        response = client.get(f"/api/chat/{chat.id}/messages")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_get_messages_unauthenticated(self, unauthenticated_client, test_user, db_session):
        """Тест получения сообщений неавторизованным пользователем"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.OPEN
        ))
        await db_session.flush()
        
        response = unauthenticated_client.get(f"/api/chat/{chat.id}/messages")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestMarkChatAsRead:
    """Тесты для отметки чата как прочитанного"""
    
    @pytest.mark.asyncio
    async def test_mark_as_read_success(self, client, test_user, db_session):
        """Тест успешной отметки чата как прочитанного"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.OPEN
        ))
        await db_session.flush()
        
        response = client.post(f"/api/chat/{chat.id}/read")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "message" in data
    
    @pytest.mark.asyncio
    async def test_mark_as_read_chat_not_found(self, client):
        """Тест отметки несуществующего чата"""
        response = client.post("/api/chat/99999/read")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_mark_as_read_forbidden(self, client, test_user, test_user2, db_session):
        """Тест отметки чужого чата"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user2.id,
            status=ChatStatus.OPEN
        ))
        await db_session.flush()
        
        response = client.post(f"/api/chat/{chat.id}/read")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_mark_as_read_unauthenticated(self, unauthenticated_client, test_user, db_session):
        """Тест отметки чата неавторизованным пользователем"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.OPEN
        ))
        await db_session.flush()
        
        response = unauthenticated_client.post(f"/api/chat/{chat.id}/read")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestGetMyChatsSummary:
    """Тесты для получения краткой информации о моих чатах"""
    
    @pytest.mark.asyncio
    async def test_get_my_chats_summary_success(self, client, test_user, db_session):
        """Тест успешного получения краткой информации"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.OPEN
        ))
        await db_session.flush()
        
        response = client.get("/api/chat/summary/my")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        if data:
            assert "id" in data[0]
            assert "is_active" in data[0]
    
    @pytest.mark.asyncio
    async def test_get_my_chats_summary_empty(self, client):
        """Тест получения пустого списка"""
        response = client.get("/api/chat/summary/my")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_get_my_chats_summary_unauthenticated(self, unauthenticated_client):
        """Тест получения краткой информации неавторизованным пользователем"""
        response = unauthenticated_client.get("/api/chat/summary/my")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestGetAdminChatsSummary:
    """Тесты для получения краткой информации о чатах администратора"""
    
    @pytest.mark.asyncio
    async def test_get_admin_chats_summary_success(self, admin_client, test_user, test_admin, db_session):
        """Тест успешного получения краткой информации"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.OPEN
        ))
        await chat_repo.assign_admin_to_chat(chat.id, test_admin.id)
        await db_session.flush()
        
        response = admin_client.get("/api/chat/summary/admin")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        if data:
            assert "id" in data[0]
            assert "user_name" in data[0]
            assert "unread_count" in data[0]
    
    @pytest.mark.asyncio
    async def test_get_admin_chats_summary_super_admin(self, super_admin_client, test_user, db_session):
        """Тест получения краткой информации супер-админом"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.OPEN
        ))
        await db_session.flush()
        
        response = super_admin_client.get("/api/chat/summary/admin")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_get_admin_chats_summary_forbidden_for_user(self, client):
        """Тест получения краткой информации обычным пользователем"""
        response = client.get("/api/chat/summary/admin")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_get_admin_chats_summary_unauthenticated(self, unauthenticated_client):
        """Тест получения краткой информации неавторизованным пользователем"""
        response = unauthenticated_client.get("/api/chat/summary/admin")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestUpdateChatStatus:
    """Тесты для обновления статуса чата"""
    
    @pytest.mark.asyncio
    async def test_update_status_success(self, admin_client, test_user, test_admin, db_session):
        """Тест успешного обновления статуса"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.OPEN
        ))
        await chat_repo.assign_admin_to_chat(chat.id, test_admin.id)
        await db_session.flush()
        
        update_data = {
            "status": "IN_PROGRESS"
        }
        
        response = admin_client.patch(f"/api/chat/{chat.id}/status", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "IN_PROGRESS"
    
    @pytest.mark.asyncio
    async def test_update_status_chat_not_found(self, admin_client, test_admin):
        """Тест обновления статуса несуществующего чата"""
        update_data = {
            "status": "IN_PROGRESS"
        }
        
        response = admin_client.patch("/api/chat/99999/status", json=update_data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_update_status_forbidden_admin_other_chat(self, admin_client, test_user, test_admin, db_session):
        """Тест обновления статуса чужого чата администратором"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.OPEN
        ))
        # Не назначаем администратора
        await db_session.flush()
        
        update_data = {
            "status": "IN_PROGRESS"
        }
        
        response = admin_client.patch(f"/api/chat/{chat.id}/status", json=update_data)
        
        # Администратор не может изменять статус чата, если он ему не назначен
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_update_status_super_admin_success(self, super_admin_client, test_user, db_session):
        """Тест обновления статуса супер-админом"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.OPEN
        ))
        await db_session.flush()
        
        update_data = {
            "status": "IN_PROGRESS"
        }
        
        response = super_admin_client.patch(f"/api/chat/{chat.id}/status", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "IN_PROGRESS"
    
    @pytest.mark.asyncio
    async def test_update_status_forbidden_for_user(self, client, test_user, db_session):
        """Тест обновления статуса обычным пользователем"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.OPEN
        ))
        await db_session.flush()
        
        update_data = {
            "status": "IN_PROGRESS"
        }
        
        response = client.patch(f"/api/chat/{chat.id}/status", json=update_data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_update_status_unauthenticated(self, unauthenticated_client, test_user, db_session):
        """Тест обновления статуса неавторизованным пользователем"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.OPEN
        ))
        await db_session.flush()
        
        update_data = {
            "status": "IN_PROGRESS"
        }
        
        response = unauthenticated_client.patch(f"/api/chat/{chat.id}/status", json=update_data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestCloseChat:
    """Тесты для закрытия чата"""
    
    @pytest.mark.asyncio
    async def test_close_chat_success(self, admin_client, test_user, test_admin, db_session):
        """Тест успешного закрытия чата"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.OPEN
        ))
        await chat_repo.assign_admin_to_chat(chat.id, test_admin.id)
        await db_session.flush()
        
        response = admin_client.post(f"/api/chat/{chat.id}/close")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "CLOSED"
    
    @pytest.mark.asyncio
    async def test_close_chat_not_found(self, admin_client):
        """Тест закрытия несуществующего чата"""
        response = admin_client.post("/api/chat/99999/close")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_close_chat_forbidden_admin_other_chat(self, admin_client, test_user, db_session):
        """Тест закрытия чужого чата администратором"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.OPEN
        ))
        await db_session.flush()
        
        response = admin_client.post(f"/api/chat/{chat.id}/close")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_close_chat_super_admin_success(self, super_admin_client, test_user, db_session):
        """Тест закрытия чата супер-админом"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.OPEN
        ))
        await db_session.flush()
        
        response = super_admin_client.post(f"/api/chat/{chat.id}/close")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "CLOSED"
    
    @pytest.mark.asyncio
    async def test_close_chat_forbidden_for_user(self, client, test_user, db_session):
        """Тест закрытия чата обычным пользователем"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.OPEN
        ))
        await db_session.flush()
        
        response = client.post(f"/api/chat/{chat.id}/close")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_close_chat_unauthenticated(self, unauthenticated_client, test_user, db_session):
        """Тест закрытия чата неавторизованным пользователем"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.OPEN
        ))
        await db_session.flush()
        
        response = unauthenticated_client.post(f"/api/chat/{chat.id}/close")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestReopenChat:
    """Тесты для переоткрытия чата"""
    
    @pytest.mark.asyncio
    async def test_reopen_chat_success(self, admin_client, test_user, test_admin, db_session):
        """Тест успешного переоткрытия чата"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.CLOSED
        ))
        await chat_repo.assign_admin_to_chat(chat.id, test_admin.id)
        await db_session.flush()
        
        response = admin_client.post(f"/api/chat/{chat.id}/reopen")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "OPEN"
    
    @pytest.mark.asyncio
    async def test_reopen_chat_not_found(self, admin_client):
        """Тест переоткрытия несуществующего чата"""
        response = admin_client.post("/api/chat/99999/reopen")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_reopen_chat_forbidden_admin_other_chat(self, admin_client, test_user, db_session):
        """Тест переоткрытия чужого чата администратором"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.CLOSED
        ))
        await db_session.flush()
        
        response = admin_client.post(f"/api/chat/{chat.id}/reopen")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_reopen_chat_super_admin_success(self, super_admin_client, test_user, db_session):
        """Тест переоткрытия чата супер-админом"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.CLOSED
        ))
        await db_session.flush()
        
        response = super_admin_client.post(f"/api/chat/{chat.id}/reopen")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "OPEN"
    
    @pytest.mark.asyncio
    async def test_reopen_chat_forbidden_for_user(self, client, test_user, db_session):
        """Тест переоткрытия чата обычным пользователем"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.CLOSED
        ))
        await db_session.flush()
        
        response = client.post(f"/api/chat/{chat.id}/reopen")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_reopen_chat_unauthenticated(self, unauthenticated_client, test_user, db_session):
        """Тест переоткрытия чата неавторизованным пользователем"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.CLOSED
        ))
        await db_session.flush()
        
        response = unauthenticated_client.post(f"/api/chat/{chat.id}/reopen")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestStartWorkingOnChat:
    """Тесты для начала работы с чатом"""
    
    @pytest.mark.asyncio
    async def test_start_working_success(self, admin_client, test_user, test_admin, db_session):
        """Тест успешного начала работы с чатом"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.OPEN
        ))
        await db_session.flush()
        
        response = admin_client.post(f"/api/chat/{chat.id}/start-working")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "IN_PROGRESS"
        # Администратор должен быть автоматически назначен
        assert data["admin_id"] == test_admin.id
    
    @pytest.mark.asyncio
    async def test_start_working_with_assigned_admin(self, admin_client, test_user, test_admin, db_session):
        """Тест начала работы с чатом, где администратор уже назначен"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.OPEN
        ))
        await chat_repo.assign_admin_to_chat(chat.id, test_admin.id)
        await db_session.flush()
        
        response = admin_client.post(f"/api/chat/{chat.id}/start-working")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "IN_PROGRESS"
        assert data["admin_id"] == test_admin.id
    
    @pytest.mark.asyncio
    async def test_start_working_not_found(self, admin_client):
        """Тест начала работы с несуществующим чатом"""
        response = admin_client.post("/api/chat/99999/start-working")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_start_working_forbidden_admin_other_chat(self, admin_client, test_user, test_admin, test_user2, db_session):
        """Тест начала работы с чужим чатом администратором"""
        from app.models.user import User, UserRole
        
        # Создаем второго администратора
        admin2 = User(
            email="admin2@example.com",
            name="Admin 2",
            picture="https://example.com/admin2.jpg",
            google_id="admin2_123",
            is_active=True,
            role=UserRole.ADMIN
        )
        db_session.add(admin2)
        await db_session.commit()
        await db_session.refresh(admin2)
        
        # Создаем чат и назначаем другого администратора
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.OPEN
        ))
        await chat_repo.assign_admin_to_chat(chat.id, admin2.id)
        await db_session.flush()
        
        # Текущий администратор не может взять в работу чужой чат
        response = admin_client.post(f"/api/chat/{chat.id}/start-working")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_start_working_super_admin_success(self, super_admin_client, test_user, db_session):
        """Тест начала работы с чатом супер-админом"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.OPEN
        ))
        await db_session.flush()
        
        response = super_admin_client.post(f"/api/chat/{chat.id}/start-working")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "IN_PROGRESS"
    
    @pytest.mark.asyncio
    async def test_start_working_forbidden_for_user(self, client, test_user, db_session):
        """Тест начала работы с чатом обычным пользователем"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.OPEN
        ))
        await db_session.flush()
        
        response = client.post(f"/api/chat/{chat.id}/start-working")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_start_working_unauthenticated(self, unauthenticated_client, test_user, db_session):
        """Тест начала работы с чатом неавторизованным пользователем"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.OPEN
        ))
        await db_session.flush()
        
        response = unauthenticated_client.post(f"/api/chat/{chat.id}/start-working")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestGetChatsByStatus:
    """Тесты для получения чатов по статусу"""
    
    @pytest.mark.asyncio
    async def test_get_chats_by_status_open(self, admin_client, test_user, test_admin, db_session):
        """Тест получения открытых чатов"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.OPEN
        ))
        await chat_repo.assign_admin_to_chat(chat.id, test_admin.id)
        await db_session.flush()
        
        response = admin_client.get("/api/chat/admin/by-status/OPEN")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_get_chats_by_status_in_progress(self, admin_client, test_user, test_admin, db_session):
        """Тест получения чатов в работе"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.OPEN
        ))
        await chat_repo.assign_admin_to_chat(chat.id, test_admin.id)
        await chat_repo.update_chat_status(chat.id, ChatStatus.IN_PROGRESS, test_admin.id)
        await db_session.flush()
        
        response = admin_client.get("/api/chat/admin/by-status/IN_PROGRESS")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_get_chats_by_status_closed(self, admin_client, test_user, test_admin, db_session):
        """Тест получения закрытых чатов"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.OPEN
        ))
        await chat_repo.assign_admin_to_chat(chat.id, test_admin.id)
        await chat_repo.close_chat(chat.id, test_admin.id)
        await db_session.flush()
        
        response = admin_client.get("/api/chat/admin/by-status/CLOSED")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_get_chats_by_status_super_admin(self, super_admin_client, test_user, db_session):
        """Тест получения чатов по статусу супер-админом"""
        chat_repo = ChatRepository(db_session)
        chat = await chat_repo.create_chat(ChatCreate(
            user_id=test_user.id,
            status=ChatStatus.OPEN
        ))
        await db_session.flush()
        
        response = super_admin_client.get("/api/chat/admin/by-status/OPEN")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_get_chats_by_status_forbidden_for_user(self, client):
        """Тест получения чатов по статусу обычным пользователем"""
        response = client.get("/api/chat/admin/by-status/OPEN")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_get_chats_by_status_unauthenticated(self, unauthenticated_client):
        """Тест получения чатов по статусу неавторизованным пользователем"""
        response = unauthenticated_client.get("/api/chat/admin/by-status/OPEN")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

