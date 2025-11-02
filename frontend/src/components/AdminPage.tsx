import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import UserManagement from './UserManagement';
import { UserRole } from '../types/user';
import { componentsApi } from '../services/api';

// Функция для перевода категорий компонентов на русский язык
const getCategoryName = (categoryKey: string): string => {
  const categoryNames: Record<string, string> = {
    PROCESSORY: 'Процессоры',
    MATERINSKIE_PLATY: 'Материнские платы',
    VIDEOKARTY: 'Видеокарты',
    OPERATIVNAYA_PAMYAT: 'Оперативная память',
    KORPUSA: 'Корпуса',
    BLOKI_PITANIYA: 'Блоки питания',
    ZHESTKIE_DISKI: 'Жесткие диски',
    OHLAZHDENIE: 'Охлаждение',
    SSD_NAKOPITELI: 'SSD накопители',
  };
  return categoryNames[categoryKey] || categoryKey;
};

const AdminPage: React.FC = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'support' | 'users' | 'components'>('support');
  
  // Состояние для парсинга компонентов
  const [parseStatus, setParseStatus] = useState<{
    is_running: boolean;
    current_category: string | null;
    processed_categories: number;
    total_categories: number;
    processed_products: number;
    errors: string[];
  } | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [componentStats, setComponentStats] = useState<{
    total: number;
    by_category: Record<string, number>;
  } | null>(null);
  
  // Обновление статуса парсинга
  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const status = await componentsApi.getParseStatus();
        setParseStatus(status);
        
        if (!status.is_running) {
          // Если парсинг не запущен, получаем статистику
          try {
            const stats = await componentsApi.getComponentStats();
            setComponentStats(stats);
          } catch (error) {
            console.error('Ошибка при получении статистики:', error);
          }
        }
      } catch (error) {
        console.error('Ошибка при получении статуса:', error);
        // Если ошибка при получении статуса, сбрасываем статус загрузки
        setParseStatus(prev => prev ? { ...prev, is_running: false } : null);
      }
    };
    
    fetchStatus();
    
    // Обновляем статус каждые 2 секунды, если парсинг запущен
    // Если парсинг завис, backend автоматически сбросит статус через 30 минут
    const interval = setInterval(() => {
      fetchStatus();
    }, 2000);
    
    return () => clearInterval(interval);
  }, []); // Убираем зависимость от parseStatus?.is_running, чтобы интервал работал всегда
  
  // Запуск парсинга
  const handleStartParsing = async (clearExisting: boolean = true) => {
    if (parseStatus?.is_running) {
      alert('Парсинг уже запущен');
      return;
    }
    
    setIsLoading(true);
    try {
      await componentsApi.startParsing(clearExisting);
      // Обновляем статус после запуска
      const status = await componentsApi.getParseStatus();
      setParseStatus(status);
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Ошибка при запуске парсинга');
    } finally {
      setIsLoading(false);
    }
  };

  // Остановка парсинга
  const handleStopParsing = async () => {
    if (!parseStatus?.is_running) {
      alert('Парсинг не запущен');
      return;
    }

    if (!confirm('Вы уверены, что хотите остановить парсинг? Текущая категория будет завершена, после чего парсинг остановится.')) {
      return;
    }

    setIsLoading(true);
    try {
      await componentsApi.stopParsing();
      // Небольшая задержка для обновления статуса на сервере
      await new Promise(resolve => setTimeout(resolve, 500));
      // Обновляем статус после остановки - делаем несколько попыток
      let attempts = 0;
      let status = await componentsApi.getParseStatus();
      while (status.is_running && attempts < 5) {
        await new Promise(resolve => setTimeout(resolve, 500));
        status = await componentsApi.getParseStatus();
        attempts++;
      }
      setParseStatus(status);
      
      if (status.is_running) {
        // Если статус все еще показывает запущенным, принудительно обновляем
        console.warn('Статус парсинга все еще показывает запущенным после остановки');
        setParseStatus({ ...status, is_running: false });
      }
    } catch (error: any) {
      console.error('Ошибка при остановке парсинга:', error);
      alert(error.response?.data?.detail || 'Ошибка при остановке парсинга');
      // В случае ошибки все равно пытаемся обновить статус
      try {
        const status = await componentsApi.getParseStatus();
        setParseStatus(status);
      } catch (e) {
        console.error('Не удалось получить статус после ошибки:', e);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const isAdmin = user?.role === UserRole.ADMIN || user?.role === UserRole.SUPER_ADMIN;

  if (!isAdmin) {
    return (
      <div className="theme-transition min-h-screen bg-gray-50 dark:bg-gray-900 py-8 px-4">
        <div className="theme-transition max-w-4xl mx-auto bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
          <div className="text-center">
            <div className="text-red-500 mb-4">
              <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
              </svg>
            </div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
              Доступ запрещен
            </h1>
            <p className="text-gray-600 dark:text-gray-300">
              У вас нет прав для доступа к этой странице.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="theme-transition min-h-screen bg-gray-50 dark:bg-gray-900 py-8 px-4">
      <div className="theme-transition max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-purple-600 to-blue-600 text-white p-6 rounded-2xl mb-6 shadow-lg">
          <div>
            <h1 className="text-3xl font-bold mb-2">Администрирование</h1>
            <p className="text-purple-100">
              Панель управления системой для администраторов
            </p>
          </div>
        </div>

        {/* Вкладки */}
        <div className="mb-8">
          <div className="border-b border-gray-200 dark:border-gray-700">
            <nav className="-mb-px flex space-x-8">
              <button
                onClick={() => setActiveTab('support')}
                className={`py-2 px-1 border-b-2 font-medium text-sm transition-colors duration-200 ${
                  activeTab === 'support'
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
                }`}
              >
                <span className="flex items-center gap-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                  </svg>
                  Управление обращениями
                </span>
              </button>
              <button
                onClick={() => setActiveTab('components')}
                className={`py-2 px-1 border-b-2 font-medium text-sm transition-colors duration-200 ${
                  activeTab === 'components'
                    ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                    : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
                }`}
              >
                <span className="flex items-center gap-2">
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                  </svg>
                  База компонентов
                </span>
              </button>
              {user?.role === UserRole.SUPER_ADMIN && (
                <button
                  onClick={() => setActiveTab('users')}
                  className={`py-2 px-1 border-b-2 font-medium text-sm transition-colors duration-200 ${
                    activeTab === 'users'
                      ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                      : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
                  }`}
                >
                  <span className="flex items-center gap-2">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
                    </svg>
                    Управление пользователями
                  </span>
                </button>
              )}
            </nav>
          </div>
        </div>

        {/* Содержимое вкладок */}
        {activeTab === 'support' && (
          <div className="theme-transition bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-200 dark:border-gray-700">
            <div className="flex items-center justify-between mb-6">
              <div>
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Управление обращениями
                </h2>
                <p className="text-gray-600 dark:text-gray-300 mt-1">
                  Просмотр и ответ на обращения пользователей
                </p>
              </div>
              <button
                onClick={() => navigate('/admin/feedback')}
                className="bg-blue-600 dark:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 dark:hover:bg-blue-800 transition-colors duration-200 flex items-center gap-2"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                Перейти к обращениям
              </button>
            </div>
            
            <div className="text-center py-12">
              <div className="text-gray-400 mb-4">
                <svg className="w-16 h-16 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                Система обращений
              </h3>
              <p className="text-gray-600 dark:text-gray-300 mb-6">
                Нажмите кнопку "Перейти к обращениям" для просмотра и ответа на обращения пользователей
              </p>
            </div>
          </div>
        )}

        {activeTab === 'components' && (
          <div className="theme-transition bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-200 dark:border-gray-700">
            <div className="mb-6">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                База компонентов
              </h2>
              <p className="text-gray-600 dark:text-gray-300">
                Управление базой данных компонентов компьютера
              </p>
            </div>
            
            {/* Статистика */}
            {componentStats && (
              <div className="mb-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg">
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-3">
                  Статистика
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
                  <div className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
                    <div className="text-sm text-gray-600 dark:text-gray-400">Всего компонентов</div>
                    <div className="text-2xl font-bold text-gray-900 dark:text-white">
                      {componentStats.total}
                    </div>
                  </div>
                  {Object.entries(componentStats.by_category)
                    .filter(([, count]) => count > 0)
                    .sort(([, a], [, b]) => (b as number) - (a as number))
                    .map(([category, count]) => (
                      <div key={category} className="bg-white dark:bg-gray-800 p-4 rounded-lg shadow">
                        <div className="text-sm text-gray-600 dark:text-gray-400">{getCategoryName(category)}</div>
                        <div className="text-2xl font-bold text-gray-900 dark:text-white">
                          {count as number}
                        </div>
                      </div>
                    ))}
                </div>
              </div>
            )}
            
            {/* Управление парсингом */}
            <div className="mb-6">
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">
                Обновление базы данных
              </h3>
              
              {parseStatus?.is_running ? (
                <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-yellow-600 dark:border-yellow-400"></div>
                      <h4 className="text-lg font-semibold text-yellow-900 dark:text-yellow-200">
                        Парсинг выполняется...
                      </h4>
                    </div>
                    <button
                      onClick={handleStopParsing}
                      disabled={isLoading}
                      className="bg-red-600 dark:bg-red-700 text-white px-4 py-2 rounded-lg font-medium hover:bg-red-700 dark:hover:bg-red-800 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                      Остановить
                    </button>
                  </div>
                  
                  {parseStatus.current_category && (
                    <div className="mb-4">
                      <div className="text-sm text-yellow-800 dark:text-yellow-300 mb-2">
                        Текущая категория: <strong>{parseStatus.current_category}</strong>
                      </div>
                      <div className="w-full bg-yellow-200 dark:bg-yellow-800 rounded-full h-2">
                        <div
                          className="bg-yellow-600 dark:bg-yellow-400 h-2 rounded-full transition-all duration-300"
                          style={{
                            width: `${(parseStatus.processed_categories / parseStatus.total_categories) * 100}%`
                          }}
                        ></div>
                      </div>
                      <div className="text-xs text-yellow-700 dark:text-yellow-400 mt-1">
                        {parseStatus.processed_categories} / {parseStatus.total_categories} категорий
                      </div>
                    </div>
                  )}
                  
                  <div className="text-sm text-yellow-800 dark:text-yellow-300">
                    Обработано товаров: <strong>{parseStatus.processed_products}</strong>
                  </div>
                  
                  {parseStatus.errors.length > 0 && (
                    <div className="mt-4">
                      <div className="text-sm font-medium text-red-600 dark:text-red-400 mb-2">
                        Ошибки ({parseStatus.errors.length}):
                      </div>
                      <div className="max-h-32 overflow-y-auto bg-red-50 dark:bg-red-900/20 rounded p-2">
                        {parseStatus.errors.slice(-5).map((error, idx) => (
                          <div key={idx} className="text-xs text-red-700 dark:text-red-400 mb-1">
                            {error}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              ) : (
                <div className="bg-gray-50 dark:bg-gray-900 rounded-lg p-6">
                  <p className="text-gray-600 dark:text-gray-300 mb-4">
                    Запустите парсинг для обновления базы данных компонентов со всех категорий.
                  </p>
                  <div className="flex gap-3">
                    <button
                      onClick={() => handleStartParsing(true)}
                      disabled={isLoading}
                      className="bg-blue-600 dark:bg-blue-700 text-white px-6 py-2 rounded-lg font-medium hover:bg-blue-700 dark:hover:bg-blue-800 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                    >
                      {isLoading ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                          Запуск...
                        </>
                      ) : (
                        <>
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                          </svg>
                          Обновить базу (очистить старые данные)
                        </>
                      )}
                    </button>
                    <button
                      onClick={() => handleStartParsing(false)}
                      disabled={isLoading}
                      className="bg-green-600 dark:bg-green-700 text-white px-6 py-2 rounded-lg font-medium hover:bg-green-700 dark:hover:bg-green-800 transition-colors duration-200 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                    >
                      {isLoading ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                          Запуск...
                        </>
                      ) : (
                        <>
                          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
                          </svg>
                          Дополнить базу (сохранить старые данные)
                        </>
                      )}
                    </button>
                  </div>
                </div>
              )}
            </div>
            
            {parseStatus && !parseStatus.is_running && (
              <>
                {parseStatus.processed_products > 0 && (
                  <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4 mb-4">
                    <div className="flex items-center gap-2 text-green-800 dark:text-green-200">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span className="font-medium">
                        Парсинг завершен. Обработано товаров: {parseStatus.processed_products}
                      </span>
                    </div>
                  </div>
                )}
                
                {parseStatus.errors.length > 0 && (
                  <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-4">
                    <div className="flex items-center gap-2 text-red-800 dark:text-red-200 mb-2">
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span className="font-medium">
                        Обнаружены ошибки при парсинге ({parseStatus.errors.length})
                      </span>
                    </div>
                    <div className="max-h-48 overflow-y-auto bg-white dark:bg-gray-800 rounded p-2">
                      {parseStatus.errors.map((error, idx) => (
                        <div key={idx} className="text-sm text-red-700 dark:text-red-400 mb-2 p-2 bg-red-50 dark:bg-red-900/30 rounded">
                          {error}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        )}

        {activeTab === 'users' && user && user.role === UserRole.SUPER_ADMIN && (
          <UserManagement currentUser={user} />
        )}
      </div>
    </div>
  );
};

export default AdminPage;
