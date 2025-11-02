export interface Message {
  id: number;
  chat_id: number;
  sender_id: number;
  content: string;
  is_read: boolean;
  message_type: string;
  created_at: string;
}

export interface Chat {
  id: number;
  user_id: number;
  admin_id?: number;
  is_active: boolean;
  last_message_at?: string;
  created_at: string;
  messages: Message[];
}

export interface ChatSummary {
  id: number;
  user_name?: string;
  admin_name?: string;
  last_message?: string;
  last_message_at?: string;
  unread_count: number;
  is_active: boolean;
}

export interface MessageCreate {
  content: string;
  message_type?: string;
}

export interface ChatCreate {
  user_id: number;
  admin_id?: number;
}

// Экспорты по умолчанию для совместимости
export default {
  Message,
  Chat,
  ChatSummary,
  MessageCreate,
  ChatCreate
};
