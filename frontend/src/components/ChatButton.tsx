import React, { useState, useEffect } from 'react';
import { chatApi } from '../services/api';
import type { ChatSummary } from '../types/chat-types';
import { useAuth } from '../contexts/AuthContext';
import ChatWidget from './ChatWidget';

const ChatButton: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const { user } = useAuth();

  useEffect(() => {
    if (user) {
      loadUnreadCount();
      // Обновляем счетчик каждые 30 секунд
      const interval = setInterval(loadUnreadCount, 30000);
      return () => clearInterval(interval);
    }
  }, [user]);

  const loadUnreadCount = async () => {
    try {
      setLoading(true);
      const summary = await chatApi.getMyChatsSummary();
      const totalUnread = summary.reduce((sum, chat) => sum + chat.unread_count, 0);
      setUnreadCount(totalUnread);
    } catch (error) {
      console.error('Ошибка загрузки счетчика непрочитанных сообщений:', error);
    } finally {
      setLoading(false);
    }
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  if (!user) {
    return null;
  }

  return (
    <>
      {/* Плавающая кнопка */}
      <button
        onClick={toggleChat}
        className="fixed bottom-6 right-6 w-14 h-14 bg-blue-600 hover:bg-blue-700 text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-300 flex items-center justify-center z-40 group"
        title="Чат с администратором"
      >
        {loading ? (
          <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
        ) : (
          <svg 
            className="w-6 h-6 transition-transform group-hover:scale-110" 
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path 
              strokeLinecap="round" 
              strokeLinejoin="round" 
              strokeWidth={2} 
              d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" 
            />
          </svg>
        )}
        
        {/* Счетчик непрочитанных сообщений */}
        {unreadCount > 0 && (
          <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full h-6 w-6 flex items-center justify-center font-bold animate-pulse">
            {unreadCount > 99 ? '99+' : unreadCount}
          </span>
        )}
      </button>

      {/* Виджет чата */}
      <ChatWidget isOpen={isOpen} onClose={() => setIsOpen(false)} />
    </>
  );
};

export default ChatButton;
