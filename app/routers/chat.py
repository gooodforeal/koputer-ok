from fastapi import APIRouter, Depends, Query
from typing import List
from app.dependencies.auth import get_current_user
from app.dependencies import get_chat_service
from app.dependencies.roles import require_role
from app.models.user import User, UserRole
from app.services.chat_service import ChatService
from app.schemas.chat import (
    ChatCreate, ChatResponse, MessageCreate, MessageResponse, 
    ChatListResponse, AssignAdminRequest, UpdateChatStatusRequest
)
from app.models.chat import ChatStatus

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def create_chat(
    chat_data: ChatCreate,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Создать новый чат"""
    return await chat_service.create_chat(chat_data, current_user)


@router.get("/my", response_model=ChatResponse)
async def get_my_chat(
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Получить мой чат"""
    return await chat_service.get_user_chat(current_user)


@router.get("/admin", response_model=List[ChatListResponse])
async def get_admin_chats(
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Получить чаты администратора"""
    return await chat_service.get_admin_chats(current_user)


@router.get("/{chat_id}", response_model=ChatResponse)
async def get_chat(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Получить чат по ID"""
    return await chat_service.get_chat(chat_id, current_user)


@router.post("/{chat_id}/assign", response_model=ChatResponse)
async def assign_admin_to_chat(
    chat_id: int,
    request: AssignAdminRequest,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Назначить администратора к чату"""
    return await chat_service.assign_admin_to_chat(chat_id, request, current_user)


@router.post("/{chat_id}/messages", response_model=MessageResponse)
async def send_message(
    chat_id: int,
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Отправить сообщение в чат"""
    return await chat_service.send_message(chat_id, message_data, current_user)


@router.get("/{chat_id}/messages", response_model=List[MessageResponse])
async def get_chat_messages(
    chat_id: int,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Получить сообщения чата"""
    return await chat_service.get_chat_messages(chat_id, limit, offset, current_user)


@router.post("/{chat_id}/read")
async def mark_chat_as_read(
    chat_id: int,
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Отметить чат как прочитанный"""
    return await chat_service.mark_chat_as_read(chat_id, current_user)


@router.get("/summary/my", response_model=List[dict])
async def get_my_chats_summary(
    current_user: User = Depends(get_current_user),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Получить краткую информацию о моих чатах"""
    return await chat_service.get_user_chats_summary(current_user)


@router.get("/summary/admin", response_model=List[dict])
async def get_admin_chats_summary(
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Получить краткую информацию о чатах администратора"""
    return await chat_service.get_admin_chats_summary(current_user)


@router.patch("/{chat_id}/status", response_model=ChatResponse)
async def update_chat_status(
    chat_id: int,
    request: UpdateChatStatusRequest,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Обновить статус чата"""
    return await chat_service.update_chat_status(chat_id, request, current_user)


@router.post("/{chat_id}/close", response_model=ChatResponse)
async def close_chat(
    chat_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Закрыть чат"""
    return await chat_service.close_chat(chat_id, current_user)


@router.post("/{chat_id}/reopen", response_model=ChatResponse)
async def reopen_chat(
    chat_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Переоткрыть чат"""
    return await chat_service.reopen_chat(chat_id, current_user)


@router.post("/{chat_id}/start-working", response_model=ChatResponse)
async def start_working_on_chat(
    chat_id: int,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Начать работу с чатом"""
    return await chat_service.start_working_on_chat(chat_id, current_user)


@router.get("/admin/by-status/{status}", response_model=List[ChatListResponse])
async def get_chats_by_status(
    status: ChatStatus,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.SUPER_ADMIN])),
    chat_service: ChatService = Depends(get_chat_service)
):
    """Получить чаты по статусу"""
    return await chat_service.get_chats_by_status(status, current_user)
