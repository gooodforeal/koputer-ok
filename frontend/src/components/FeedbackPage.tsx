import React, { useState, useEffect } from 'react';
import { feedbackApi } from '../services/api';
import type {
  FeedbackType, 
  FeedbackStatus, 
  Feedback, 
  FeedbackCreate, 
  FeedbackAdminUpdate, 
  FeedbackStats 
} from '../types/feedback';
import { FeedbackTypeValues, FeedbackStatusValues } from '../types/feedback';
import { useAuth } from '../contexts/AuthContext';
import { UserRole } from '../types/user';

const FeedbackPage: React.FC = () => {
  const [feedbacks, setFeedbacks] = useState<Feedback[]>([]);
  const [myFeedbacks, setMyFeedbacks] = useState<Feedback[]>([]);
  const [stats, setStats] = useState<FeedbackStats | null>(null);
  const [selectedFeedback, setSelectedFeedback] = useState<Feedback | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [activeTab, setActiveTab] = useState<'my' | 'all' | 'assigned'>('all');
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [itemsPerPage] = useState(12);
  const [totalItems, setTotalItems] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  
  // Sort state
  const [sortOrder, setSortOrder] = useState<'newest' | 'oldest'>('newest');
  
  const { user } = useAuth();
  const isAdmin = user?.role === UserRole.ADMIN || user?.role === UserRole.SUPER_ADMIN;
  const isAuthenticated = !!user;

  // Форма создания отзыва
  const [formData, setFormData] = useState<FeedbackCreate>({
    title: '',
    description: '',
    type: FeedbackTypeValues.GENERAL,
    rating: undefined
  });

  // Форма обновления администратором
  const [adminFormData, setAdminFormData] = useState<FeedbackAdminUpdate>({
    status: undefined,
    admin_response: ''
  });

  useEffect(() => {
    loadData();
  }, [activeTab, currentPage, sortOrder]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      // Очищаем старые данные при загрузке новой страницы
      setFeedbacks([]);
      setMyFeedbacks([]);

      const skip = (currentPage - 1) * itemsPerPage;
      const limit = itemsPerPage;

      if (activeTab === 'my' && isAuthenticated) {
        const response = await feedbackApi.getMyFeedbacks(skip, limit);
        setMyFeedbacks(response.feedbacks);
        setTotalItems(response.total);
        setTotalPages(response.total_pages);
      } else if (activeTab === 'all') {
        // Все пользователи видят все отзывы (авторизованные и нет)
        if (isAuthenticated) {
          const response = await feedbackApi.getAllFeedbacks(skip, limit);
          setFeedbacks(response.feedbacks);
          setTotalItems(response.total);
          setTotalPages(response.total_pages);
          if (isAdmin) {
            const statsData = await feedbackApi.getFeedbackStats();
            setStats(statsData);
          }
        } else {
          // Загружаем все публичные отзывы для неавторизованных пользователей
          const response = await feedbackApi.getPublicFeedbacks(skip, limit);
          setFeedbacks(response.feedbacks);
          setTotalItems(response.total);
          setTotalPages(response.total_pages);
        }
      } else if (activeTab === 'assigned' && isAdmin) {
        const response = await feedbackApi.getAssignedFeedbacks(skip, limit);
        setFeedbacks(response.feedbacks);
        setTotalItems(response.total);
        setTotalPages(response.total_pages);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка загрузки данных');
      setFeedbacks([]);
      setMyFeedbacks([]);
      setTotalItems(0);
      setTotalPages(0);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateFeedback = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!isAuthenticated) {
      setError('Для создания отзыва необходимо авторизоваться');
      return;
    }
    
    try {
      setLoading(true);
      setError(null);
      await feedbackApi.createFeedback(formData);
      setShowCreateForm(false);
      setFormData({
        title: '',
        description: '',
        type: FeedbackTypeValues.GENERAL,
        rating: undefined
      });
      // Переключаемся на "Мои отзывы" и сбрасываем страницу
      setActiveTab('my');
      setCurrentPage(1);
      await loadData(); // Обновляем данные
    } catch (err: any) {
      const errorMessage = err.response?.data?.detail || 'Ошибка создания отзыва';
      setError(errorMessage);
      
      // Если ошибка связана с существующим отзывом, закрываем форму и переключаемся на "Мои отзывы"
      if (errorMessage.includes('уже оставили отзыв')) {
        setShowCreateForm(false);
        setActiveTab('my');
        setCurrentPage(1);
      }
    } finally {
      setLoading(false);
    }
  };
  
  const handleCreateButtonClick = async () => {
    if (!isAuthenticated) {
      setError('Для создания отзыва необходимо авторизоваться. Перейдите на страницу входа.');
      setTimeout(() => {
        window.location.href = '/login';
      }, 2000);
      return;
    }
    
      // Проверяем, есть ли уже отзыв от этого пользователя
    try {
      const response = await feedbackApi.getMyFeedbacks(0, 1);
      if (response.feedbacks.length > 0) {
        setError('Вы уже оставили отзыв. Вы можете просмотреть его во вкладке "Мои отзывы".');
        // Переключаемся на вкладку "Мои отзывы"
        setActiveTab('my');
        setCurrentPage(1);
        return;
      }
    } catch (err: any) {
      // Если ошибка при проверке, можно продолжить (возможно, отзывов еще нет)
      console.error('Ошибка проверки отзывов:', err);
    }
    
    setShowCreateForm(true);
  };

  const handleAdminUpdate = async (feedbackId: number) => {
    try {
      setLoading(true);
      setError(null);
      await feedbackApi.adminUpdateFeedback(feedbackId, adminFormData);
      setSelectedFeedback(null);
      setAdminFormData({ status: undefined, admin_response: '' });
      loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка обновления отзыва');
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteFeedback = async (feedbackId: number) => {
    if (!confirm('Вы уверены, что хотите удалить этот отзыв?')) return;
    
    try {
      setLoading(true);
      setError(null);
      await feedbackApi.deleteFeedback(feedbackId);
      setSelectedFeedback(null);
      loadData();
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка удаления отзыва');
    } finally {
      setLoading(false);
    }
  };

  const getFeedbackTypeLabel = (type: FeedbackType): string => {
    const labels: Record<string, string> = {
      'BUG': 'Ошибка',
      'FEATURE': 'Новая функция',
      'IMPROVEMENT': 'Улучшение',
      'GENERAL': 'Общий отзыв'
    };
    return labels[type] || type;
  };

  const getFeedbackStatusLabel = (status: FeedbackStatus): string => {
    const labels: Record<string, string> = {
      'NEW': 'Новый',
      'IN_REVIEW': 'На рассмотрении',
      'IN_PROGRESS': 'В работе',
      'RESOLVED': 'Решено',
      'REJECTED': 'Отклонено'
    };
    return labels[status] || status;
  };

  const getStatusColor = (status: FeedbackStatus): string => {
    const colors: Record<string, string> = {
      'NEW': 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
      'IN_REVIEW': 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300',
      'IN_PROGRESS': 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300',
      'RESOLVED': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
      'REJECTED': 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
    };
    return colors[status] || '';
  };

  const getTypeColor = (type: FeedbackType): string => {
    const colors: Record<string, string> = {
      'BUG': 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
      'FEATURE': 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
      'IMPROVEMENT': 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
      'GENERAL': 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
    };
    return colors[type] || '';
  };

  // Сортировка отзывов
  const sortFeedbacks = (feedbackList: Feedback[]) => {
    return [...feedbackList].sort((a, b) => {
      const dateA = new Date(a.created_at).getTime();
      const dateB = new Date(b.created_at).getTime();
      return sortOrder === 'newest' ? dateB - dateA : dateA - dateB;
    });
  };

  const displayFeedbacks = sortFeedbacks(activeTab === 'my' ? myFeedbacks : feedbacks);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8 px-4 transition-colors">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-6 rounded-2xl mb-6 shadow-lg">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold mb-2">Система отзывов</h1>
              <p className="text-purple-100">
                {isAuthenticated 
                  ? 'Ваше мнение помогает нам становиться лучше' 
                  : 'Посмотрите, что говорят наши пользователи'}
              </p>
            </div>
            <button
              onClick={handleCreateButtonClick}
              className="px-6 py-3 bg-white text-purple-600 rounded-lg hover:bg-purple-50 transition-colors font-medium shadow-md"
            >
              + Оставить отзыв
            </button>
          </div>
        </div>

        {/* Statistics (only for admins) */}
        {isAdmin && stats && activeTab === 'all' && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Всего отзывов</p>
                  <p className="text-3xl font-bold text-gray-900 dark:text-white">{stats.total}</p>
                </div>
                <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                  <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
                  </svg>
                </div>
              </div>
            </div>
            
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Новых</p>
                  <p className="text-3xl font-bold text-blue-600">{stats.new}</p>
                </div>
                <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                  <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                  </svg>
                </div>
              </div>
            </div>
            
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">В работе</p>
                  <p className="text-3xl font-bold text-yellow-600">{stats.in_progress}</p>
                </div>
                <div className="w-12 h-12 bg-yellow-100 dark:bg-yellow-900/30 rounded-lg flex items-center justify-center">
                  <svg className="w-6 h-6 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
            </div>
            
            <div className="bg-white dark:bg-gray-800 p-6 rounded-lg shadow border border-gray-200 dark:border-gray-700">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Решено</p>
                  <p className="text-3xl font-bold text-green-600">{stats.resolved}</p>
                </div>
                <div className="w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-lg flex items-center justify-center">
                  <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Tabs */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow mb-6 border border-gray-200 dark:border-gray-700">
          <div className="flex justify-between items-center border-b border-gray-200 dark:border-gray-700">
            <div className="flex">
              <button
                onClick={() => {
                  setActiveTab('all');
                  setCurrentPage(1);
                }}
                className={`px-6 py-3 font-medium transition-colors ${
                  activeTab === 'all'
                    ? 'border-b-2 border-purple-600 text-purple-600 dark:text-purple-400'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                Все отзывы
              </button>
              {isAuthenticated && (
                <button
                  onClick={() => {
                    setActiveTab('my');
                    setCurrentPage(1);
                  }}
                  className={`px-6 py-3 font-medium transition-colors ${
                    activeTab === 'my'
                      ? 'border-b-2 border-purple-600 text-purple-600 dark:text-purple-400'
                      : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                  }`}
                >
                  Мои отзывы
                </button>
              )}
              {isAdmin && (
                <button
                  onClick={() => {
                    setActiveTab('assigned');
                    setCurrentPage(1);
                  }}
                  className={`px-6 py-3 font-medium transition-colors ${
                    activeTab === 'assigned'
                      ? 'border-b-2 border-purple-600 text-purple-600 dark:text-purple-400'
                      : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                  }`}
                >
                  Назначенные мне
                </button>
              )}
            </div>
            
            {/* Sort Button */}
            <div className="px-6 py-3 flex items-center gap-2">
              <span className="text-sm text-gray-600 dark:text-gray-400">Сортировка:</span>
              <button
                onClick={() => {
                  setSortOrder(sortOrder === 'newest' ? 'oldest' : 'newest');
                  setCurrentPage(1); // Сбрасываем на первую страницу при изменении сортировки
                }}
                className="flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  {sortOrder === 'newest' ? (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12" />
                  ) : (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4h13M3 8h9m-9 4h9m5-4v12m0 0l-4-4m4 4l4-4" />
                  )}
                </svg>
                <span className="text-sm font-medium">
                  {sortOrder === 'newest' ? 'Сначала новые' : 'Сначала старые'}
                </span>
              </button>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-800 dark:text-red-200 px-6 py-4 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Feedbacks List */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {loading ? (
            <div className="col-span-full flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
            </div>
          ) : displayFeedbacks.length === 0 ? (
            <div className="col-span-full text-center py-12">
              <svg className="w-16 h-16 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
              </svg>
              <p className="text-gray-600 dark:text-gray-400 text-lg">Отзывов пока нет</p>
            </div>
          ) : (
            displayFeedbacks.map((feedback) => (
              <div
                key={feedback.id}
                className="bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-6 hover:shadow-xl transition-shadow cursor-pointer"
                onClick={() => setSelectedFeedback(feedback)}
              >
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white break-words overflow-hidden pr-2 flex-1">{feedback.title}</h3>
                  <div className="flex gap-2 flex-shrink-0">
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getTypeColor(feedback.type)}`}>
                      {getFeedbackTypeLabel(feedback.type)}
                    </span>
                    <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(feedback.status)}`}>
                      {getFeedbackStatusLabel(feedback.status)}
                    </span>
                  </div>
                </div>
                
                <p className="text-gray-600 dark:text-gray-400 mb-4 line-clamp-3 break-words whitespace-pre-wrap overflow-hidden">{feedback.description}</p>
                
                <div className="flex items-center justify-between text-sm">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-white font-semibold">
                      {feedback.user.name.charAt(0).toUpperCase()}
                    </div>
                    <span className="text-gray-700 dark:text-gray-300">{feedback.user.name}</span>
                  </div>
                  
                  {feedback.rating && (
                    <div className="flex items-center gap-1">
                      {[...Array(5)].map((_, i) => (
                        <svg
                          key={i}
                          className={`w-5 h-5 ${i < feedback.rating! ? 'text-yellow-400' : 'text-gray-300 dark:text-gray-600'}`}
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                        </svg>
                      ))}
                    </div>
                  )}
                </div>
                
                <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    {new Date(feedback.created_at).toLocaleString('ru-RU')}
                  </p>
                </div>
              </div>
            ))
          )}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="mt-8 flex flex-col sm:flex-row justify-center items-center gap-4">
            {/* Информация о странице */}
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Страница <span className="font-semibold text-gray-900 dark:text-white">{currentPage}</span> из <span className="font-semibold text-gray-900 dark:text-white">{totalPages}</span>
              <span className="ml-2 text-gray-500 dark:text-gray-500">
                ({totalItems} отзывов)
              </span>
            </div>

            {/* Навигация */}
            <div className="flex items-center gap-1">
              {/* Кнопка "В начало" */}
              <button
                onClick={() => {
                  handlePageChange(1);
                }}
                disabled={currentPage === 1}
                className="px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                title="В начало"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
                </svg>
              </button>

              {/* Кнопка "Предыдущая" */}
              <button
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1}
                className="px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                title="Предыдущая страница"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>

              {/* Номера страниц */}
              <div className="flex items-center gap-1 flex-wrap justify-center">
                {(() => {
                  const pages: (number | string)[] = [];
                  const maxVisible = 7;
                  
                  if (totalPages <= maxVisible) {
                    // Показываем все страницы, если их немного
                    for (let i = 1; i <= totalPages; i++) {
                      pages.push(i);
                    }
                  } else {
                    // Всегда показываем первую страницу
                    pages.push(1);
                    
                    if (currentPage <= 4) {
                      // Близко к началу: показываем первые страницы
                      for (let i = 2; i <= 5; i++) {
                        pages.push(i);
                      }
                      pages.push('...');
                      pages.push(totalPages);
                    } else if (currentPage >= totalPages - 3) {
                      // Близко к концу: показываем последние страницы
                      pages.push('...');
                      for (let i = totalPages - 4; i <= totalPages; i++) {
                        pages.push(i);
                      }
                    } else {
                      // В середине: показываем текущую и соседние
                      pages.push('...');
                      for (let i = currentPage - 1; i <= currentPage + 1; i++) {
                        pages.push(i);
                      }
                      pages.push('...');
                      pages.push(totalPages);
                    }
                  }
                  
                  return pages.map((item, index) => {
                    if (item === '...') {
                      return (
                        <span key={`ellipsis-${index}`} className="px-2 text-gray-500 dark:text-gray-400">
                          ...
                        </span>
                      );
                    }
                    
                    const pageNumber = item as number;
                    return (
                      <button
                        key={pageNumber}
                        onClick={() => handlePageChange(pageNumber)}
                        className={`min-w-[2.5rem] px-3 py-2 rounded-lg font-medium transition-colors ${
                          currentPage === pageNumber
                            ? 'bg-purple-600 text-white shadow-md hover:bg-purple-700'
                            : 'bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                        }`}
                      >
                        {pageNumber}
                      </button>
                    );
                  });
                })()}
              </div>

              {/* Кнопка "Следующая" */}
              <button
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
                className="px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                title="Следующая страница"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </button>

              {/* Кнопка "В конец" */}
              <button
                onClick={() => {
                  handlePageChange(totalPages);
                }}
                disabled={currentPage === totalPages}
                className="px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                title="В конец"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
                </svg>
              </button>
            </div>
          </div>
        )}

        {/* Create Feedback Modal */}
        {showCreateForm && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-2xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white">Новый отзыв</h2>
              </div>
              
              <form onSubmit={handleCreateFeedback} className="p-6 space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Заголовок *
                  </label>
                  <input
                    type="text"
                    value={formData.title}
                    onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white break-words"
                    required
                    minLength={3}
                    maxLength={200}
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Описание *
                  </label>
                  <textarea
                    value={formData.description}
                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white break-words resize-y"
                    rows={4}
                    required
                    minLength={10}
                    maxLength={2000}
                  />
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Тип отзыва *
                  </label>
                  <select
                    value={formData.type}
                    onChange={(e) => setFormData({ ...formData, type: e.target.value as FeedbackType })}
                    className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                  >
                    {Object.values(FeedbackTypeValues).map((type) => (
                      <option key={type} value={type}>
                        {getFeedbackTypeLabel(type)}
                      </option>
                    ))}
                  </select>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Оценка (необязательно)
                  </label>
                  <div className="flex gap-2">
                    {[1, 2, 3, 4, 5].map((rating) => (
                      <button
                        key={rating}
                        type="button"
                        onClick={() => setFormData({ ...formData, rating })}
                        className="focus:outline-none"
                      >
                        <svg
                          className={`w-8 h-8 ${formData.rating && rating <= formData.rating ? 'text-yellow-400' : 'text-gray-300 dark:text-gray-600'}`}
                          fill="currentColor"
                          viewBox="0 0 20 20"
                        >
                          <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                        </svg>
                      </button>
                    ))}
                  </div>
                </div>
                
                <div className="flex justify-end gap-4 pt-4">
                  <button
                    type="button"
                    onClick={() => setShowCreateForm(false)}
                    className="px-6 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors text-gray-700 dark:text-gray-300"
                    disabled={loading}
                  >
                    Отмена
                  </button>
                  <button
                    type="submit"
                    className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50"
                    disabled={loading}
                  >
                    Отправить
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* View/Edit Feedback Modal */}
        {selectedFeedback && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl max-w-3xl w-full max-h-[90vh] overflow-y-auto">
              <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                <div className="flex justify-between items-start">
                  <div className="flex-1 overflow-hidden">
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2 break-words overflow-wrap-anywhere">
                      {selectedFeedback.title}
                    </h2>
                    <div className="flex gap-2 flex-wrap">
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getTypeColor(selectedFeedback.type)}`}>
                        {getFeedbackTypeLabel(selectedFeedback.type)}
                      </span>
                      <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(selectedFeedback.status)}`}>
                        {getFeedbackStatusLabel(selectedFeedback.status)}
                      </span>
                    </div>
                  </div>
                  <button
                    onClick={() => setSelectedFeedback(null)}
                    className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>
              </div>
              
              <div className="p-6 space-y-6">
                <div>
                  <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Описание</h3>
                  <p className="text-gray-900 dark:text-white whitespace-pre-wrap break-words overflow-wrap-anywhere">{selectedFeedback.description}</p>
                </div>
                
                <div className="flex items-center gap-4">
                  <div>
                    <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Автор</h3>
                    <div className="flex items-center gap-2">
                      <div className="w-10 h-10 bg-gradient-to-r from-purple-500 to-blue-500 rounded-full flex items-center justify-center text-white font-semibold">
                        {selectedFeedback.user.name.charAt(0).toUpperCase()}
                      </div>
                      <div>
                        <p className="text-gray-900 dark:text-white font-medium">{selectedFeedback.user.name}</p>
                        <p className="text-sm text-gray-600 dark:text-gray-400">{selectedFeedback.user.email}</p>
                      </div>
                    </div>
                  </div>
                  
                  {selectedFeedback.rating && (
                    <div>
                      <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Оценка</h3>
                      <div className="flex gap-1">
                        {[...Array(5)].map((_, i) => (
                          <svg
                            key={i}
                            className={`w-5 h-5 ${i < selectedFeedback.rating! ? 'text-yellow-400' : 'text-gray-300 dark:text-gray-600'}`}
                            fill="currentColor"
                            viewBox="0 0 20 20"
                          >
                            <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                          </svg>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
                
                {selectedFeedback.admin_response && (
                  <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
                    <h3 className="text-sm font-medium text-blue-900 dark:text-blue-300 mb-2">Ответ администратора</h3>
                    <p className="text-blue-800 dark:text-blue-200 whitespace-pre-wrap break-words overflow-wrap-anywhere">{selectedFeedback.admin_response}</p>
                  </div>
                )}
                
                {/* Admin controls */}
                {isAdmin && (
                  <div className="border-t border-gray-200 dark:border-gray-700 pt-6 space-y-4">
                    <h3 className="text-lg font-bold text-gray-900 dark:text-white">Управление администратора</h3>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Статус
                      </label>
                      <select
                        value={adminFormData.status || selectedFeedback.status}
                        onChange={(e) => setAdminFormData({ ...adminFormData, status: e.target.value as FeedbackStatus })}
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      >
                        {Object.values(FeedbackStatusValues).map((status) => (
                          <option key={status} value={status}>
                            {getFeedbackStatusLabel(status)}
                          </option>
                        ))}
                      </select>
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Ответ
                      </label>
                      <textarea
                        value={adminFormData.admin_response || selectedFeedback.admin_response || ''}
                        onChange={(e) => setAdminFormData({ ...adminFormData, admin_response: e.target.value })}
                        className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white break-words resize-y"
                        rows={4}
                        placeholder="Введите ответ пользователю..."
                        maxLength={2000}
                      />
                    </div>
                    
                    <div className="flex justify-between">
                      <button
                        onClick={() => handleDeleteFeedback(selectedFeedback.id)}
                        className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50"
                        disabled={loading}
                      >
                        Удалить
                      </button>
                      <button
                        onClick={() => handleAdminUpdate(selectedFeedback.id)}
                        className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors disabled:opacity-50"
                        disabled={loading}
                      >
                        Сохранить изменения
                      </button>
                    </div>
                  </div>
                )}
                
                {/* User can delete their own feedback */}
                {!isAdmin && selectedFeedback.user_id === user?.id && 
                  selectedFeedback.status !== FeedbackStatusValues.RESOLVED && 
                  selectedFeedback.status !== FeedbackStatusValues.REJECTED && (
                  <div className="flex justify-end">
                    <button
                      onClick={() => handleDeleteFeedback(selectedFeedback.id)}
                      className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors disabled:opacity-50"
                      disabled={loading}
                    >
                      Удалить отзыв
                    </button>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default FeedbackPage;

