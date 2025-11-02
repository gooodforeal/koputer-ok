import type { ChatStatus } from '../types/chat-types';

export const CHAT_STATUS_LABELS: Record<ChatStatus, string> = {
  OPEN: 'Открыт',
  IN_PROGRESS: 'В работе',
  CLOSED: 'Закрыт'
};

export const CHAT_STATUS_COLORS: Record<ChatStatus, string> = {
  OPEN: 'bg-green-100 text-green-800',
  IN_PROGRESS: 'bg-yellow-100 text-yellow-800',
  CLOSED: 'bg-gray-100 text-gray-800'
};

export const getChatStatusLabel = (status: ChatStatus): string => {
  return CHAT_STATUS_LABELS[status];
};

export const getChatStatusColor = (status: ChatStatus): string => {
  return CHAT_STATUS_COLORS[status];
};

export const getNextStatus = (currentStatus: ChatStatus): ChatStatus | null => {
  switch (currentStatus) {
    case 'OPEN':
      return 'IN_PROGRESS';
    case 'IN_PROGRESS':
      return 'CLOSED';
    case 'CLOSED':
      return 'OPEN';
    default:
      return null;
  }
};

export const canChangeStatus = (currentStatus: ChatStatus, newStatus: ChatStatus): boolean => {
  // Можно переходить между любыми статусами
  return true;
};
