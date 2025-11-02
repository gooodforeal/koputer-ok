"""
Тесты для эндпоинтов builds
"""
import pytest
from fastapi import status
from typing import List


class TestCreateBuild:
    """Тесты для создания сборки"""
    
    @pytest.mark.asyncio
    async def test_create_build_success(
        self, client, test_user, test_components
    ):
        """Тест успешного создания сборки"""
        component_ids = [c.id for c in test_components]
        
        build_data = {
            "title": "Тестовая сборка",
            "description": "Описание тестовой сборки для проверки функционала",
            "component_ids": component_ids,
            "additional_info": "Дополнительная информация"
        }
        
        response = client.post("/api/builds/", json=build_data)
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == build_data["title"]
        assert data["description"] == build_data["description"]
        assert data["author_id"] == test_user.id
        assert len(data["components"]) == len(component_ids)
        assert data["views_count"] == 0
        assert data["average_rating"] == 0.0
        assert data["ratings_count"] == 0
    
    @pytest.mark.asyncio
    async def test_create_build_without_auth(self, unauthenticated_client):
        """Тест создания сборки без авторизации"""
        build_data = {
            "title": "Тестовая сборка",
            "description": "Описание тестовой сборки",
            "component_ids": [1, 2, 3]
        }
        
        response = unauthenticated_client.post("/api/builds/", json=build_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
    
    @pytest.mark.asyncio
    async def test_create_build_invalid_data(self, client):
        """Тест создания сборки с невалидными данными"""
        build_data = {
            "title": "А",  # Слишком короткое название
            "description": "Описание",
            "component_ids": []
        }
        
        response = client.post("/api/builds/", json=build_data)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestGetBuilds:
    """Тесты для получения списка сборок"""
    
    @pytest.mark.asyncio
    async def test_get_builds_empty_list(self, client):
        """Тест получения пустого списка сборок"""
        response = client.get("/api/builds/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 0
        assert len(data["builds"]) == 0
        assert data["page"] == 1
    
    @pytest.mark.asyncio
    async def test_get_builds_with_pagination(
        self, client, test_user, test_components, db_session
    ):
        """Тест получения списка сборок с пагинацией"""
        # Создаем несколько сборок
        from app.repositories.build_repository import BuildRepository
        from app.schemas.build import BuildCreate
        
        build_repo = BuildRepository(db_session)
        component_ids = [c.id for c in test_components]
        
        for i in range(5):
            build_data = BuildCreate(
                title=f"Сборка {i+1}",
                description=f"Описание сборки {i+1}",
                component_ids=component_ids
            )
            await build_repo.create(build_data, test_user.id)
        
        response = client.get("/api/builds/?skip=0&limit=3")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 5
        assert len(data["builds"]) == 3
        assert data["page"] == 1
        assert data["per_page"] == 3
    
    @pytest.mark.asyncio
    async def test_get_builds_with_query(
        self, client, test_user, test_components, db_session
    ):
        """Тест поиска сборок по запросу"""
        from app.repositories.build_repository import BuildRepository
        from app.schemas.build import BuildCreate
        
        build_repo = BuildRepository(db_session)
        component_ids = [c.id for c in test_components]
        
        build_data1 = BuildCreate(
            title="Игровая сборка",
            description="Мощная игровая сборка",
            component_ids=component_ids
        )
        build_data2 = BuildCreate(
            title="Офисная сборка",
            description="Сборка для офиса",
            component_ids=component_ids
        )
        
        await build_repo.create(build_data1, test_user.id)
        await build_repo.create(build_data2, test_user.id)
        
        response = client.get("/api/builds/?query=игровая")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] >= 1
        assert any("игровая" in build["title"].lower() or "игровая" in build["description"].lower() 
                  for build in data["builds"])
    
    @pytest.mark.asyncio
    async def test_get_builds_with_author_filter(
        self, client, test_user, test_user2, test_components, db_session
    ):
        """Тест фильтрации сборок по автору"""
        from app.repositories.build_repository import BuildRepository
        from app.schemas.build import BuildCreate
        
        build_repo = BuildRepository(db_session)
        component_ids = [c.id for c in test_components]
        
        build_data = BuildCreate(
            title="Сборка пользователя 1",
            description="Подробное описание сборки для тестирования",
            component_ids=component_ids
        )
        await build_repo.create(build_data, test_user.id)
        
        build_data2 = BuildCreate(
            title="Сборка пользователя 2",
            description="Подробное описание сборки пользователя 2",
            component_ids=component_ids
        )
        await build_repo.create(build_data2, test_user2.id)
        
        response = client.get(f"/api/builds/?author_id={test_user.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] >= 1
        assert all(build["author_id"] == test_user.id for build in data["builds"])


class TestGetTopBuilds:
    """Тесты для получения топа сборок"""
    
    @pytest.mark.asyncio
    async def test_get_top_builds_empty(self, client):
        """Тест получения топа пустых сборок"""
        response = client.get("/api/builds/top")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 0
        assert len(data["builds"]) == 0


class TestGetMyBuilds:
    """Тесты для получения моих сборок"""
    
    @pytest.mark.asyncio
    async def test_get_my_builds_empty(self, client):
        """Тест получения пустого списка моих сборок"""
        response = client.get("/api/builds/my")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 0
        assert len(data["builds"]) == 0
    
    @pytest.mark.asyncio
    async def test_get_my_builds_with_data(
        self, client, test_user, test_components, db_session
    ):
        """Тест получения списка моих сборок"""
        from app.repositories.build_repository import BuildRepository
        from app.schemas.build import BuildCreate
        
        build_repo = BuildRepository(db_session)
        component_ids = [c.id for c in test_components]
        
        build_data = BuildCreate(
            title="Моя сборка",
            description="Описание моей сборки",
            component_ids=component_ids
        )
        await build_repo.create(build_data, test_user.id)
        
        response = client.get("/api/builds/my")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 1
        assert len(data["builds"]) == 1
        assert data["builds"][0]["author_id"] == test_user.id


class TestGetBuildStats:
    """Тесты для получения статистики"""
    
    @pytest.mark.asyncio
    async def test_get_builds_stats_empty(self, client):
        """Тест получения статистики при отсутствии сборок"""
        response = client.get("/api/builds/stats")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total_builds"] == 0
        assert data["total_ratings"] == 0
        assert data["total_comments"] == 0
        assert data["average_rating"] == 0.0


class TestGetUniqueComponents:
    """Тесты для получения уникальных компонентов"""
    
    @pytest.mark.asyncio
    async def test_get_unique_components(self, client, test_components):
        """Тест получения уникальных компонентов"""
        response = client.get("/api/builds/components/unique")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "components_by_category" in data
        assert isinstance(data["components_by_category"], dict)


class TestGetBuildById:
    """Тесты для получения сборки по ID"""
    
    @pytest.mark.asyncio
    async def test_get_build_by_id_success(
        self, client, test_user, test_components, db_session
    ):
        """Тест успешного получения сборки по ID"""
        from app.repositories.build_repository import BuildRepository
        from app.schemas.build import BuildCreate
        
        build_repo = BuildRepository(db_session)
        component_ids = [c.id for c in test_components]
        
        build_data = BuildCreate(
            title="Тестовая сборка",
            description="Описание сборки",
            component_ids=component_ids
        )
        created_build = await build_repo.create(build_data, test_user.id)
        
        response = client.get(f"/api/builds/{created_build.id}")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == created_build.id
        assert data["title"] == build_data.title
        assert data["views_count"] >= 0
    
    @pytest.mark.asyncio
    async def test_get_build_by_id_not_found(self, client):
        """Тест получения несуществующей сборки"""
        response = client.get("/api/builds/99999")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "не найдена" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_get_build_by_id_unauthenticated(
        self, unauthenticated_client, test_user, test_components, db_session
    ):
        """Тест получения сборки неавторизованным пользователем"""
        from app.repositories.build_repository import BuildRepository
        from app.schemas.build import BuildCreate
        
        build_repo = BuildRepository(db_session)
        component_ids = [c.id for c in test_components]
        
        build_data = BuildCreate(
            title="Тестовая сборка",
            description="Описание сборки",
            component_ids=component_ids
        )
        created_build = await build_repo.create(build_data, test_user.id)
        
        response = unauthenticated_client.get(f"/api/builds/{created_build.id}")
        
        # Неавторизованный пользователь может просматривать сборки
        assert response.status_code == status.HTTP_200_OK


class TestUpdateBuild:
    """Тесты для обновления сборки"""
    
    @pytest.mark.asyncio
    async def test_update_build_success(
        self, client, test_user, test_components, db_session
    ):
        """Тест успешного обновления сборки"""
        from app.repositories.build_repository import BuildRepository
        from app.schemas.build import BuildCreate
        
        build_repo = BuildRepository(db_session)
        component_ids = [c.id for c in test_components]
        
        build_data = BuildCreate(
            title="Старое название",
            description="Старое описание",
            component_ids=component_ids
        )
        created_build = await build_repo.create(build_data, test_user.id)
        
        update_data = {
            "title": "Новое название",
            "description": "Новое описание"
        }
        
        response = client.put(f"/api/builds/{created_build.id}", json=update_data)
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == update_data["title"]
        assert data["description"] == update_data["description"]
    
    @pytest.mark.asyncio
    async def test_update_build_not_found(self, client):
        """Тест обновления несуществующей сборки"""
        update_data = {
            "title": "Новое название",
            "description": "Новое описание"
        }
        
        response = client.put("/api/builds/99999", json=update_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_update_build_forbidden(
        self, client_user2, test_user, test_components, db_session
    ):
        """Тест обновления сборки другим пользователем"""
        from app.repositories.build_repository import BuildRepository
        from app.schemas.build import BuildCreate
        
        build_repo = BuildRepository(db_session)
        component_ids = [c.id for c in test_components]
        
        build_data = BuildCreate(
            title="Сборка пользователя 1",
            description="Подробное описание сборки для тестирования",
            component_ids=component_ids
        )
        created_build = await build_repo.create(build_data, test_user.id)
        
        update_data = {
            "title": "Попытка изменить",
            "description": "Подробное описание для проверки прав доступа"
        }
        
        response = client_user2.put(f"/api/builds/{created_build.id}", json=update_data)
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestDeleteBuild:
    """Тесты для удаления сборки"""
    
    @pytest.mark.asyncio
    async def test_delete_build_success(
        self, client, test_user, test_components, db_session
    ):
        """Тест успешного удаления сборки"""
        from app.repositories.build_repository import BuildRepository
        from app.schemas.build import BuildCreate
        
        build_repo = BuildRepository(db_session)
        component_ids = [c.id for c in test_components]
        
        build_data = BuildCreate(
            title="Сборка для удаления",
            description="Подробное описание сборки для тестирования",
            component_ids=component_ids
        )
        created_build = await build_repo.create(build_data, test_user.id)
        
        response = client.delete(f"/api/builds/{created_build.id}")
        
        assert response.status_code == status.HTTP_200_OK
        assert "успешно удалена" in response.json()["message"].lower()
        
        # Проверяем, что сборка удалена
        get_response = client.get(f"/api/builds/{created_build.id}")
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_delete_build_not_found(self, client):
        """Тест удаления несуществующей сборки"""
        response = client.delete("/api/builds/99999")
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    @pytest.mark.asyncio
    async def test_delete_build_forbidden(
        self, client_user2, test_user, test_components, db_session
    ):
        """Тест удаления сборки другим пользователем"""
        from app.repositories.build_repository import BuildRepository
        from app.schemas.build import BuildCreate
        
        build_repo = BuildRepository(db_session)
        component_ids = [c.id for c in test_components]
        
        build_data = BuildCreate(
            title="Сборка пользователя 1",
            description="Подробное описание сборки для тестирования",
            component_ids=component_ids
        )
        created_build = await build_repo.create(build_data, test_user.id)
        
        response = client_user2.delete(f"/api/builds/{created_build.id}")
        
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestCreateRating:
    """Тесты для создания оценки"""
    
    @pytest.mark.asyncio
    async def test_create_rating_success(
        self, client_user2, test_user, test_components, db_session
    ):
        """Тест успешного создания оценки"""
        from app.repositories.build_repository import BuildRepository
        from app.schemas.build import BuildCreate
        
        build_repo = BuildRepository(db_session)
        component_ids = [c.id for c in test_components]
        
        build_data = BuildCreate(
            title="Сборка для оценки",
            description="Подробное описание сборки для тестирования",
            component_ids=component_ids
        )
        created_build = await build_repo.create(build_data, test_user.id)
        
        rating_data = {"score": 5}
        
        response = client_user2.post(
            f"/api/builds/{created_build.id}/ratings",
            json=rating_data
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["score"] == rating_data["score"]
        assert data["build_id"] == created_build.id
    
    @pytest.mark.asyncio
    async def test_create_rating_own_build(
        self, client, test_user, test_components, db_session
    ):
        """Тест создания оценки для своей сборки"""
        from app.repositories.build_repository import BuildRepository
        from app.schemas.build import BuildCreate
        
        build_repo = BuildRepository(db_session)
        component_ids = [c.id for c in test_components]
        
        build_data = BuildCreate(
            title="Моя сборка",
            description="Подробное описание сборки для тестирования",
            component_ids=component_ids
        )
        created_build = await build_repo.create(build_data, test_user.id)
        
        rating_data = {"score": 5}
        
        response = client.post(
            f"/api/builds/{created_build.id}/ratings",
            json=rating_data
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "свою собственную" in response.json()["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_create_rating_duplicate(
        self, client_user2, test_user, test_components, db_session
    ):
        """Тест создания дублирующей оценки"""
        from app.repositories.build_repository import BuildRepository
        from app.schemas.build import BuildCreate
        
        build_repo = BuildRepository(db_session)
        component_ids = [c.id for c in test_components]
        
        build_data = BuildCreate(
            title="Сборка для оценки",
            description="Подробное описание сборки для тестирования",
            component_ids=component_ids
        )
        created_build = await build_repo.create(build_data, test_user.id)
        
        rating_data = {"score": 5}
        
        # Создаем первую оценку
        response1 = client_user2.post(
            f"/api/builds/{created_build.id}/ratings",
            json=rating_data
        )
        assert response1.status_code == status.HTTP_201_CREATED
        
        # Пытаемся создать вторую оценку
        response2 = client_user2.post(
            f"/api/builds/{created_build.id}/ratings",
            json=rating_data
        )
        
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert "уже оценили" in response2.json()["detail"].lower()


class TestUpdateRating:
    """Тесты для обновления оценки"""
    
    @pytest.mark.asyncio
    async def test_update_rating_success(
        self, client_user2, test_user, test_components, db_session
    ):
        """Тест успешного обновления оценки"""
        from app.repositories.build_repository import BuildRepository
        from app.schemas.build import BuildCreate
        
        build_repo = BuildRepository(db_session)
        component_ids = [c.id for c in test_components]
        
        build_data = BuildCreate(
            title="Сборка для оценки",
            description="Подробное описание сборки для тестирования",
            component_ids=component_ids
        )
        created_build = await build_repo.create(build_data, test_user.id)
        
        # Создаем оценку
        rating_data_create = {"score": 3}
        create_response = client_user2.post(
            f"/api/builds/{created_build.id}/ratings",
            json=rating_data_create
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        
        # Обновляем оценку
        rating_data_update = {"score": 5}
        update_response = client_user2.put(
            f"/api/builds/{created_build.id}/ratings",
            json=rating_data_update
        )
        
        assert update_response.status_code == status.HTTP_200_OK
        data = update_response.json()
        assert data["score"] == rating_data_update["score"]
    
    @pytest.mark.asyncio
    async def test_update_rating_not_found(
        self, client_user2, test_user, test_components, db_session
    ):
        """Тест обновления несуществующей оценки"""
        from app.repositories.build_repository import BuildRepository
        from app.schemas.build import BuildCreate
        
        build_repo = BuildRepository(db_session)
        component_ids = [c.id for c in test_components]
        
        build_data = BuildCreate(
            title="Сборка",
            description="Подробное описание сборки для тестирования",
            component_ids=component_ids
        )
        created_build = await build_repo.create(build_data, test_user.id)
        
        rating_data = {"score": 5}
        
        response = client_user2.put(
            f"/api/builds/{created_build.id}/ratings",
            json=rating_data
        )
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteRating:
    """Тесты для удаления оценки"""
    
    @pytest.mark.asyncio
    async def test_delete_rating_success(
        self, client_user2, test_user, test_components, db_session
    ):
        """Тест успешного удаления оценки"""
        from app.repositories.build_repository import BuildRepository
        from app.schemas.build import BuildCreate
        
        build_repo = BuildRepository(db_session)
        component_ids = [c.id for c in test_components]
        
        build_data = BuildCreate(
            title="Сборка для оценки",
            description="Подробное описание сборки для тестирования",
            component_ids=component_ids
        )
        created_build = await build_repo.create(build_data, test_user.id)
        
        # Создаем оценку
        rating_data = {"score": 5}
        create_response = client_user2.post(
            f"/api/builds/{created_build.id}/ratings",
            json=rating_data
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        
        # Удаляем оценку
        delete_response = client_user2.delete(
            f"/api/builds/{created_build.id}/ratings"
        )
        
        assert delete_response.status_code == status.HTTP_200_OK
        assert "успешно удалена" in delete_response.json()["message"].lower()
    
    @pytest.mark.asyncio
    async def test_delete_rating_not_found(
        self, client_user2, test_user, test_components, db_session
    ):
        """Тест удаления несуществующей оценки"""
        from app.repositories.build_repository import BuildRepository
        from app.schemas.build import BuildCreate
        
        build_repo = BuildRepository(db_session)
        component_ids = [c.id for c in test_components]
        
        build_data = BuildCreate(
            title="Сборка",
            description="Подробное описание сборки для тестирования",
            component_ids=component_ids
        )
        created_build = await build_repo.create(build_data, test_user.id)
        
        response = client_user2.delete(f"/api/builds/{created_build.id}/ratings")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestGetMyRating:
    """Тесты для получения моей оценки"""
    
    @pytest.mark.asyncio
    async def test_get_my_rating_success(
        self, client_user2, test_user, test_components, db_session
    ):
        """Тест успешного получения моей оценки"""
        from app.repositories.build_repository import BuildRepository
        from app.schemas.build import BuildCreate
        
        build_repo = BuildRepository(db_session)
        component_ids = [c.id for c in test_components]
        
        build_data = BuildCreate(
            title="Сборка для оценки",
            description="Подробное описание сборки для тестирования",
            component_ids=component_ids
        )
        created_build = await build_repo.create(build_data, test_user.id)
        
        # Создаем оценку
        rating_data = {"score": 4}
        create_response = client_user2.post(
            f"/api/builds/{created_build.id}/ratings",
            json=rating_data
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        
        # Получаем мою оценку
        response = client_user2.get(f"/api/builds/{created_build.id}/ratings/my")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["score"] == rating_data["score"]
        assert data["build_id"] == created_build.id
    
    @pytest.mark.asyncio
    async def test_get_my_rating_not_found(
        self, client_user2, test_user, test_components, db_session
    ):
        """Тест получения несуществующей оценки"""
        from app.repositories.build_repository import BuildRepository
        from app.schemas.build import BuildCreate
        
        build_repo = BuildRepository(db_session)
        component_ids = [c.id for c in test_components]
        
        build_data = BuildCreate(
            title="Сборка",
            description="Подробное описание сборки для тестирования",
            component_ids=component_ids
        )
        created_build = await build_repo.create(build_data, test_user.id)
        
        response = client_user2.get(f"/api/builds/{created_build.id}/ratings/my")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestCreateComment:
    """Тесты для создания комментария"""
    
    @pytest.mark.asyncio
    async def test_create_comment_success(
        self, client_user2, test_user, test_components, db_session
    ):
        """Тест успешного создания комментария"""
        from app.repositories.build_repository import BuildRepository
        from app.schemas.build import BuildCreate
        
        build_repo = BuildRepository(db_session)
        component_ids = [c.id for c in test_components]
        
        build_data = BuildCreate(
            title="Сборка для комментария",
            description="Подробное описание сборки для тестирования",
            component_ids=component_ids
        )
        created_build = await build_repo.create(build_data, test_user.id)
        
        comment_data = {"content": "Отличная сборка!"}
        
        response = client_user2.post(
            f"/api/builds/{created_build.id}/comments",
            json=comment_data
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["content"] == comment_data["content"]
        assert data["build_id"] == created_build.id
    
    @pytest.mark.asyncio
    async def test_create_reply_comment_success(
        self, client, client_user2, test_user, test_components, db_session
    ):
        """Тест успешного создания ответа на комментарий"""
        from app.repositories.build_repository import BuildRepository
        from app.schemas.build import BuildCreate
        
        build_repo = BuildRepository(db_session)
        component_ids = [c.id for c in test_components]
        
        build_data = BuildCreate(
            title="Сборка для комментария",
            description="Подробное описание сборки для тестирования",
            component_ids=component_ids
        )
        created_build = await build_repo.create(build_data, test_user.id)
        
        # Создаем родительский комментарий
        parent_comment_data = {"content": "Первый комментарий"}
        parent_response = client_user2.post(
            f"/api/builds/{created_build.id}/comments",
            json=parent_comment_data
        )
        assert parent_response.status_code == status.HTTP_201_CREATED
        parent_id = parent_response.json()["id"]
        
        # Создаем ответ на комментарий
        reply_data = {
            "content": "Ответ на комментарий",
            "parent_id": parent_id
        }
        
        response = client.post(
            f"/api/builds/{created_build.id}/comments",
            json=reply_data
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["content"] == reply_data["content"]
        assert data["parent_id"] == parent_id
    
    @pytest.mark.asyncio
    async def test_create_comment_not_found(self, client_user2):
        """Тест создания комментария для несуществующей сборки"""
        comment_data = {"content": "Комментарий"}
        
        response = client_user2.post("/api/builds/99999/comments", json=comment_data)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestGetComments:
    """Тесты для получения комментариев"""
    
    @pytest.mark.asyncio
    async def test_get_comments_empty(
        self, client, test_user, test_components, db_session
    ):
        """Тест получения пустого списка комментариев"""
        from app.repositories.build_repository import BuildRepository
        from app.schemas.build import BuildCreate
        
        build_repo = BuildRepository(db_session)
        component_ids = [c.id for c in test_components]
        
        build_data = BuildCreate(
            title="Сборка",
            description="Подробное описание сборки для тестирования",
            component_ids=component_ids
        )
        created_build = await build_repo.create(build_data, test_user.id)
        
        response = client.get(f"/api/builds/{created_build.id}/comments")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 0
        assert len(data["comments"]) == 0
    
    @pytest.mark.asyncio
    async def test_get_comments_with_data(
        self, client_user2, test_user, test_components, db_session
    ):
        """Тест получения списка комментариев"""
        from app.repositories.build_repository import BuildRepository
        from app.schemas.build import BuildCreate
        
        build_repo = BuildRepository(db_session)
        component_ids = [c.id for c in test_components]
        
        build_data = BuildCreate(
            title="Сборка",
            description="Подробное описание сборки для тестирования",
            component_ids=component_ids
        )
        created_build = await build_repo.create(build_data, test_user.id)
        
        # Создаем несколько комментариев
        for i in range(3):
            comment_data = {"content": f"Комментарий {i+1}"}
            client_user2.post(
                f"/api/builds/{created_build.id}/comments",
                json=comment_data
            )
        
        response = client_user2.get(f"/api/builds/{created_build.id}/comments")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["total"] == 3
        assert len(data["comments"]) == 3


class TestUpdateComment:
    """Тесты для обновления комментария"""
    
    @pytest.mark.asyncio
    async def test_update_comment_success(
        self, client_user2, test_user, test_components, db_session
    ):
        """Тест успешного обновления комментария"""
        from app.repositories.build_repository import BuildRepository
        from app.schemas.build import BuildCreate
        
        build_repo = BuildRepository(db_session)
        component_ids = [c.id for c in test_components]
        
        build_data = BuildCreate(
            title="Сборка",
            description="Подробное описание сборки для тестирования",
            component_ids=component_ids
        )
        created_build = await build_repo.create(build_data, test_user.id)
        
        # Создаем комментарий
        comment_data = {"content": "Старый комментарий"}
        create_response = client_user2.post(
            f"/api/builds/{created_build.id}/comments",
            json=comment_data
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        comment_id = create_response.json()["id"]
        
        # Обновляем комментарий
        update_data = {"content": "Обновленный комментарий"}
        response = client_user2.put(
            f"/api/builds/{created_build.id}/comments/{comment_id}",
            json=update_data
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["content"] == update_data["content"]
    
    @pytest.mark.asyncio
    async def test_update_comment_forbidden(
        self, client, client_user2, test_user, test_user2, test_components, db_session
    ):
        """Тест обновления комментария другим пользователем"""
        from app.repositories.build_repository import BuildRepository
        from app.schemas.build import BuildCreate
        
        build_repo = BuildRepository(db_session)
        component_ids = [c.id for c in test_components]
        
        build_data = BuildCreate(
            title="Сборка",
            description="Подробное описание сборки для тестирования",
            component_ids=component_ids
        )
        created_build = await build_repo.create(build_data, test_user.id)
        
        # Убеждаемся, что пользователи разные
        assert test_user.id != test_user2.id, "Users should be different"
        
        # Создаем комментарий от второго пользователя
        comment_data = {"content": "Комментарий пользователя 2"}
        create_response = client_user2.post(
            f"/api/builds/{created_build.id}/comments",
            json=comment_data
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        comment_id = create_response.json()["id"]
        # Проверяем, что комментарий создан вторым пользователем
        assert create_response.json()["user_id"] == test_user2.id
        
        # Пытаемся обновить комментарий от первого пользователя (не автора)
        update_data = {"content": "Попытка изменить"}
        response = client.put(
            f"/api/builds/{created_build.id}/comments/{comment_id}",
            json=update_data
        )
        
        # Проверяем, что это действительно другой пользователь
        assert response.status_code == status.HTTP_403_FORBIDDEN, f"Expected 403, got {response.status_code}. Response: {response.json() if response.status_code != 200 else 'OK'}"


class TestDeleteComment:
    """Тесты для удаления комментария"""
    
    @pytest.mark.asyncio
    async def test_delete_comment_success(
        self, client_user2, test_user, test_components, db_session
    ):
        """Тест успешного удаления комментария"""
        from app.repositories.build_repository import BuildRepository
        from app.schemas.build import BuildCreate
        
        build_repo = BuildRepository(db_session)
        component_ids = [c.id for c in test_components]
        
        build_data = BuildCreate(
            title="Сборка",
            description="Подробное описание сборки для тестирования",
            component_ids=component_ids
        )
        created_build = await build_repo.create(build_data, test_user.id)
        
        # Создаем комментарий
        comment_data = {"content": "Комментарий для удаления"}
        create_response = client_user2.post(
            f"/api/builds/{created_build.id}/comments",
            json=comment_data
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        comment_id = create_response.json()["id"]
        
        # Удаляем комментарий
        response = client_user2.delete(
            f"/api/builds/{created_build.id}/comments/{comment_id}"
        )
        
        assert response.status_code == status.HTTP_200_OK
        assert "успешно удален" in response.json()["message"].lower()
    
    @pytest.mark.asyncio
    async def test_delete_comment_forbidden(
        self, client, client_user2, test_user, test_user2, test_components, db_session
    ):
        """Тест удаления комментария другим пользователем"""
        from app.repositories.build_repository import BuildRepository
        from app.schemas.build import BuildCreate
        
        build_repo = BuildRepository(db_session)
        component_ids = [c.id for c in test_components]
        
        build_data = BuildCreate(
            title="Сборка",
            description="Подробное описание сборки для тестирования",
            component_ids=component_ids
        )
        created_build = await build_repo.create(build_data, test_user.id)
        
        # Убеждаемся, что пользователи разные
        assert test_user.id != test_user2.id, "Users should be different"
        
        # Создаем комментарий от второго пользователя
        comment_data = {"content": "Комментарий"}
        create_response = client_user2.post(
            f"/api/builds/{created_build.id}/comments",
            json=comment_data
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        comment_id = create_response.json()["id"]
        # Проверяем, что комментарий создан вторым пользователем
        assert create_response.json()["user_id"] == test_user2.id

        
        # Пытаемся удалить комментарий от первого пользователя (не автора)
        response = client.delete(
            f"/api/builds/{created_build.id}/comments/{comment_id}"
        )
        
        # Проверяем, что это действительно другой пользователь
        assert response.status_code == status.HTTP_403_FORBIDDEN, f"Expected 403, got {response.status_code}. Response: {response.json() if response.status_code != 200 else 'OK'}"


class TestExportPDF:
    """Тесты для экспорта PDF"""
    
    @pytest.mark.asyncio
    async def test_export_pdf_success(
        self, client, test_user, test_components, db_session
    ):
        """Тест успешного экспорта PDF"""
        from app.repositories.build_repository import BuildRepository
        from app.schemas.build import BuildCreate
        
        build_repo = BuildRepository(db_session)
        component_ids = [c.id for c in test_components]
        
        build_data = BuildCreate(
            title="Сборка для экспорта",
            description="Описание сборки",
            component_ids=component_ids
        )
        created_build = await build_repo.create(build_data, test_user.id)
        
        response = client.get(f"/api/builds/{created_build.id}/export/pdf")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "application/pdf"
        assert "attachment" in response.headers["content-disposition"]
        assert len(response.content) > 0
    
    @pytest.mark.asyncio
    async def test_export_pdf_not_found(self, client):
        """Тест экспорта PDF несуществующей сборки"""
        response = client.get("/api/builds/99999/export/pdf")
        
        assert response.status_code == status.HTTP_404_NOT_FOUND

