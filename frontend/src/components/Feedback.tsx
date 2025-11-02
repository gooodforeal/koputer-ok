import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { chatApi } from '../services/api';
import type { Chat, Message, MessageCreate, ChatStatus } from '../types/chat-types';
import { useAuth } from '../contexts/AuthContext';
import { UserRole } from '../types/user';
import { getChatStatusLabel, getChatStatusColor } from '../utils/chatStatus';
import AdminStats from './AdminStats';
import MessageTemplates from './MessageTemplates';

// Простой компонент выбора статуса как MessageTemplates
const StatusSelector: React.FC<{
  status: ChatStatus;
  onStatusChange: (status: ChatStatus) => void;
  disabled?: boolean;
}> = React.memo(({ status, onStatusChange, disabled = false }) => {
  const [isOpen, setIsOpen] = useState(false);

  const statusOptions = useMemo(() => [
    { value: 'OPEN' as ChatStatus, label: 'Открыт', color: 'text-red-600 dark:text-red-400' },
    { value: 'IN_PROGRESS' as ChatStatus, label: 'В работе', color: 'text-yellow-600 dark:text-yellow-400' },
    { value: 'CLOSED' as ChatStatus, label: 'Закрыт', color: 'text-green-600 dark:text-green-400' }
  ], []);

  const currentStatus = statusOptions.find(option => option.value === status) || statusOptions[0];

  const handleStatusSelect = useCallback((newStatus: ChatStatus) => {
    onStatusChange(newStatus);
    setIsOpen(false);
  }, [onStatusChange]);

  const toggleOpen = useCallback(() => {
    if (!disabled) {
      setIsOpen(prev => !prev);
    }
  }, [disabled]);

  const closeDropdown = useCallback(() => {
    setIsOpen(false);
  }, []);

  return (
    <div className="relative">
      <div className="flex items-center gap-2">
        <span className="text-sm text-gray-600 dark:text-gray-400">Статус:</span>
        <button
          onClick={toggleOpen}
          disabled={disabled}
          className="px-3 py-1.5 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
        >
          <span className={`text-sm font-medium ${currentStatus.color}`}>
            {currentStatus.label}
          </span>
          <svg className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      </div>

      {isOpen && (
        <div className="absolute top-full left-0 mt-1 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-50">
          <div className="p-2">
            <div className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-2 px-2">
              Выберите статус
            </div>
            <div className="space-y-1">
              {statusOptions.map((option) => (
                <button
                  key={option.value}
                  onClick={() => handleStatusSelect(option.value)}
                  className={`w-full text-left px-3 py-2 text-sm rounded-lg transition-colors ${
                    status === option.value
                      ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
                      : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700'
                  }`}
                >
                  <span className={option.color}>{option.label}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {isOpen && (
        <div 
          className="fixed inset-0 z-40" 
          onClick={closeDropdown}
        ></div>
      )}
    </div>
  );
});

StatusSelector.displayName = 'StatusSelector';

// Мемоизированный компонент сообщения
const MessageItem = React.memo<{
  message: Message;
  isOwnMessage: boolean;
  formatTime: (dateString: string) => string;
}>(({ message, isOwnMessage, formatTime }) => {
  // Проверяем, является ли сообщение системным
  const isSystemMessage = message.message_type === 'system';
  
  if (isSystemMessage) {
    // Системное сообщение - отображается по центру
    return (
      <div id={`message-${message.id || 0}`} className="flex justify-center my-4">
        <div className="bg-blue-50 dark:bg-blue-900 text-blue-800 dark:text-blue-100 px-6 py-3 rounded-full text-sm font-medium border border-blue-200 dark:border-blue-700 max-w-md text-center shadow-sm">
          {message.content || 'Системное сообщение'}
        </div>
      </div>
    );
  }
  
  // Обычное сообщение пользователя/администратора
  return (
    <div
      id={`message-${message.id || 0}`}
      className={`flex ${isOwnMessage ? 'justify-end' : 'justify-start'}`}
    >
      <div className={`max-w-2xl ${isOwnMessage ? 'order-2' : 'order-1'}`}>
        <div
          className={`px-6 py-4 rounded-2xl shadow-sm ${
            isOwnMessage
              ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white'
              : 'bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200 border border-gray-200 dark:border-gray-600'
          }`}
        >
          <p className="text-base leading-relaxed break-words overflow-wrap-anywhere whitespace-pre-wrap">{message.content || 'Пустое сообщение'}</p>
          <p className={`text-sm mt-3 ${
            isOwnMessage ? 'text-blue-100' : 'text-gray-500 dark:text-gray-400'
          }`}>
            {formatTime(message.created_at || '')}
          </p>
        </div>
      </div>
    </div>
  );
});

interface ChatSummary {
  id: number;
  user_name: string;
  admin_name?: string;
  is_active: boolean;
  status: ChatStatus;
  last_message_at: string;
  unread_count: number;
}

const Feedback: React.FC = () => {
  const [chats, setChats] = useState<ChatSummary[]>([]);
  const [selectedChat, setSelectedChat] = useState<Chat | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<ChatStatus | 'ALL'>('ALL');
  const [showChatList, setShowChatList] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { user } = useAuth();
  
  const isAdmin = user?.role === UserRole.ADMIN || user?.role === UserRole.SUPER_ADMIN;

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    loadChats();
  }, []);

  const loadChats = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      console.log('Загружаем чаты администратора...');
      const response = await chatApi.getAdminChatsSummary();
      console.log('Получены чаты:', response);
      setChats(response);
    } catch (error: any) {
      console.error('Ошибка загрузки чатов:', error);
      setError('Ошибка загрузки чатов: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  }, []);

  const loadChat = useCallback(async (chatId: number) => {
    try {
      setLoading(true);
      setError(null);
      console.log('Loading chat:', chatId);
      
      // Загружаем информацию о чате с сообщениями
      const chatResponse = await chatApi.getChat(chatId || 0);
      console.log('Chat response:', chatResponse.data);
      setSelectedChat(chatResponse.data);
      setMessages(chatResponse.data.messages || []);
      
      // Скрываем список чатов при открытии чата
      setShowChatList(false);
      
      // Отмечаем сообщения как прочитанные
      await chatApi.markAsRead(chatId || 0);
      
      // Обновляем список чатов
      loadChats();
    } catch (error: any) {
      console.error('Error loading chat:', error);
      setError('Ошибка загрузки чата: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  }, [loadChats]);

  const sendMessage = useCallback(async () => {
    if (!(newMessage || '').trim() || !selectedChat) return;

    const messageData: MessageCreate = {
      content: (newMessage || '').trim(),
      message_type: 'text'
    };

    try {
      const response = await chatApi.sendMessage(selectedChat.id || 0, messageData);
      setMessages(prev => [...prev, response.data]);
      setNewMessage('');
      
      // Обновляем список чатов
      loadChats();
      
      // Прокручиваем к новому сообщению после отправки
      setTimeout(() => {
        scrollToBottom();
      }, 100);
    } catch (error: any) {
      setError('Ошибка отправки сообщения: ' + (error.response?.data?.detail || error.message));
    }
  }, [newMessage, selectedChat, loadChats]);

  const updateChatStatus = useCallback(async (chatId: number, status: ChatStatus) => {
    try {
      await chatApi.updateChatStatus(chatId || 0, status);
      loadChat(chatId || 0);
      loadChats();
    } catch (error: any) {
      setError('Ошибка обновления статуса: ' + (error.response?.data?.detail || error.message));
    }
  }, [loadChat, loadChats]);

  const handleBackToList = useCallback(() => {
    setShowChatList(true);
    setSelectedChat(null);
    setMessages([]);
  }, []);

  const handleKeyPress = useCallback((e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
    // Shift + Enter позволяет переходить на новую строку
  }, [sendMessage]);

  const formatTime = useCallback((dateString: string) => {
    if (!dateString) return '--:--';
    
    try {
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return '--:--';
      
      return date.toLocaleTimeString('ru-RU', { 
        hour: '2-digit', 
        minute: '2-digit' 
      });
    } catch (error) {
      return '--:--';
    }
  }, []);

  const formatDate = (dateString: string) => {
    if (!dateString) return '--/--/----';
    
    try {
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return '--/--/----';
      
      return date.toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
      });
    } catch (error) {
      return '--/--/----';
    }
  };

  const getRelativeTime = (dateString: string) => {
    if (!dateString) return 'Нет данных';
    
    try {
      const date = new Date(dateString);
      if (isNaN(date.getTime())) return 'Неверная дата';
      
      const now = new Date();
      const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
      
      if (diffInMinutes < 1) return 'только что';
      if (diffInMinutes < 60) return `${diffInMinutes} мин назад`;
      if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)} ч назад`;
      return formatDate(dateString);
    } catch (error) {
      return 'Ошибка даты';
    }
  };

  // Фильтрация чатов с мемоизацией
  const filteredChats = useMemo(() => {
    return chats.filter(chat => {
      const matchesSearch = chat.user_name?.toLowerCase().includes((searchQuery || '').toLowerCase()) ?? false;
      const matchesStatus = statusFilter === 'ALL' || (chat.status || 'OPEN') === statusFilter;
      return matchesSearch && matchesStatus;
    });
  }, [chats, searchQuery, statusFilter]);

  if (!isAdmin) {
    return (
      <div className="theme-transition min-h-screen bg-gray-50 dark:bg-gray-900 py-8 px-4">
        <div className="theme-transition max-w-4xl mx-auto bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
          <div className="text-center">
            <svg className="w-20 h-20 mx-auto mb-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Доступ запрещен</h3>
            <p className="text-gray-600 dark:text-gray-400 mb-4">У вас нет прав для доступа к панели обращений</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="theme-transition min-h-screen bg-gray-50 dark:bg-gray-900 py-8 px-4">
      <div className="theme-transition max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-blue-700 text-white p-6 rounded-2xl mb-6">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="font-bold text-3xl mb-2">Управление обращениями</h1>
              <div className="flex items-center gap-4 text-blue-100">
                <span className="flex items-center gap-2">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M2 5a2 2 0 012-2h7a2 2 0 012 2v4a2 2 0 01-2 2H9l-3 3v-3H4a2 2 0 01-2-2V5z" />
                  </svg>
                  Всего: {chats?.length || 0}
                </span>
                <span className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-red-400 rounded-full"></div>
                  Активных: {(chats || []).filter(c => (c.status || 'OPEN') === 'OPEN').length}
                </span>
                <span className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-yellow-400 rounded-full"></div>
                  В работе: {(chats || []).filter(c => (c.status || 'OPEN') === 'IN_PROGRESS').length}
                </span>
                <span className="flex items-center gap-2">
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  Закрытых: {(chats || []).filter(c => (c.status || 'OPEN') === 'CLOSED').length}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Статистика */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-200 dark:border-gray-700 mb-6">
          <AdminStats
            totalChats={chats?.length || 0}
            openChats={(chats || []).filter(c => (c.status || 'OPEN') === 'OPEN').length}
            inProgressChats={(chats || []).filter(c => (c.status || 'OPEN') === 'IN_PROGRESS').length}
            closedChats={(chats || []).filter(c => (c.status || 'OPEN') === 'CLOSED').length}
            unreadMessages={(chats || []).reduce((sum, chat) => sum + (chat.unread_count || 0), 0)}
          />
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
          <div className="flex h-[600px]">
            {/* Список чатов */}
            <div className={`${showChatList ? 'w-1/4' : 'w-0'} transition-all duration-300 ease-in-out border-r border-gray-200 dark:border-gray-600 flex flex-col bg-gray-50 dark:bg-gray-900 overflow-hidden`}>
              {/* Фильтры и поиск */}
              <div className="p-4 border-b border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-800">
                <div className="space-y-3">
                  <div className="relative">
                    <input
                      type="text"
                      placeholder="Поиск по имени пользователя..."
                      value={searchQuery || ''}
                      onChange={(e) => setSearchQuery(e.target.value || '')}
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                    />
                    <svg className="absolute left-3 top-2.5 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                    </svg>
                  </div>
                  <div className="flex gap-2">
                    {(['ALL', 'OPEN', 'IN_PROGRESS', 'CLOSED'] as const).map((status) => (
                      <button
                        key={status}
                        onClick={() => setStatusFilter(status)}
                        className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                          statusFilter === status
                            ? 'bg-blue-600 text-white'
                            : 'bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-500'
                        }`}
                      >
                        {status === 'ALL' ? 'Все' : getChatStatusLabel(status)}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
              
              <div className="flex-1 overflow-y-auto">
                {loading && (chats?.length || 0) === 0 ? (
                  <div className="flex justify-center items-center h-full">
                    <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                  </div>
                ) : error ? (
                  <div className="text-red-600 text-center p-4">
                    <div className="bg-red-50 dark:bg-red-900/20 p-4 rounded-lg">
                      <svg className="w-8 h-8 mx-auto mb-2 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      {error}
                      <button
                        onClick={loadChats}
                        className="block mt-2 text-blue-600 hover:text-blue-800 underline"
                      >
                        Попробовать снова
                      </button>
                    </div>
                  </div>
                ) : (filteredChats || []).length === 0 ? (
                  <div className="text-gray-500 text-center p-8">
                    <svg className="w-12 h-12 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                    </svg>
                    <p className="text-lg font-medium mb-2">Нет обращений</p>
                    <p className="text-sm">Пока нет обращений, соответствующих выбранным фильтрам</p>
                  </div>
                ) : (
                  <div className="space-y-1 p-2">
                    {(filteredChats || []).map((chat) => (
                      <div
                        key={chat.id || 0}
                        className={`p-4 rounded-xl cursor-pointer transition-all duration-200 ${
                          (selectedChat?.id || 0) === (chat.id || 0)
                            ? 'bg-blue-100 dark:bg-blue-900/30 border-2 border-blue-300 dark:border-blue-600 shadow-md'
                            : 'hover:bg-gray-100 dark:hover:bg-gray-700 hover:shadow-sm border-2 border-transparent'
                        }`}
                        onClick={() => loadChat(chat.id || 0)}
                      >
                        <div className="flex justify-between items-start">
                          <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-2">
                              <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-semibold text-sm">
                                {chat.user_name?.charAt(0).toUpperCase() || '?'}
                              </div>
                              <div className="flex-1 min-w-0">
                                <h5 className="font-semibold text-gray-900 dark:text-white truncate">
                                  {chat.user_name || 'Неизвестный пользователь'}
                                </h5>
                                <p className="text-xs text-gray-500 dark:text-gray-400">
                                  {chat.last_message_at ? getRelativeTime(chat.last_message_at) : 'Нет сообщений'}
                                </p>
                              </div>
                            </div>
                            <div className="flex items-center gap-2 mb-2">
                              <span className={`text-xs px-2 py-1 rounded-full font-medium ${getChatStatusColor(chat.status || 'OPEN')}`}>
                                {getChatStatusLabel(chat.status || 'OPEN')}
                              </span>
                              {chat.admin_name && (
                                <span className="text-xs text-blue-600 dark:text-blue-400 bg-blue-50 dark:bg-blue-900/30 px-2 py-1 rounded-full">
                                  {chat.admin_name || 'Неизвестный админ'}
                                </span>
                              )}
                            </div>
                          </div>
                          {(chat.unread_count || 0) > 0 && (
                            <span className="bg-red-500 text-white text-xs rounded-full px-2 py-1 font-bold min-w-[20px] text-center">
                              {chat.unread_count || 0}
                            </span>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Область сообщений */}
            <div className={`${showChatList ? 'flex-1' : 'w-full'} flex flex-col bg-white dark:bg-gray-800 transition-all duration-300 ease-in-out`}>
              {selectedChat ? (
                <>
                  {/* Заголовок чата */}
                  <div className="p-4 border-b border-gray-200 dark:border-gray-600 bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-700 dark:to-gray-800">
                    <div className="flex justify-between items-start">
                      <div className="flex items-center gap-3 flex-1">
                        {/* Кнопка "Назад" */}
                        <button
                          onClick={handleBackToList}
                          className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-200 dark:hover:bg-gray-600 rounded-lg transition-colors"
                          title="Вернуться к списку обращений"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                          </svg>
                          Назад
                        </button>
                        <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-bold text-base">
                          {selectedChat.user.name?.charAt(0).toUpperCase() || '?'}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <h4 className="font-bold text-lg text-gray-900 dark:text-white">
                              {selectedChat.user.name || 'Неизвестный пользователь'}
                            </h4>
                          </div>
                          <p className="text-xs text-gray-600 dark:text-gray-400">
                            {selectedChat.admin ? `Назначен: ${selectedChat.admin.name || 'Неизвестный админ'}` : 'Не назначен администратор'}
                          </p>
                          <p className="text-xs text-gray-500 dark:text-gray-500">
                            {selectedChat.user.email || 'Email не указан'}
                          </p>
                        </div>
                      </div>
                      
                      {/* Красивый выбор статуса справа */}
                      <div className="ml-4 flex-shrink-0">
                        <StatusSelector
                          status={selectedChat.status || 'OPEN'}
                          onStatusChange={(status) => updateChatStatus(selectedChat.id || 0, status)}
                          disabled={loading}
                        />
                      </div>
                    </div>
                  </div>

                  {/* Сообщения */}
                  <div className="flex-1 overflow-y-auto p-8 space-y-6 bg-gray-50 dark:bg-gray-900">
                    {loading ? (
                      <div className="flex justify-center items-center h-full">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
                      </div>
                    ) : error ? (
                      <div className="text-red-600 text-center p-8">
                        <div className="bg-red-50 dark:bg-red-900/20 p-6 rounded-xl">
                          <svg className="w-12 h-12 mx-auto mb-4 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                          </svg>
                          <p className="text-lg font-medium mb-2">Ошибка загрузки сообщений</p>
                          <p className="text-sm mb-4">{error}</p>
                          <button
                            onClick={() => loadChat(selectedChat.id || 0)}
                            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                          >
                            Попробовать снова
                          </button>
                        </div>
                      </div>
                    ) : (messages || []).length === 0 ? (
                      <div className="text-gray-500 text-center p-8">
                        <svg className="w-16 h-16 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                        </svg>
                        <p className="text-lg font-medium mb-2">Нет сообщений</p>
                        <p className="text-sm">Начните диалог с пользователем</p>
                      </div>
                    ) : (
                      (messages || []).map((message) => (
                        <MessageItem
                          key={message.id || 0}
                          message={message}
                          isOwnMessage={(message.sender_id || 0) === (user?.id || 0)}
                          formatTime={formatTime}
                        />
                      ))
                    )}
                    <div ref={messagesEndRef} />
                  </div>

                  {/* Поле ввода */}
                  <div className="p-4 border-t border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-800">
                    <div className="flex space-x-2 mb-2">
                      <MessageTemplates
                        onSelectTemplate={(template) => setNewMessage(template)}
                        disabled={loading}
                      />
                      <div className="flex-1 relative">
                        <textarea
                          value={newMessage || ''}
                          onChange={(e) => setNewMessage(e.target.value || '')}
                          onKeyPress={handleKeyPress}
                          placeholder="Введите ответ пользователю... (Shift+Enter для новой строки)"
                          className="w-full px-4 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 resize-none min-h-[40px] max-h-[120px]"
                          disabled={loading}
                          rows={1}
                          style={{ 
                            height: 'auto',
                            minHeight: '40px',
                            maxHeight: '120px'
                          }}
                          onInput={(e) => {
                            const target = e.target as HTMLTextAreaElement;
                            target.style.height = 'auto';
                            target.style.height = Math.min(target.scrollHeight, 120) + 'px';
                          }}
                        />
                      </div>
                      <button
                        onClick={sendMessage}
                        disabled={!(newMessage || '').trim() || loading}
                        className="px-4 py-2 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg hover:from-blue-600 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 font-medium shadow-md hover:shadow-lg disabled:shadow-none"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                        </svg>
                      </button>
                    </div>
                    <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                      <p>Enter для отправки, Shift+Enter для новой строки</p>
                      <p>Длина сообщения: {(newMessage || '').length}/1000</p>
                    </div>
                  </div>
                </>
              ) : (
                <div className="flex-1 flex items-center justify-center text-gray-500 dark:text-gray-400">
                  <div className="text-center">
                    <svg className="w-20 h-20 mx-auto mb-4 text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                    </svg>
                    <p className="text-xl font-medium mb-2">Выберите обращение</p>
                    <p className="text-sm">Выберите обращение из списка слева для начала работы</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Feedback;
