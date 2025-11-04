"""
Сервис для работы с чатами
"""
from typing import List, Optional
from fastapi import HTTPException, status
from app.repositories.chat_repository import ChatRepository
from app.models.user import User, UserRole
from app.models.chat import ChatStatus
from app.schemas.chat import (
    ChatCreate, ChatResponse, MessageCreate, MessageCreateWithChatId, MessageResponse,
    ChatListResponse, AssignAdminRequest, UpdateChatStatusRequest
)

class ChatService:
    """Сервис для работы с чатами"""
    
    def __init__(self, chat_repo: ChatRepository):
        self.chat_repo = chat_repo
    
    async def create_chat(
        self,
        chat_data: ChatCreate,
        current_user: User
    ) -> ChatResponse:
        """
        Создать новый чат
        
        Args:
            chat_data: Данные для создания чата
            current_user: Текущий пользователь
            
        Returns:
            ChatResponse с данными чата
        """
        # Проверяем, что пользователь создает чат для себя
        if chat_data.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Вы можете создавать чат только для себя"
            )
        
        # Проверяем, нет ли уже активного чата у пользователя
        existing_chat = await self.chat_repo.get_user_chat(current_user.id)
        if existing_chat:
            return existing_chat
        
        return await self.chat_repo.create_chat(chat_data)
    
    async def get_user_chat(self, current_user: User) -> ChatResponse:
        """
        Получить чат пользователя
        
        Args:
            current_user: Текущий пользователь
            
        Returns:
            ChatResponse с данными чата
        """
        chat = await self.chat_repo.get_user_chat(current_user.id)
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Чат не найден"
            )
        return chat
    
    async def get_admin_chats(self, current_user: User) -> List[ChatListResponse]:
        """
        Получить чаты администратора
        
        Args:
            current_user: Текущий пользователь (должен быть администратором)
            
        Returns:
            Список чатов администратора
        """
        if current_user.role == UserRole.SUPER_ADMIN:
            chats = await self.chat_repo.get_all_active_chats()
        else:
            chats = await self.chat_repo.get_admin_chats(current_user.id)
        
        return chats
    
    async def get_chat(
        self,
        chat_id: int,
        current_user: User
    ) -> ChatResponse:
        """
        Получить чат по ID
        
        Args:
            chat_id: ID чата
            current_user: Текущий пользователь
            
        Returns:
            ChatResponse с данными чата
        """
        chat = await self.chat_repo.get_chat_by_id(chat_id)
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Чат не найден"
            )
        
        # Проверяем права доступа
        if (chat.user_id != current_user.id and 
            chat.admin_id != current_user.id and 
            current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нет доступа к этому чату"
            )
        
        return chat
    
    async def assign_admin_to_chat(
        self,
        chat_id: int,
        request: AssignAdminRequest,
        current_user: User
    ) -> ChatResponse:
        """
        Назначить администратора к чату
        
        Args:
            chat_id: ID чата
            request: Данные запроса с ID администратора
            current_user: Текущий пользователь (должен быть администратором)
            
        Returns:
            ChatResponse с обновленными данными чата
        """
        chat = await self.chat_repo.assign_admin_to_chat(chat_id, request.admin_id)
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Чат не найден"
            )
        return chat
    
    async def send_message(
        self,
        chat_id: int,
        message_data: MessageCreate,
        current_user: User
    ) -> MessageResponse:
        """
        Отправить сообщение в чат
        
        Args:
            chat_id: ID чата
            message_data: Данные сообщения
            current_user: Текущий пользователь
            
        Returns:
            MessageResponse с данными сообщения
        """
        # Проверяем существование чата и права доступа
        chat = await self.chat_repo.get_chat_by_id(chat_id)
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Чат не найден"
            )
        
        if (chat.user_id != current_user.id and 
            chat.admin_id != current_user.id and 
            current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нет доступа к этому чату"
            )
        
        # Создаем данные сообщения с chat_id
        message_data_with_chat = MessageCreateWithChatId(
            content=message_data.content,
            message_type=message_data.message_type,
            chat_id=chat_id
        )
        
        return await self.chat_repo.create_message(message_data_with_chat, current_user.id)
    
    async def get_chat_messages(
        self,
        chat_id: int,
        limit: int,
        offset: int,
        current_user: User
    ) -> List[MessageResponse]:
        """
        Получить сообщения чата
        
        Args:
            chat_id: ID чата
            limit: Максимальное количество сообщений
            offset: Смещение для пагинации
            current_user: Текущий пользователь
            
        Returns:
            Список сообщений
        """
        # Проверяем существование чата и права доступа
        chat = await self.chat_repo.get_chat_by_id(chat_id)
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Чат не найден"
            )
        
        if (chat.user_id != current_user.id and 
            chat.admin_id != current_user.id and 
            current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нет доступа к этому чату"
            )
        
        messages = await self.chat_repo.get_chat_messages(chat_id, limit, offset)
        
        # Отмечаем сообщения как прочитанные
        await self.chat_repo.mark_messages_as_read(chat_id, current_user.id)
        
        return messages
    
    async def mark_chat_as_read(
        self,
        chat_id: int,
        current_user: User
    ) -> dict:
        """
        Отметить чат как прочитанный
        
        Args:
            chat_id: ID чата
            current_user: Текущий пользователь
            
        Returns:
            Словарь с сообщением об успехе
        """
        # Проверяем существование чата и права доступа
        chat = await self.chat_repo.get_chat_by_id(chat_id)
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Чат не найден"
            )
        
        if (chat.user_id != current_user.id and 
            chat.admin_id != current_user.id and 
            current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Нет доступа к этому чату"
            )
        
        await self.chat_repo.mark_messages_as_read(chat_id, current_user.id)
        return {"message": "Чат отмечен как прочитанный"}
    
    async def get_user_chats_summary(self, current_user: User) -> List[dict]:
        """
        Получить краткую информацию о чатах пользователя
        
        Args:
            current_user: Текущий пользователь
            
        Returns:
            Список словарей с краткой информацией о чатах
        """
        return await self.chat_repo.get_user_chats_summary(current_user.id)
    
    async def get_admin_chats_summary(self, current_user: User) -> List[dict]:
        """
        Получить краткую информацию о чатах администратора
        
        Args:
            current_user: Текущий пользователь (должен быть администратором)
            
        Returns:
            Список словарей с краткой информацией о чатах
        """
        if current_user.role == UserRole.SUPER_ADMIN:
            chats = await self.chat_repo.get_all_active_chats()
            summaries = []
            for chat in chats:
                unread_count = await self.chat_repo.get_unread_count(chat.id, current_user.id)
                summaries.append({
                    "id": chat.id,
                    "user_name": chat.user.name,
                    "admin_name": chat.admin.name if chat.admin else None,
                    "is_active": chat.is_active,
                    "status": chat.status,
                    "last_message_at": chat.last_message_at,
                    "unread_count": unread_count
                })
            return summaries
        else:
            return await self.chat_repo.get_admin_chats_summary(current_user.id)
    
    async def update_chat_status(
        self,
        chat_id: int,
        request: UpdateChatStatusRequest,
        current_user: User
    ) -> ChatResponse:
        """
        Обновить статус чата
        
        Args:
            chat_id: ID чата
            request: Данные запроса с новым статусом
            current_user: Текущий пользователь (должен быть администратором)
            
        Returns:
            ChatResponse с обновленными данными чата
        """
        chat = await self.chat_repo.get_chat_by_id(chat_id)
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Чат не найден"
            )
        
        # Проверяем права доступа
        if (current_user.role == UserRole.ADMIN and 
            chat.admin_id != current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Вы можете изменять статус только своих чатов"
            )
        
        updated_chat = await self.chat_repo.update_chat_status(chat_id, request.status, current_user.id)
        return updated_chat
    
    async def close_chat(
        self,
        chat_id: int,
        current_user: User
    ) -> ChatResponse:
        """
        Закрыть чат
        
        Args:
            chat_id: ID чата
            current_user: Текущий пользователь (должен быть администратором)
            
        Returns:
            ChatResponse с обновленными данными чата
        """
        chat = await self.chat_repo.get_chat_by_id(chat_id)
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Чат не найден"
            )
        
        # Проверяем права доступа
        if (current_user.role == UserRole.ADMIN and 
            chat.admin_id != current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Вы можете закрывать только свои чаты"
            )
        
        closed_chat = await self.chat_repo.close_chat(chat_id, current_user.id)
        return closed_chat
    
    async def reopen_chat(
        self,
        chat_id: int,
        current_user: User
    ) -> ChatResponse:
        """
        Переоткрыть чат
        
        Args:
            chat_id: ID чата
            current_user: Текущий пользователь (должен быть администратором)
            
        Returns:
            ChatResponse с обновленными данными чата
        """
        chat = await self.chat_repo.get_chat_by_id(chat_id)
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Чат не найден"
            )
        
        # Проверяем права доступа
        if (current_user.role == UserRole.ADMIN and 
            chat.admin_id != current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Вы можете переоткрывать только свои чаты"
            )
        
        reopened_chat = await self.chat_repo.reopen_chat(chat_id, current_user.id)
        return reopened_chat
    
    async def start_working_on_chat(
        self,
        chat_id: int,
        current_user: User
    ) -> ChatResponse:
        """
        Начать работу с чатом
        
        Args:
            chat_id: ID чата
            current_user: Текущий пользователь (должен быть администратором)
            
        Returns:
            ChatResponse с обновленными данными чата
        """
        chat = await self.chat_repo.get_chat_by_id(chat_id)
        if not chat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Чат не найден"
            )
        
        # Автоматически назначаем администратора, если он не назначен
        if not chat.admin_id:
            chat = await self.chat_repo.assign_admin_to_chat(chat_id, current_user.id)
        
        # Проверяем права доступа (после назначения, если необходимо)
        if (current_user.role == UserRole.ADMIN and 
            chat.admin_id != current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Вы можете начинать работу только со своими чатами"
            )
        
        working_chat = await self.chat_repo.start_working_on_chat(chat_id, current_user.id)
        return working_chat
    
    async def get_chats_by_status(
        self,
        status: ChatStatus,
        current_user: User
    ) -> List[ChatListResponse]:
        """
        Получить чаты по статусу
        
        Args:
            status: Статус чата
            current_user: Текущий пользователь (должен быть администратором)
            
        Returns:
            Список чатов с указанным статусом
        """
        if current_user.role == UserRole.SUPER_ADMIN:
            chats = await self.chat_repo.get_chats_by_status(status)
        else:
            chats = await self.chat_repo.get_admin_chats_by_status(current_user.id, status)
        
        return chats

