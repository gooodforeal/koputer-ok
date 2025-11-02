import React from 'react';
import type { ChatStatus } from '../types/chat-types';

interface AdminQuickActionsProps {
  chatId: number;
  status: ChatStatus;
  adminName?: string;
  onStatusChange: (chatId: number, status: ChatStatus) => void;
  onAssignToMe: (chatId: number) => void;
  onStartWorking: (chatId: number) => void;
  onClose: (chatId: number) => void;
  onReopen: (chatId: number) => void;
  isLoading?: boolean;
}

const AdminQuickActions: React.FC<AdminQuickActionsProps> = ({
  chatId,
  status,
  adminName,
  onStatusChange,
  onAssignToMe,
  onStartWorking,
  onClose,
  onReopen,
  isLoading = false
}) => {
  const getStatusIcon = (status: ChatStatus) => {
    switch (status) {
      case 'OPEN':
        return (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        );
      case 'IN_PROGRESS':
        return (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      case 'CLOSED':
        return (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        );
      default:
        return null;
    }
  };

  const getStatusColor = (status: ChatStatus) => {
    switch (status) {
      case 'OPEN':
        return 'from-red-500 to-pink-500 hover:from-red-600 hover:to-pink-600';
      case 'IN_PROGRESS':
        return 'from-yellow-500 to-orange-500 hover:from-yellow-600 hover:to-orange-600';
      case 'CLOSED':
        return 'from-green-500 to-emerald-500 hover:from-green-600 hover:to-emerald-600';
      default:
        return 'from-gray-500 to-gray-600 hover:from-gray-600 hover:to-gray-700';
    }
  };

  const getStatusLabel = (status: ChatStatus) => {
    switch (status) {
      case 'OPEN':
        return 'Открыт';
      case 'IN_PROGRESS':
        return 'В работе';
      case 'CLOSED':
        return 'Закрыт';
      default:
        return 'Неизвестно';
    }
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-6">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className={`w-10 h-10 rounded-full bg-gradient-to-r ${getStatusColor(status)} flex items-center justify-center text-white`}>
            {getStatusIcon(status)}
          </div>
          <div>
            <h3 className="font-semibold text-gray-900 dark:text-white">
              Статус: {getStatusLabel(status)}
            </h3>
            {adminName && (
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Администратор: {adminName}
              </p>
            )}
          </div>
        </div>
        <div className="text-right">
          <p className="text-xs text-gray-500 dark:text-gray-400">ID: #{chatId}</p>
        </div>
      </div>

      <div className="space-y-3">
        {status === 'OPEN' && !adminName && (
          <button
            onClick={() => onAssignToMe(chatId)}
            disabled={isLoading}
            className="w-full px-4 py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-lg hover:from-blue-600 hover:to-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 font-medium shadow-md hover:shadow-lg disabled:shadow-none flex items-center justify-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            Назначить себе
          </button>
        )}

        {status === 'OPEN' && adminName && (
          <button
            onClick={() => onStartWorking(chatId)}
            disabled={isLoading}
            className="w-full px-4 py-3 bg-gradient-to-r from-yellow-500 to-orange-500 text-white rounded-lg hover:from-yellow-600 hover:to-orange-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 font-medium shadow-md hover:shadow-lg disabled:shadow-none flex items-center justify-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            Начать работу
          </button>
        )}

        {status === 'IN_PROGRESS' && (
          <button
            onClick={() => onClose(chatId)}
            disabled={isLoading}
            className="w-full px-4 py-3 bg-gradient-to-r from-red-500 to-pink-500 text-white rounded-lg hover:from-red-600 hover:to-pink-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 font-medium shadow-md hover:shadow-lg disabled:shadow-none flex items-center justify-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
            Закрыть обращение
          </button>
        )}

        {status === 'CLOSED' && (
          <button
            onClick={() => onReopen(chatId)}
            disabled={isLoading}
            className="w-full px-4 py-3 bg-gradient-to-r from-green-500 to-emerald-500 text-white rounded-lg hover:from-green-600 hover:to-emerald-600 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 font-medium shadow-md hover:shadow-lg disabled:shadow-none flex items-center justify-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
            Переоткрыть
          </button>
        )}

        {/* Дополнительные действия */}
        <div className="pt-3 border-t border-gray-200 dark:border-gray-700">
          <div className="grid grid-cols-2 gap-2">
            <button
              onClick={() => onStatusChange(chatId, 'IN_PROGRESS')}
              disabled={isLoading || status === 'IN_PROGRESS'}
              className="px-3 py-2 text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-1"
            >
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              В работу
            </button>
            <button
              onClick={() => onStatusChange(chatId, 'CLOSED')}
              disabled={isLoading || status === 'CLOSED'}
              className="px-3 py-2 text-sm bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-1"
            >
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              Закрыть
            </button>
          </div>
        </div>
      </div>

      {isLoading && (
        <div className="mt-4 flex items-center justify-center">
          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
          <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">Обработка...</span>
        </div>
      )}
    </div>
  );
};

export default AdminQuickActions;


