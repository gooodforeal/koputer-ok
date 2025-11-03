import axios from 'axios';
import type { Chat, Message, ChatSummary, MessageCreate, ChatCreate, ChatStatus } from '../types/chat-types';
import type {
  FeedbackType,
  FeedbackStatus,
  FeedbackCreate,
  FeedbackUpdate,
  FeedbackAdminUpdate,
  Feedback,
  FeedbackStats,
  FeedbackListResponse
} from '../types/feedback';
import type {
  Build,
  BuildCreate,
  BuildUpdate,
  BuildListResponse,
  BuildTopResponse,
  BuildRating,
  BuildRatingCreate,
  BuildRatingUpdate,
  BuildComment,
  BuildCommentCreate,
  BuildCommentUpdate,
  BuildCommentListResponse,
  BuildStats,
  BuildComponents,
  Component
} from '../types/build';
import type {
  Balance,
  Transaction,
  TransactionListResponse,
  PaymentCreate,
  PaymentResponse,
  BalanceStats,
  PaymentStatus,
  TransactionType,
  TransactionStatus
} from '../types/balance';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,  // Включаем отправку credentials для CORS
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle auth errors
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Chat API functions
export const chatApi = {
  // Создать чат
  createChat: async (chatData: ChatCreate): Promise<Chat> => {
    const response = await api.post('/api/chat/', chatData);
    return response.data;
  },

  // Получить мой чат
  getMyChat: async (): Promise<Chat> => {
    const response = await api.get('/api/chat/my');
    return response.data;
  },

  // Получить чат по ID
  getChat: async (chatId: number) => {
    const response = await api.get(`/api/chat/${chatId}`);
    return response;
  },

  // Получить чаты администратора
  getAdminChats: async () => {
    const response = await api.get('/api/chat/admin');
    return response;
  },

  // Назначить администратора к чату
  assignAdmin: async (chatId: number, adminId: number): Promise<Chat> => {
    const response = await api.post(`/api/chat/${chatId}/assign`, { admin_id: adminId });
    return response.data;
  },

  // Отправить сообщение
  sendMessage: async (chatId: number, messageData: MessageCreate) => {
    const response = await api.post(`/api/chat/${chatId}/messages`, messageData);
    return response;
  },

  // Получить сообщения чата
  getChatMessages: async (chatId: number, limit = 50, offset = 0): Promise<Message[]> => {
    const response = await api.get(`/api/chat/${chatId}/messages`, {
      params: { limit, offset }
    });
    return response.data;
  },

  // Отметить чат как прочитанный
  markAsRead: async (chatId: number): Promise<void> => {
    await api.post(`/api/chat/${chatId}/read`);
  },

  // Получить краткую информацию о моих чатах
  getMyChatsSummary: async (): Promise<ChatSummary[]> => {
    const response = await api.get('/api/chat/summary/my');
    return response.data;
  },

  // Получить краткую информацию о чатах администратора
  getAdminChatsSummary: async (): Promise<ChatSummary[]> => {
    const response = await api.get('/api/chat/summary/admin');
    return response.data;
  },

  // Обновить статус чата
  updateChatStatus: async (chatId: number, status: ChatStatus): Promise<Chat> => {
    const response = await api.patch(`/api/chat/${chatId}/status`, { status });
    return response.data;
  },

  // Закрыть чат
  closeChat: async (chatId: number): Promise<Chat> => {
    const response = await api.post(`/api/chat/${chatId}/close`);
    return response.data;
  },

  // Переоткрыть чат
  reopenChat: async (chatId: number): Promise<Chat> => {
    const response = await api.post(`/api/chat/${chatId}/reopen`);
    return response.data;
  },

  // Начать работу с чатом
  startWorkingOnChat: async (chatId: number): Promise<Chat> => {
    const response = await api.post(`/api/chat/${chatId}/start-working`);
    return response.data;
  },

  // Получить чаты по статусу
  getChatsByStatus: async (status: ChatStatus): Promise<Chat[]> => {
    const response = await api.get(`/api/chat/admin/by-status/${status}`);
    return response.data;
  }
};

// User API functions
export const userApi = {
  // Получить профиль пользователя
  getProfile: async () => {
    const response = await api.get('/api/users/profile');
    return response.data;
  },

  // Обновить профиль пользователя
  updateProfile: async (profileData: { name?: string; email?: string; picture?: string }) => {
    const response = await api.put('/api/users/profile', profileData);
    return response.data;
  }
};

// Feedback API functions
export const feedbackApi = {
  // Создать отзыв
  createFeedback: async (feedbackData: FeedbackCreate): Promise<Feedback> => {
    const response = await api.post('/api/feedback/', feedbackData);
    return response.data;
  },

  // Получить все отзывы
  getAllFeedbacks: async (
    skip = 0,
    limit = 100,
    status?: FeedbackStatus,
    type?: FeedbackType
  ): Promise<FeedbackListResponse> => {
    const response = await api.get('/api/feedback/', {
      params: {
        skip,
        limit,
        status_filter: status,
        type_filter: type
      }
    });
    return response.data;
  },
  
  // Получить все публичные отзывы (доступно без авторизации)
  getPublicFeedbacks: async (
    skip = 0,
    limit = 100
  ): Promise<FeedbackListResponse> => {
    const response = await axios.get(`${API_BASE_URL}/api/feedback/public`, {
      params: { skip, limit }
    });
    return response.data;
  },

  // Получить мои отзывы
  getMyFeedbacks: async (skip = 0, limit = 100): Promise<FeedbackListResponse> => {
    const response = await api.get('/api/feedback/my', {
      params: { skip, limit }
    });
    return response.data;
  },

  // Получить отзывы, назначенные мне
  getAssignedFeedbacks: async (skip = 0, limit = 100): Promise<FeedbackListResponse> => {
    const response = await api.get('/api/feedback/assigned', {
      params: { skip, limit }
    });
    return response.data;
  },

  // Получить статистику по отзывам
  getFeedbackStats: async (): Promise<FeedbackStats> => {
    const response = await api.get('/api/feedback/stats');
    return response.data;
  },

  // Получить отзыв по ID
  getFeedback: async (feedbackId: number): Promise<Feedback> => {
    const response = await api.get(`/api/feedback/${feedbackId}`);
    return response.data;
  },

  // Обновить свой отзыв
  updateFeedback: async (feedbackId: number, feedbackData: FeedbackUpdate): Promise<Feedback> => {
    const response = await api.put(`/api/feedback/${feedbackId}`, feedbackData);
    return response.data;
  },

  // Обновить отзыв администратором
  adminUpdateFeedback: async (feedbackId: number, feedbackData: FeedbackAdminUpdate): Promise<Feedback> => {
    const response = await api.patch(`/api/feedback/${feedbackId}/admin`, feedbackData);
    return response.data;
  },

  // Удалить отзыв
  deleteFeedback: async (feedbackId: number): Promise<void> => {
    await api.delete(`/api/feedback/${feedbackId}`);
  }
};

// Builds API functions
export const buildsApi = {
  // Создать сборку
  createBuild: async (buildData: BuildCreate): Promise<Build> => {
    const response = await api.post('/api/builds/', buildData);
    return response.data;
  },

  // Получить список сборок
  getBuilds: async (
    skip = 0,
    limit = 20,
    query = '',
    authorId?: number,
    sortBy: string = 'created_at',
    order: string = 'desc'
  ): Promise<BuildListResponse> => {
    const params: any = { skip, limit };
    if (query) params.query = query;
    if (authorId) params.author_id = authorId;
    if (sortBy) params.sort_by = sortBy;
    if (order) params.order = order;
    
    const response = await api.get('/api/builds/', { params });
    return response.data;
  },

  // Получить топ сборок
  getTopBuilds: async (limit = 10): Promise<BuildTopResponse> => {
    const response = await api.get('/api/builds/top', { params: { limit } });
    return response.data;
  },

  // Получить мои сборки
  getMyBuilds: async (skip = 0, limit = 20): Promise<BuildListResponse> => {
    const response = await api.get('/api/builds/my', { params: { skip, limit } });
    return response.data;
  },

  // Получить статистику сборок
  getBuildStats: async (): Promise<BuildStats> => {
    const response = await api.get('/api/builds/stats');
    return response.data;
  },

  // Получить уникальные компоненты для автозаполнения
  getUniqueComponents: async (): Promise<BuildComponents> => {
    const response = await api.get('/api/builds/components/unique');
    return response.data;
  },

  // Получить сборку по ID
  getBuild: async (buildId: number): Promise<Build> => {
    const response = await api.get(`/api/builds/${buildId}`);
    return response.data;
  },

  // Обновить сборку
  updateBuild: async (buildId: number, buildData: BuildUpdate): Promise<Build> => {
    const response = await api.put(`/api/builds/${buildId}`, buildData);
    return response.data;
  },

  // Удалить сборку
  deleteBuild: async (buildId: number): Promise<void> => {
    await api.delete(`/api/builds/${buildId}`);
  },

  // === Методы для оценок ===
  
  // Поставить оценку
  createRating: async (buildId: number, ratingData: BuildRatingCreate): Promise<BuildRating> => {
    const response = await api.post(`/api/builds/${buildId}/ratings`, ratingData);
    return response.data;
  },

  // Обновить оценку
  updateRating: async (buildId: number, ratingData: BuildRatingUpdate): Promise<BuildRating> => {
    const response = await api.put(`/api/builds/${buildId}/ratings`, ratingData);
    return response.data;
  },

  // Удалить оценку
  deleteRating: async (buildId: number): Promise<void> => {
    await api.delete(`/api/builds/${buildId}/ratings`);
  },

  // Получить мою оценку
  getMyRating: async (buildId: number): Promise<BuildRating> => {
    const response = await api.get(`/api/builds/${buildId}/ratings/my`);
    return response.data;
  },

  // === Методы для комментариев ===
  
  // Создать комментарий
  createComment: async (buildId: number, commentData: BuildCommentCreate): Promise<BuildComment> => {
    const response = await api.post(`/api/builds/${buildId}/comments`, commentData);
    return response.data;
  },

  // Получить комментарии
  getComments: async (buildId: number, skip = 0, limit = 50): Promise<BuildCommentListResponse> => {
    const response = await api.get(`/api/builds/${buildId}/comments`, {
      params: { skip, limit }
    });
    return response.data;
  },

  // Обновить комментарий
  updateComment: async (buildId: number, commentId: number, commentData: BuildCommentUpdate): Promise<BuildComment> => {
    const response = await api.put(`/api/builds/${buildId}/comments/${commentId}`, commentData);
    return response.data;
  },

  // Удалить комментарий
  deleteComment: async (buildId: number, commentId: number): Promise<void> => {
    await api.delete(`/api/builds/${buildId}/comments/${commentId}`);
  },

  // Экспортировать сборку в PDF
  exportPdf: async (buildId: number): Promise<Blob> => {
    const response = await api.get(`/api/builds/${buildId}/export/pdf`, {
      responseType: 'blob'
    });
    return response.data;
  }
};

// Balance API functions
export const balanceApi = {
  // Получить баланс
  getBalance: async (): Promise<Balance> => {
    const response = await api.get('/api/balance/');
    return response.data;
  },

  // Получить статистику баланса
  getBalanceStats: async (): Promise<BalanceStats> => {
    const response = await api.get('/api/balance/stats');
    return response.data;
  },

  // Получить транзакции
  getTransactions: async (
    page: number = 1,
    per_page: number = 20,
    transaction_type?: TransactionType,
    status?: TransactionStatus
  ): Promise<TransactionListResponse> => {
    const params: any = { page, per_page };
    if (transaction_type) params.transaction_type = transaction_type;
    if (status) params.status = status;
    
    const response = await api.get('/api/balance/transactions', { params });
    return response.data;
  },

  // Создать платеж
  createPayment: async (paymentData: PaymentCreate): Promise<PaymentResponse> => {
    const response = await api.post('/api/balance/payment/create', paymentData);
    return response.data;
  },

  // Получить статус платежа
  getPaymentStatus: async (payment_id: string): Promise<PaymentStatus> => {
    const response = await api.get(`/api/balance/payment/${payment_id}/status`);
    return response.data;
  }
};

// Components API functions
export const componentsApi = {
  // Запустить парсинг компонентов
  startParsing: async (clearExisting: boolean = true): Promise<{ message: string; status: string }> => {
    const response = await api.post(`/api/components/parse?clear_existing=${clearExisting}`);
    return response.data;
  },

  // Получить статус парсинга
  getParseStatus: async (): Promise<{
    is_running: boolean;
    current_category: string | null;
    processed_categories: number;
    total_categories: number;
    processed_products: number;
    errors: string[];
  }> => {
    const response = await api.get('/api/components/parse/status');
    return response.data;
  },

  // Получить статистику компонентов
  getComponentStats: async (): Promise<{
    total: number;
    by_category: Record<string, number>;
  }> => {
    const response = await api.get('/api/components/stats');
    return response.data;
  },

  // Остановить парсинг компонентов
  stopParsing: async (): Promise<{ message: string; status: string }> => {
    const response = await api.post('/api/components/parse/stop');
    return response.data;
  },

  // Получить компоненты по категории с поиском
  getComponentsByCategory: async (
    category: string,
    query: string = '',
    skip: number = 0,
    limit: number = 100
  ): Promise<Component[]> => {
    const response = await api.get('/api/components/by-category', {
      params: { category, query, skip, limit }
    });
    return response.data;
  }
};



