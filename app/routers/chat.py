from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.dependencies.auth import get_current_user
from app.dependencies.repositories import get_chat_repository
from app.dependencies.roles import require_role
from app.models.user import User, UserRole
from app.repositories.chat_repository import ChatRepository
from app.schemas.chat import (
    ChatCreate, ChatResponse, MessageCreate, MessageCreateWithChatId, MessageResponse, 
    ChatListResponse, ChatSummary, AssignAdminRequest, UpdateChatStatusRequest
)
from app.models.chat import ChatStatus

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def create_chat(
    chat_data: ChatCreate,
    current_user: User = Depends(get_current_user),
    chat_repo: ChatRepository = Depends(get_chat_repository)
):
    """Создать новый чат"""
    # Проверяем, что пользователь создает чат для себя
    if chat_data.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы можете создавать чат только для себя"
        )
    
    # Проверяем, нет ли уже активного чата у пользователя
    existing_chat = await chat_repo.get_user_chat(current_user.id)
    if existing_chat:
        return existing_chat
    
    return await chat_repo.create_chat(chat_data)


@router.get("/my", response_model=ChatResponse)
async def get_my_chat(
    current_user: User = Depends(get_current_user),
    chat_repo: ChatRepository = Depends(get_chat_repository)
):
    """Получить мой чат"""
    chat = await chat_repo.get_user_chat(current_user.id)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Чат не найден"
        )
    return chat


@router.get("/admin", response_model=List[ChatListResponse])
async def get_admin_chats(
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])),
    chat_repo: ChatRepository = Depends(get_chat_repository)
):
    """Получить чаты администратора"""
    if current_user.role == UserRole.SUPER_ADMIN:
        chats = await chat_repo.get_all_active_chats()
    else:
        chats = await chat_repo.get_admin_chats(current_user.id)
    
    return chats


@router.get("/{chat_id}", response_model=ChatResponse)
async def get_chat(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    chat_repo: ChatRepository = Depends(get_chat_repository)
):
    """Получить чат по ID"""
    chat = await chat_repo.get_chat_by_id(chat_id)
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


@router.post("/{chat_id}/assign", response_model=ChatResponse)
async def assign_admin_to_chat(
    chat_id: int,
    request: AssignAdminRequest,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])),
    chat_repo: ChatRepository = Depends(get_chat_repository)
):
    """Назначить администратора к чату"""
    chat = await chat_repo.assign_admin_to_chat(chat_id, request.admin_id)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Чат не найден"
        )
    return chat


@router.post("/{chat_id}/messages", response_model=MessageResponse)
async def send_message(
    chat_id: int,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    chat_repo: ChatRepository = Depends(get_chat_repository)
):
    """Отправить сообщение в чат"""
    # Проверяем существование чата и права доступа
    chat = await chat_repo.get_chat_by_id(chat_id)
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
    
    return await chat_repo.create_message(message_data_with_chat, current_user.id)


@router.get("/{chat_id}/messages", response_model=List[MessageResponse])
async def get_chat_messages(
    chat_id: int,
    limit: int = 50,
    offset: int = 0,
    current_user: User = Depends(get_current_user),
    chat_repo: ChatRepository = Depends(get_chat_repository)
):
    """Получить сообщения чата"""
    # Проверяем существование чата и права доступа
    chat = await chat_repo.get_chat_by_id(chat_id)
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
    
    messages = await chat_repo.get_chat_messages(chat_id, limit, offset)
    
    # Отмечаем сообщения как прочитанные
    await chat_repo.mark_messages_as_read(chat_id, current_user.id)
    
    return messages


@router.post("/{chat_id}/read")
async def mark_chat_as_read(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    chat_repo: ChatRepository = Depends(get_chat_repository)
):
    """Отметить чат как прочитанный"""
    # Проверяем существование чата и права доступа
    chat = await chat_repo.get_chat_by_id(chat_id)
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
    
    await chat_repo.mark_messages_as_read(chat_id, current_user.id)
    return {"message": "Чат отмечен как прочитанный"}


@router.get("/summary/my", response_model=List[dict])
async def get_my_chats_summary(
    current_user: User = Depends(get_current_user),
    chat_repo: ChatRepository = Depends(get_chat_repository)
):
    """Получить краткую информацию о моих чатах"""
    return await chat_repo.get_user_chats_summary(current_user.id)


@router.get("/summary/admin", response_model=List[dict])
async def get_admin_chats_summary(
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])),
    chat_repo: ChatRepository = Depends(get_chat_repository)
):
    """Получить краткую информацию о чатах администратора"""
    if current_user.role == UserRole.SUPER_ADMIN:
        chats = await chat_repo.get_all_active_chats()
        summaries = []
        for chat in chats:
            unread_count = await chat_repo.get_unread_count(chat.id, current_user.id)
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
        return await chat_repo.get_admin_chats_summary(current_user.id)


@router.patch("/{chat_id}/status", response_model=ChatResponse)
async def update_chat_status(
    chat_id: int,
    request: UpdateChatStatusRequest,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])),
    chat_repo: ChatRepository = Depends(get_chat_repository)
):
    """Обновить статус чата"""
    chat = await chat_repo.get_chat_by_id(chat_id)
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
    
    updated_chat = await chat_repo.update_chat_status(chat_id, request.status, current_user.id)
    return updated_chat


@router.post("/{chat_id}/close", response_model=ChatResponse)
async def close_chat(
    chat_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])),
    chat_repo: ChatRepository = Depends(get_chat_repository)
):
    """Закрыть чат"""
    chat = await chat_repo.get_chat_by_id(chat_id)
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
    
    closed_chat = await chat_repo.close_chat(chat_id, current_user.id)
    return closed_chat


@router.post("/{chat_id}/reopen", response_model=ChatResponse)
async def reopen_chat(
    chat_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])),
    chat_repo: ChatRepository = Depends(get_chat_repository)
):
    """Переоткрыть чат"""
    chat = await chat_repo.get_chat_by_id(chat_id)
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
    
    reopened_chat = await chat_repo.reopen_chat(chat_id, current_user.id)
    return reopened_chat


@router.post("/{chat_id}/start-working", response_model=ChatResponse)
async def start_working_on_chat(
    chat_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])),
    chat_repo: ChatRepository = Depends(get_chat_repository)
):
    """Начать работу с чатом"""
    chat = await chat_repo.get_chat_by_id(chat_id)
    if not chat:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Чат не найден"
        )
    
    # Автоматически назначаем администратора, если он не назначен
    if not chat.admin_id:
        chat = await chat_repo.assign_admin_to_chat(chat_id, current_user.id)
    
    # Проверяем права доступа (после назначения, если необходимо)
    if (current_user.role == UserRole.ADMIN and 
        chat.admin_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Вы можете начинать работу только со своими чатами"
        )
    
    working_chat = await chat_repo.start_working_on_chat(chat_id, current_user.id)
    return working_chat


@router.get("/admin/by-status/{status}", response_model=List[ChatListResponse])
async def get_chats_by_status(
    status: ChatStatus,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])),
    chat_repo: ChatRepository = Depends(get_chat_repository)
):
    """Получить чаты по статусу"""
    if current_user.role == UserRole.SUPER_ADMIN:
        chats = await chat_repo.get_chats_by_status(status)
    else:
        chats = await chat_repo.get_admin_chats_by_status(current_user.id, status)
    
    return chats
