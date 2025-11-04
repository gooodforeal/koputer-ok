"""
Тесты для эндпоинтов feedback
"""
import pytest
from fastapi import status
from app.models.feedback import FeedbackType, FeedbackStatus


class TestCreateFeedback:
    """Тесты для создания отзыва"""
    
    @pytest.mark.asyncio
    async def test_create_feedback_success(self, client, test_user):
        """Тест успешного создания отзыва"""
        feedback_data = {
            "title": "Новый отзыв",
            "description": "Это описание нового отзыва длиной более 10 символов",
            "type": "GENERAL",
            "rating": 5
        }
        
        response = client.post("/api/feedback/", json=feedback_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == feedback_data["title"]
        assert data["description"] == feedback_data["description"]
        assert data["type"] == feedback_data["type"]
        assert data["rating"] == feedback_data["rating"]
        assert data["status"] == "NEW"
        assert data["user_id"] == test_user.id
        assert "id" in data
        assert "created_at" in data
    
    @pytest.mark.asyncio
    async def test_create_feedback_without_rating(self, client, test_user):
        """Тест создания отзыва без оценки"""
        feedback_data = {
            "title": "Отзыв без оценки",
            "description": "Описание отзыва без оценки длиной более 10 символов",
            "type": "BUG"
        }
        
        response = client.post("/api/feedback/", json=feedback_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["rating"] is None
    
    @pytest.mark.asyncio
    async def test_create_feedback_duplicate(self, client, test_user, test_feedback):
        """Тест создания второго отзыва одним пользователем (должно быть запрещено)"""
        feedback_data = {
            "title": "Второй отзыв",
            "description": "Попытка создать второй отзыв длиной более 10 символов",
            "type": "FEATURE",
            "rating": 4
        }
        
        response = client.post("/api/feedback/", json=feedback_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "уже оставили отзыв" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_create_feedback_invalid_title_short(self, client):
        """Тест создания отзыва с коротким заголовком"""
        feedback_data = {
            "title": "ab",
            "description": "Описание отзыва длиной более 10 символов",
            "type": "GENERAL"
        }
        
        response = client.post("/api/feedback/", json=feedback_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_create_feedback_invalid_description_short(self, client):
        """Тест создания отзыва с коротким описанием"""
        feedback_data = {
            "title": "Валидный заголовок",
            "description": "коротко",
            "type": "GENERAL"
        }
        
        response = client.post("/api/feedback/", json=feedback_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_create_feedback_invalid_rating_low(self, client):
        """Тест создания отзыва с оценкой меньше 1"""
        feedback_data = {
            "title": "Валидный заголовок",
            "description": "Описание отзыва длиной более 10 символов",
            "type": "GENERAL",
            "rating": 0
        }
        
        response = client.post("/api/feedback/", json=feedback_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_create_feedback_invalid_rating_high(self, client):
        """Тест создания отзыва с оценкой больше 5"""
        feedback_data = {
            "title": "Валидный заголовок",
            "description": "Описание отзыва длиной более 10 символов",
            "type": "GENERAL",
            "rating": 6
        }
        
        response = client.post("/api/feedback/", json=feedback_data)
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    @pytest.mark.asyncio
    async def test_create_feedback_unauthenticated(self, unauthenticated_client):
        """Тест создания отзыва неавторизованным пользователем"""
        feedback_data = {
            "title": "Новый отзыв",
            "description": "Описание отзыва длиной более 10 символов",
            "type": "GENERAL"
        }
        
        response = unauthenticated_client.post("/api/feedback/", json=feedback_data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestGetPublicFeedbacks:
    """Тесты для получения публичных отзывов"""
    
    @pytest.mark.asyncio
    async def test_get_public_feedbacks_empty(self, unauthenticated_client):
        """Тест получения пустого списка публичных отзывов"""
        response = unauthenticated_client.get("/api/feedback/public")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data["feedbacks"], list)
        assert len(data["feedbacks"]) == 0
        assert data["total"] == 0
    
    @pytest.mark.asyncio
    async def test_get_public_feedbacks_with_data(self, unauthenticated_client, test_feedbacks):
        """Тест получения публичных отзывов с данными"""
        response = unauthenticated_client.get("/api/feedback/public")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data["feedbacks"], list)
        assert len(data["feedbacks"]) >= len(test_feedbacks)
        assert data["total"] >= len(test_feedbacks)
        assert "page" in data
        assert "per_page" in data
        assert "total_pages" in data
    
    @pytest.mark.asyncio
    async def test_get_public_feedbacks_with_pagination(self, unauthenticated_client, test_feedbacks):
        """Тест получения публичных отзывов с пагинацией"""
        response = unauthenticated_client.get("/api/feedback/public?skip=0&limit=2")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data["feedbacks"], list)
        assert len(data["feedbacks"]) <= 2


class TestGetFeedbacks:
    """Тесты для получения всех отзывов"""
    
    @pytest.mark.asyncio
    async def test_get_feedbacks_empty(self, client):
        """Тест получения пустого списка отзывов"""
        response = client.get("/api/feedback/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data["feedbacks"], list)
        assert len(data["feedbacks"]) == 0
    
    @pytest.mark.asyncio
    async def test_get_feedbacks_with_data(self, client, test_feedbacks):
        """Тест получения списка отзывов с данными"""
        response = client.get("/api/feedback/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data["feedbacks"], list)
        assert len(data["feedbacks"]) >= len(test_feedbacks)
    
    @pytest.mark.asyncio
    async def test_get_feedbacks_with_filters_admin(self, admin_client, test_feedbacks):
        """Тест получения отзывов с фильтрами администратором"""
        response = admin_client.get("/api/feedback/?status_filter=NEW")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data["feedbacks"], list)
        # Проверяем, что все отзывы имеют статус NEW
        for feedback in data["feedbacks"]:
            assert feedback["status"] == "NEW"
    
    @pytest.mark.asyncio
    async def test_get_feedbacks_with_type_filter_admin(self, admin_client, test_feedbacks):
        """Тест получения отзывов с фильтром по типу администратором"""
        response = admin_client.get("/api/feedback/?type_filter=BUG")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data["feedbacks"], list)
        # Проверяем, что все отзывы имеют тип BUG
        for feedback in data["feedbacks"]:
            assert feedback["type"] == "BUG"
    
    @pytest.mark.asyncio
    async def test_get_feedbacks_filters_ignored_for_user(self, client, test_feedbacks):
        """Тест, что фильтры игнорируются для обычных пользователей"""
        response = client.get("/api/feedback/?status_filter=NEW&type_filter=BUG")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # Фильтры должны быть проигнорированы, возвращаются все отзывы
        assert isinstance(data["feedbacks"], list)
    
    @pytest.mark.asyncio
    async def test_get_feedbacks_unauthenticated(self, unauthenticated_client):
        """Тест получения отзывов неавторизованным пользователем"""
        response = unauthenticated_client.get("/api/feedback/")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestGetMyFeedbacks:
    """Тесты для получения моих отзывов"""
    
    @pytest.mark.asyncio
    async def test_get_my_feedbacks_empty(self, client, test_user):
        """Тест получения пустого списка моих отзывов"""
        response = client.get("/api/feedback/my")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data["feedbacks"], list)
        assert data["total"] == 0
    
    @pytest.mark.asyncio
    async def test_get_my_feedbacks_with_data(self, client, test_feedback):
        """Тест получения моих отзывов с данными"""
        response = client.get("/api/feedback/my")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data["feedbacks"], list)
        assert len(data["feedbacks"]) >= 1
        assert data["total"] >= 1
        # Проверяем, что все отзывы принадлежат текущему пользователю
        for feedback in data["feedbacks"]:
            assert feedback["user_id"] == test_feedback.user_id
    
    @pytest.mark.asyncio
    async def test_get_my_feedbacks_unauthenticated(self, unauthenticated_client):
        """Тест получения моих отзывов неавторизованным пользователем"""
        response = unauthenticated_client.get("/api/feedback/my")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestGetAssignedFeedbacks:
    """Тесты для получения назначенных отзывов"""
    
    @pytest.mark.asyncio
    async def test_get_assigned_feedbacks_empty(self, admin_client, test_admin):
        """Тест получения пустого списка назначенных отзывов"""
        response = admin_client.get("/api/feedback/assigned")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data["feedbacks"], list)
        assert data["total"] == 0
    
    @pytest.mark.asyncio
    async def test_get_assigned_feedbacks_with_data(self, admin_client, test_feedbacks, test_admin):
        """Тест получения назначенных отзывов с данными"""
        response = admin_client.get("/api/feedback/assigned")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data["feedbacks"], list)
        # Проверяем, что все отзывы назначены текущему администратору
        for feedback in data["feedbacks"]:
            assert feedback["assigned_to_id"] == test_admin.id
    
    @pytest.mark.asyncio
    async def test_get_assigned_feedbacks_forbidden_for_user(self, client):
        """Тест получения назначенных отзывов обычным пользователем"""
        response = client.get("/api/feedback/assigned")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_get_assigned_feedbacks_unauthenticated(self, unauthenticated_client):
        """Тест получения назначенных отзывов неавторизованным пользователем"""
        response = unauthenticated_client.get("/api/feedback/assigned")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestGetFeedbackStats:
    """Тесты для получения статистики по отзывам"""
    
    @pytest.mark.asyncio
    async def test_get_feedback_stats_empty(self, admin_client):
        """Тест получения статистики при отсутствии отзывов"""
        response = admin_client.get("/api/feedback/stats")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 0
        assert data["new"] == 0
        assert data["in_review"] == 0
        assert data["in_progress"] == 0
        assert data["resolved"] == 0
        assert data["rejected"] == 0
        assert "by_type" in data
    
    @pytest.mark.asyncio
    async def test_get_feedback_stats_with_data(self, admin_client, test_feedbacks):
        """Тест получения статистики с данными"""
        response = admin_client.get("/api/feedback/stats")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] >= len(test_feedbacks)
        assert "by_type" in data
        assert isinstance(data["by_type"], dict)
        # Проверяем, что все типы присутствуют
        for feedback_type in FeedbackType:
            assert feedback_type.value in data["by_type"]
    
    @pytest.mark.asyncio
    async def test_get_feedback_stats_forbidden_for_user(self, client):
        """Тест получения статистики обычным пользователем"""
        response = client.get("/api/feedback/stats")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_get_feedback_stats_unauthenticated(self, unauthenticated_client):
        """Тест получения статистики неавторизованным пользователем"""
        response = unauthenticated_client.get("/api/feedback/stats")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestGetFeedbackById:
    """Тесты для получения отзыва по ID"""
    
    @pytest.mark.asyncio
    async def test_get_feedback_by_id_success(self, client, test_feedback):
        """Тест успешного получения отзыва по ID"""
        response = client.get(f"/api/feedback/{test_feedback.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_feedback.id
        assert data["title"] == test_feedback.title
        assert data["description"] == test_feedback.description
        assert data["type"] == test_feedback.type.value
        assert "user" in data
    
    @pytest.mark.asyncio
    async def test_get_feedback_by_id_not_found(self, client):
        """Тест получения несуществующего отзыва"""
        response = client.get("/api/feedback/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "не найден" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_get_feedback_by_id_unauthenticated(self, unauthenticated_client, test_feedback):
        """Тест получения отзыва неавторизованным пользователем"""
        # Эндпоинт доступен без авторизации (нет зависимости get_current_user)
        response = unauthenticated_client.get(f"/api/feedback/{test_feedback.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_feedback.id


class TestUpdateFeedback:
    """Тесты для обновления отзыва"""
    
    @pytest.mark.asyncio
    async def test_update_feedback_success(self, client, test_feedback):
        """Тест успешного обновления отзыва"""
        update_data = {
            "title": "Обновленный заголовок",
            "description": "Обновленное описание отзыва длиной более 10 символов",
            "rating": 4
        }
        
        response = client.put(f"/api/feedback/{test_feedback.id}", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["description"] == update_data["description"]
        assert data["rating"] == update_data["rating"]
    
    @pytest.mark.asyncio
    async def test_update_feedback_partial(self, client, test_feedback):
        """Тест частичного обновления отзыва"""
        update_data = {
            "title": "Частично обновленный заголовок"
        }
        
        response = client.put(f"/api/feedback/{test_feedback.id}", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == update_data["title"]
        # Другие поля должны остаться без изменений
        assert data["description"] == test_feedback.description
    
    @pytest.mark.asyncio
    async def test_update_feedback_other_user_forbidden(self, client_user2, test_feedback):
        """Тест обновления чужого отзыва"""
        # test_feedback принадлежит test_user, пытаемся обновить его через client_user2
        update_data = {
            "title": "Попытка обновить чужой отзыв"
        }
        
        response = client_user2.put(f"/api/feedback/{test_feedback.id}", json=update_data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "свои отзывы" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_update_feedback_resolved_forbidden(self, client, db_session, test_user):
        """Тест обновления завершенного отзыва"""
        from app.repositories.feedback_repository import FeedbackRepository
        from app.models.feedback import FeedbackStatus, FeedbackType
        from app.schemas.feedback import FeedbackCreate
        
        # Создаем отзыв со статусом RESOLVED
        feedback_repo = FeedbackRepository(db_session)
        feedback = await feedback_repo.create_feedback(
            FeedbackCreate(
                title="Завершенный отзыв",
                description="Описание завершенного отзыва длиной более 10 символов",
                type=FeedbackType.GENERAL,
                rating=5
            ),
            test_user.id
        )
        
        # Обновляем статус на RESOLVED
        feedback.status = FeedbackStatus.RESOLVED
        await db_session.commit()
        await db_session.refresh(feedback)
        
        update_data = {"title": "Попытка обновить"}
        response = client.put(f"/api/feedback/{feedback.id}", json=update_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "завершенные" in response.json()["detail"].lower() or "отклоненные" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_update_feedback_not_found(self, client):
        """Тест обновления несуществующего отзыва"""
        update_data = {"title": "Новый заголовок"}
        
        response = client.put("/api/feedback/99999", json=update_data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_update_feedback_unauthenticated(self, unauthenticated_client, test_feedback):
        """Тест обновления отзыва неавторизованным пользователем"""
        update_data = {"title": "Новый заголовок"}
        
        response = unauthenticated_client.put(f"/api/feedback/{test_feedback.id}", json=update_data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestAdminUpdateFeedback:
    """Тесты для административного обновления отзыва"""
    
    @pytest.mark.asyncio
    async def test_admin_update_feedback_status(self, admin_client, test_feedback):
        """Тест обновления статуса отзыва администратором"""
        update_data = {
            "status": "IN_REVIEW"
        }
        
        response = admin_client.patch(f"/api/feedback/{test_feedback.id}/admin", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "IN_REVIEW"
    
    @pytest.mark.asyncio
    async def test_admin_update_feedback_assign(self, admin_client, test_feedback, test_admin):
        """Тест назначения отзыва администратору"""
        update_data = {
            "assigned_to_id": test_admin.id
        }
        
        response = admin_client.patch(f"/api/feedback/{test_feedback.id}/admin", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["assigned_to_id"] == test_admin.id
    
    @pytest.mark.asyncio
    async def test_admin_update_feedback_response(self, admin_client, test_feedback):
        """Тест добавления ответа администратора"""
        update_data = {
            "admin_response": "Спасибо за отзыв! Мы учтем ваши замечания."
        }
        
        response = admin_client.patch(f"/api/feedback/{test_feedback.id}/admin", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["admin_response"] == update_data["admin_response"]
    
    @pytest.mark.asyncio
    async def test_admin_update_feedback_assign_to_non_admin(self, admin_client, test_feedback, test_user):
        """Тест попытки назначить отзыв обычному пользователю"""
        update_data = {
            "assigned_to_id": test_user.id
        }
        
        response = admin_client.patch(f"/api/feedback/{test_feedback.id}/admin", json=update_data)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "администратора" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_admin_update_feedback_not_found(self, admin_client):
        """Тест обновления несуществующего отзыва"""
        update_data = {"status": "IN_REVIEW"}
        
        response = admin_client.patch("/api/feedback/99999/admin", json=update_data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_admin_update_feedback_forbidden_for_user(self, client, test_feedback):
        """Тест административного обновления обычным пользователем"""
        update_data = {"status": "IN_REVIEW"}
        
        response = client.patch(f"/api/feedback/{test_feedback.id}/admin", json=update_data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_admin_update_feedback_unauthenticated(self, unauthenticated_client, test_feedback):
        """Тест административного обновления неавторизованным пользователем"""
        update_data = {"status": "IN_REVIEW"}
        
        response = unauthenticated_client.patch(f"/api/feedback/{test_feedback.id}/admin", json=update_data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestDeleteFeedback:
    """Тесты для удаления отзыва"""
    
    @pytest.mark.asyncio
    async def test_delete_feedback_by_owner(self, client, test_feedback):
        """Тест удаления отзыва владельцем"""
        response = client.delete(f"/api/feedback/{test_feedback.id}")
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
        
        # Проверяем, что отзыв действительно удален
        get_response = client.get(f"/api/feedback/{test_feedback.id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_delete_feedback_by_admin(self, admin_client, test_feedback):
        """Тест удаления отзыва администратором"""
        response = admin_client.delete(f"/api/feedback/{test_feedback.id}")
        
        assert response.status_code == status.HTTP_204_NO_CONTENT
    
    @pytest.mark.asyncio
    async def test_delete_feedback_by_other_user_forbidden(self, client_user2, test_feedback):
        """Тест удаления чужого отзыва обычным пользователем"""
        response = client_user2.delete(f"/api/feedback/{test_feedback.id}")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_delete_feedback_not_found(self, client):
        """Тест удаления несуществующего отзыва"""
        response = client.delete("/api/feedback/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_delete_feedback_unauthenticated(self, unauthenticated_client, test_feedback):
        """Тест удаления отзыва неавторизованным пользователем"""
        response = unauthenticated_client.delete(f"/api/feedback/{test_feedback.id}")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN

