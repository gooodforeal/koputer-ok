from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from app.models.user import UserRole
from app.models.chat import ChatStatus


class MessageBase(BaseModel):
    content: str
    message_type: str = "text"


class MessageCreate(MessageBase):
    pass


class MessageCreateWithChatId(MessageBase):
    chat_id: int


class AssignAdminRequest(BaseModel):
    admin_id: int


class UpdateChatStatusRequest(BaseModel):
    status: ChatStatus


class MessageResponse(MessageBase):
    id: int
    chat_id: int
    sender_id: int
    is_read: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class ChatBase(BaseModel):
    user_id: int
    admin_id: Optional[int] = None
    status: ChatStatus = ChatStatus.OPEN


class ChatCreate(ChatBase):
    pass


class UserInfo(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    
    class Config:
        from_attributes = True


class ChatResponse(ChatBase):
    id: int
    is_active: bool
    last_message_at: Optional[datetime]
    created_at: datetime
    messages: List[MessageResponse] = []
    user: UserInfo
    admin: Optional[UserInfo] = None
    
    class Config:
        from_attributes = True


class ChatListResponse(BaseModel):
    id: int
    user_id: int
    admin_id: Optional[int]
    is_active: bool
    status: ChatStatus
    last_message_at: Optional[datetime]
    created_at: datetime
    user_name: Optional[str] = None
    admin_name: Optional[str] = None
    unread_count: int = 0
    
    class Config:
        from_attributes = True


class ChatSummary(BaseModel):
    """Краткая информация о чате для списка"""
    id: int
    user_name: str
    admin_name: Optional[str]
    last_message: Optional[str]
    last_message_at: Optional[datetime]
    unread_count: int
    is_active: bool
    status: ChatStatus
