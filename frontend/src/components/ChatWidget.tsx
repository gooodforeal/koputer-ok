import React, { useState, useEffect, useRef } from 'react';
import { chatApi } from '../services/api';
import type { Chat, Message, MessageCreate } from '../types/chat-types';
import { useAuth } from '../contexts/AuthContext';

interface ChatWidgetProps {
  isOpen: boolean;
  onClose: () => void;
}

const ChatWidget: React.FC<ChatWidgetProps> = ({ isOpen, onClose }) => {
  const [chat, setChat] = useState<Chat | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { user } = useAuth();

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    if (isOpen) {
      loadChat();
    }
  }, [isOpen]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadChat = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Пытаемся получить существующий чат
      let chatData: Chat;
      try {
        chatData = await chatApi.getMyChat();
        console.log('My chat data:', chatData);
      } catch (error: any) {
        if (error.response?.status === 404) {
          // Если чата нет, создаем новый
          chatData = await chatApi.createChat({ user_id: user?.id || 0 });
          console.log('Created new chat:', chatData);
        } else {
          throw error;
        }
      }
      
      setChat(chatData);
      
      // Фильтруем сообщения с корректными датами
      const validMessages = (chatData.messages || []).filter(msg => {
        if (!msg.created_at) {
          console.warn('Message without created_at:', msg);
          return false;
        }
        const date = new Date(msg.created_at);
        if (isNaN(date.getTime())) {
          console.warn('Message with invalid date:', msg);
          return false;
        }
        return true;
      });
      
      setMessages(validMessages);
      console.log('Messages loaded:', validMessages);
      
      // Отмечаем сообщения как прочитанные
      if (chatData.id) {
        await chatApi.markAsRead(chatData.id);
      }
    } catch (error: any) {
      console.error('Error loading chat:', error);
      setError('Ошибка загрузки чата: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!newMessage.trim() || !chat) return;

    const messageData: MessageCreate = {
      content: newMessage.trim(),
      message_type: 'text'
    };

    try {
      const response = await chatApi.sendMessage(chat.id, messageData);
      const sentMessage = response.data;
      
      // Проверяем, что сообщение имеет корректную дату
      if (sentMessage && sentMessage.created_at) {
        setMessages(prev => [...prev, sentMessage]);
        setNewMessage('');
      } else {
        console.error('Invalid message data received:', sentMessage);
        setError('Ошибка: получены некорректные данные сообщения');
      }
    } catch (error: any) {
      console.error('Error sending message:', error);
      setError('Ошибка отправки сообщения: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
    // Shift + Enter позволяет переходить на новую строку
  };

  const formatTime = (dateString: string) => {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    if (isNaN(date.getTime())) {
      console.warn('Invalid date string:', dateString);
      return '';
    }
    
    return date.toLocaleTimeString('ru-RU', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed bottom-4 right-4 w-96 h-96 bg-white rounded-lg shadow-2xl border border-gray-200 flex flex-col z-50">
      {/* Header */}
      <div className="bg-blue-600 text-white p-4 rounded-t-lg flex justify-between items-center">
        <div>
          <h3 className="font-semibold">Чат с администратором</h3>
          <p className="text-sm text-blue-100">
            {chat?.admin_id ? 'Подключен администратор' : 'Ожидание администратора'}
          </p>
        </div>
        <button
          onClick={onClose}
          className="text-white hover:text-gray-200 transition-colors"
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {loading ? (
          <div className="flex justify-center items-center h-full">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        ) : error ? (
          <div className="text-red-600 text-center p-4">
            {error}
            <button
              onClick={loadChat}
              className="block mt-2 text-blue-600 hover:text-blue-800 underline"
            >
              Попробовать снова
            </button>
          </div>
        ) : messages.length === 0 ? (
          <div className="text-gray-500 text-center p-4">
            Начните диалог с администратором
          </div>
        ) : (
          messages.map((message) => {
            // Проверяем, является ли сообщение системным
            const isSystemMessage = message.message_type === 'system';
            
            if (isSystemMessage) {
              // Системное сообщение - отображается по центру
              return (
                <div key={message.id} className="flex justify-center my-3">
                  <div className="bg-blue-50 dark:bg-blue-900 text-blue-800 dark:text-blue-100 px-4 py-2 rounded-full text-sm border border-blue-200 dark:border-blue-700 max-w-xs text-center">
                    {message.content}
                  </div>
                </div>
              );
            }
            
            // Обычное сообщение пользователя/администратора
            return (
              <div
                key={message.id}
                className={`flex ${message.sender_id === user?.id ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs px-3 py-2 rounded-lg ${
                    message.sender_id === user?.id
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-800'
                  }`}
                >
                  <p className="text-sm break-words overflow-wrap-anywhere whitespace-pre-wrap">{message.content}</p>
                  <p className={`text-xs mt-1 ${
                    message.sender_id === user?.id ? 'text-blue-100' : 'text-gray-500'
                  }`}>
                    {formatTime(message.created_at)}
                  </p>
                </div>
              </div>
            );
          })
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex space-x-2">
          <textarea
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Введите сообщение... (Shift+Enter для новой строки)"
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none min-h-[40px] max-h-[120px]"
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
          <button
            onClick={sendMessage}
            disabled={!newMessage.trim() || loading}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors self-end"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
            </svg>
          </button>
        </div>
        <div className="text-xs text-gray-500 mt-1">
          Enter для отправки, Shift+Enter для новой строки
        </div>
      </div>
    </div>
  );
};

export default ChatWidget;
