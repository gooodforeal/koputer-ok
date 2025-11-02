export type Message = {
  id: number;
  chat_id: number;
  sender_id: number;
  content: string;
  is_read: boolean;
  message_type: string;
  created_at: string;
};

export type ChatStatus = 'OPEN' | 'IN_PROGRESS' | 'CLOSED';

export type Chat = {
  id: number;
  user_id: number;
  admin_id?: number;
  is_active: boolean;
  status: ChatStatus;
  last_message_at?: string;
  created_at: string;
  messages: Message[];
  user: {
    id: number;
    name: string;
    email: string;
  };
  admin?: {
    id: number;
    name: string;
    email: string;
  };
};

export type ChatSummary = {
  id: number;
  user_name: string;
  admin_name?: string;
  last_message?: string;
  last_message_at: string;
  unread_count: number;
  is_active: boolean;
  status: ChatStatus;
};

export type MessageCreate = {
  content: string;
  message_type?: string;
};

export type ChatCreate = {
  user_id: number;
  admin_id?: number;
  status?: ChatStatus;
};

export type UpdateChatStatusRequest = {
  status: ChatStatus;
};
