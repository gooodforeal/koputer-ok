from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from app.models.chat import Chat, Message, ChatStatus
from app.models.user import User, UserRole
from app.schemas.chat import ChatCreate, MessageCreateWithChatId


class ChatRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_chat(self, chat_data: ChatCreate) -> Chat:
        """Создать новый чат"""
        chat = Chat(**chat_data.dict())
        self.db.add(chat)
        await self.db.commit()
        await self.db.refresh(chat)
        # Загружаем связанные объекты
        return await self.get_chat_by_id(chat.id) or chat

    async def get_chat_by_id(self, chat_id: int) -> Optional[Chat]:
        """Получить чат по ID с пользователями"""
        result = await self.db.execute(
            select(Chat)
            .options(
                selectinload(Chat.user),
                selectinload(Chat.admin),
                selectinload(Chat.messages).selectinload(Message.sender)
            )
            .where(Chat.id == chat_id)
        )
        return result.scalar_one_or_none()

    async def get_user_chat(self, user_id: int) -> Optional[Chat]:
        """Получить активный чат пользователя"""
        result = await self.db.execute(
            select(Chat)
            .options(
                selectinload(Chat.user),
                selectinload(Chat.admin),
                selectinload(Chat.messages).selectinload(Message.sender)
            )
            .where(and_(Chat.user_id == user_id, Chat.is_active == True))
        )
        return result.scalar_one_or_none()

    async def get_admin_chats(self, admin_id: int) -> List[Chat]:
        """Получить все чаты администратора"""
        result = await self.db.execute(
            select(Chat)
            .options(selectinload(Chat.user), selectinload(Chat.messages))
            .where(Chat.admin_id == admin_id)
            .order_by(Chat.updated_at.desc())
        )
        return result.scalars().all()

    async def get_all_active_chats(self) -> List[Chat]:
        """Получить все активные чаты (для супер-админа)"""
        result = await self.db.execute(
            select(Chat)
            .options(selectinload(Chat.user), selectinload(Chat.admin))
            .where(Chat.is_active == True)
            .order_by(Chat.updated_at.desc())
        )
        return result.scalars().all()

    async def assign_admin_to_chat(self, chat_id: int, admin_id: int) -> Optional[Chat]:
        """Назначить администратора к чату"""
        chat = await self.get_chat_by_id(chat_id)
        if chat:
            # Проверяем, был ли уже назначен администратор
            was_assigned = chat.admin_id is not None
            old_admin_id = chat.admin_id
            
            chat.admin_id = admin_id
            
            # Создаем системное сообщение о назначении администратора
            if not was_assigned or old_admin_id != admin_id:
                # Получаем имя нового администратора
                result = await self.db.execute(
                    select(User).where(User.id == admin_id)
                )
                admin = result.scalar_one_or_none()
                if admin:
                    if not was_assigned:
                        message_content = f"ℹ️ К чату подключен администратор: {admin.name}"
                    else:
                        message_content = f"ℹ️ Администратор чата изменен на: {admin.name}"
                    await self.create_system_message(chat_id, message_content)
            
            await self.db.commit()
            await self.db.refresh(chat)
            # Загружаем связанные объекты
            chat = await self.get_chat_by_id(chat_id) or chat
        return chat

    async def create_message(self, message_data: MessageCreateWithChatId, sender_id: int) -> Message:
        """Создать новое сообщение"""
        message = Message(
            **message_data.dict(),
            sender_id=sender_id
        )
        self.db.add(message)
        await self.db.flush()  # Сохраняем в БД без коммита, чтобы получить ID и created_at
        
        # Обновляем время последнего сообщения в чате
        chat = await self.get_chat_by_id(message_data.chat_id)
        if chat and message.created_at:
            chat.last_message_at = message.created_at
        
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def create_system_message(self, chat_id: int, content: str) -> Message:
        """Создать системное информационное сообщение"""
        # Используем ID первого пользователя чата как отправителя системного сообщения
        chat = await self.get_chat_by_id(chat_id)
        if not chat:
            return None
        
        message = Message(
            chat_id=chat_id,
            sender_id=chat.user_id,  # Используем ID пользователя чата
            content=content,
            message_type="system",  # Специальный тип для системных сообщений
            is_read=False
        )
        self.db.add(message)
        await self.db.flush()
        
        # Обновляем время последнего сообщения в чате
        if message.created_at:
            chat.last_message_at = message.created_at
        
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def get_chat_messages(self, chat_id: int, limit: int = 50, offset: int = 0) -> List[Message]:
        """Получить сообщения чата с пагинацией"""
        result = await self.db.execute(
            select(Message)
            .options(selectinload(Message.sender))
            .where(Message.chat_id == chat_id)
            .order_by(Message.created_at.asc())  # Изменено на asc для хронологического порядка
            .limit(limit)
            .offset(offset)
        )
        return result.scalars().all()

    async def mark_messages_as_read(self, chat_id: int, user_id: int) -> None:
        """Отметить сообщения как прочитанные"""
        # Получаем ID отправителей сообщений, которые не являются текущим пользователем
        await self.db.execute(
            select(Message)
            .where(
                and_(
                    Message.chat_id == chat_id,
                    Message.sender_id != user_id,
                    Message.is_read == False
                )
            )
        )
        
        # Обновляем статус прочтения
        await self.db.execute(
            Message.__table__.update()
            .where(
                and_(
                    Message.chat_id == chat_id,
                    Message.sender_id != user_id,
                    Message.is_read == False
                )
            )
            .values(is_read=True)
        )
        await self.db.commit()

    async def get_unread_count(self, chat_id: int, user_id: int) -> int:
        """Получить количество непрочитанных сообщений для пользователя"""
        result = await self.db.execute(
            select(func.count(Message.id))
            .where(
                and_(
                    Message.chat_id == chat_id,
                    Message.sender_id != user_id,
                    Message.is_read == False
                )
            )
        )
        return result.scalar() or 0

    async def get_user_chats_summary(self, user_id: int) -> List[dict]:
        """Получить краткую информацию о чатах пользователя"""
        result = await self.db.execute(
            select(Chat)
            .options(selectinload(Chat.admin))
            .where(Chat.user_id == user_id)
            .order_by(Chat.updated_at.desc())
        )
        chats = result.scalars().all()
        
        summaries = []
        for chat in chats:
            unread_count = await self.get_unread_count(chat.id, user_id)
            summaries.append({
                "id": chat.id,
                "admin_name": chat.admin.name if chat.admin else None,
                "is_active": chat.is_active,
                "last_message_at": chat.last_message_at,
                "unread_count": unread_count
            })
        
        return summaries

    async def get_admin_chats_summary(self, admin_id: int) -> List[dict]:
        """Получить краткую информацию о чатах администратора"""
        result = await self.db.execute(
            select(Chat)
            .options(selectinload(Chat.user))
            .where(Chat.admin_id == admin_id)
            .order_by(Chat.updated_at.desc())
        )
        chats = result.scalars().all()
        
        summaries = []
        for chat in chats:
            unread_count = await self.get_unread_count(chat.id, admin_id)
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

    async def update_chat_status(self, chat_id: int, status: ChatStatus, admin_id: Optional[int] = None) -> Optional[Chat]:
        """Обновить статус чата"""
        chat = await self.get_chat_by_id(chat_id)
        if chat:
            old_status = chat.status
            chat.status = status
            
            # Если устанавливается статус "в работе" и не назначен администратор,
            # автоматически назначаем переданного администратора
            if (status == ChatStatus.IN_PROGRESS and 
                chat.admin_id is None and 
                admin_id is not None):
                chat.admin_id = admin_id
            
            # Создаем системное сообщение о смене статуса
            if old_status != status:
                status_messages = {
                    ChatStatus.OPEN: "Обращение открыто",
                    ChatStatus.IN_PROGRESS: "Обращение взято в работу",
                    ChatStatus.CLOSED: "Обращение закрыто"
                }
                message_content = f"ℹ️ {status_messages.get(status, f'Статус изменен на {status}')}"
                await self.create_system_message(chat_id, message_content)
            
            await self.db.commit()
            await self.db.refresh(chat)
            # Загружаем связанные объекты
            chat = await self.get_chat_by_id(chat_id) or chat
        return chat

    async def get_chats_by_status(self, status: ChatStatus) -> List[Chat]:
        """Получить чаты по статусу"""
        result = await self.db.execute(
            select(Chat)
            .options(selectinload(Chat.user), selectinload(Chat.admin))
            .where(Chat.status == status)
            .order_by(Chat.updated_at.desc())
        )
        return result.scalars().all()

    async def get_admin_chats_by_status(self, admin_id: int, status: ChatStatus) -> List[Chat]:
        """Получить чаты администратора по статусу"""
        result = await self.db.execute(
            select(Chat)
            .options(selectinload(Chat.user), selectinload(Chat.admin))
            .where(and_(Chat.admin_id == admin_id, Chat.status == status))
            .order_by(Chat.updated_at.desc())
        )
        return result.scalars().all()

    async def close_chat(self, chat_id: int, admin_id: Optional[int] = None) -> Optional[Chat]:
        """Закрыть чат"""
        return await self.update_chat_status(chat_id, ChatStatus.CLOSED, admin_id)

    async def reopen_chat(self, chat_id: int, admin_id: Optional[int] = None) -> Optional[Chat]:
        """Переоткрыть чат"""
        return await self.update_chat_status(chat_id, ChatStatus.OPEN, admin_id)

    async def start_working_on_chat(self, chat_id: int, admin_id: Optional[int] = None) -> Optional[Chat]:
        """Начать работу с чатом"""
        return await self.update_chat_status(chat_id, ChatStatus.IN_PROGRESS, admin_id)
