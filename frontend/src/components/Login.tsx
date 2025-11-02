import React, { useEffect, useState } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../services/api';

const Login: React.FC = () => {
  const [searchParams] = useSearchParams();
  const [error, setError] = useState<string | null>(null);
  const [telegramAuthToken, setTelegramAuthToken] = useState<string | null>(null);
  const [isWaitingForTelegram, setIsWaitingForTelegram] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();
  const { login } = useAuth();

  useEffect(() => {
    const errorParam = searchParams.get('error');
    if (errorParam) {
      setError(decodeURIComponent(errorParam));
    }
  }, [searchParams]);

  // Polling для проверки статуса авторизации
  useEffect(() => {
    if (!telegramAuthToken || !isWaitingForTelegram) return;

    const checkAuthStatus = async () => {
      try {
        const response = await api.get(`/auth/telegram/check/${telegramAuthToken}`);
        
        if (response.data.status === 'completed' && response.data.access_token) {
          // Авторизация завершена, получили JWT токен
          console.log('Получен JWT токен:', response.data.access_token.substring(0, 20) + '...');
          setIsWaitingForTelegram(false);
          setTelegramAuthToken(null);
          
          // Авторизуем пользователя с полученным токеном
          await login(response.data.access_token);
          
          // Небольшая задержка для гарантии что localStorage обновился
          await new Promise(resolve => setTimeout(resolve, 100));
          
          console.log('Авторизация успешна, перенаправляем на главную...');
          navigate('/');
        }
      } catch (error: any) {
        console.error('Ошибка при проверке статуса:', error);
        if (error.response?.status === 404) {
          // Токен истек
          setIsWaitingForTelegram(false);
          setTelegramAuthToken(null);
          setError('Время ожидания авторизации истекло. Попробуйте снова.');
        }
      }
    };

    // Проверяем статус каждые 2 секунды
    const interval = setInterval(checkAuthStatus, 2000);

    return () => clearInterval(interval);
  }, [telegramAuthToken, isWaitingForTelegram, login, navigate]);

  const handleGoogleLogin = async () => {
    try {
      setError(null);
      setIsLoading(true);
      const response = await fetch('http://localhost:8000/auth/google');
      const data = await response.json();
      window.location.href = data.auth_url;
    } catch (error) {
      console.error('Login error:', error);
      setError('Ошибка при инициации авторизации');
      setIsLoading(false);
    }
  };

  const handleTelegramLogin = async () => {
    try {
      setError(null);
      setIsWaitingForTelegram(true);
      
      // Получаем ссылку на бота с токеном авторизации
      const response = await api.get('/auth/telegram/init');
      const { bot_url, auth_token } = response.data;
      
      setTelegramAuthToken(auth_token);
      
      // Открываем бота в новой вкладке
      window.open(bot_url, '_blank');
      
    } catch (error: any) {
      console.error('Telegram login error:', error);
      setError('Ошибка при инициации авторизации через Telegram');
      setIsWaitingForTelegram(false);
    }
  };

  return (
    <div className="theme-transition min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 flex items-center justify-center px-4 py-12 relative overflow-hidden">
      {/* Декоративные элементы */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-400/10 dark:bg-blue-500/10 rounded-full blur-3xl"></div>
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-indigo-400/10 dark:bg-indigo-500/10 rounded-full blur-3xl"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-96 h-96 bg-purple-400/5 dark:bg-purple-500/5 rounded-full blur-3xl"></div>
      </div>

      <div className="theme-transition relative z-10 max-w-md w-full">
        {/* Главная карточка */}
        <div className="theme-transition bg-white/80 dark:bg-gray-800/80 backdrop-blur-xl rounded-2xl shadow-2xl border border-white/20 dark:border-gray-700/50 p-8 text-center">
          {/* Логотип/Иконка */}
          <div className="mb-8">
            <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-indigo-600 rounded-2xl mx-auto flex items-center justify-center shadow-lg">
              <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
          </div>

          {/* Заголовок */}
          <h1 className="text-3xl font-bold bg-gradient-to-r from-gray-900 to-gray-700 dark:from-white dark:to-gray-300 bg-clip-text text-transparent mb-2">
            Добро пожаловать!
          </h1>
          <p className="text-gray-600 dark:text-gray-400 mb-8 text-lg">
            Войдите в систему для доступа к вашему профилю
          </p>
          
          {/* Сообщения об ошибках */}
          {error && (
            <div className="theme-transition bg-red-50/80 dark:bg-red-900/20 border border-red-200 dark:border-red-800/50 text-red-700 dark:text-red-400 px-4 py-3 rounded-xl mb-6 backdrop-blur-sm" role="alert">
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                </svg>
                <span className="font-medium">Ошибка авторизации:</span>
              </div>
              <p className="text-sm mt-1">{error}</p>
            </div>
          )}
          
          {/* Сообщение ожидания Telegram */}
          {isWaitingForTelegram && (
            <div className="theme-transition bg-blue-50/80 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800/50 text-blue-700 dark:text-blue-400 px-4 py-3 rounded-xl mb-6 backdrop-blur-sm" role="alert">
              <div className="flex items-center justify-center gap-3">
                <svg className="animate-spin h-5 w-5 flex-shrink-0" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span className="font-medium">Ожидание авторизации в Telegram боте...</span>
              </div>
              <p className="text-sm mt-2 text-center">Откройте бота и нажмите /start</p>
            </div>
          )}
          
          {/* Кнопки авторизации */}
          <div className="space-y-4">
            {/* Google Login */}
            <button 
              className="group relative w-full bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 border border-gray-300 dark:border-gray-600 rounded-xl px-6 py-4 flex items-center justify-center gap-3 font-medium hover:bg-gray-50 dark:hover:bg-gray-600 hover:shadow-lg transition-all duration-300 shadow-sm disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:shadow-sm"
              onClick={handleGoogleLogin}
              disabled={isWaitingForTelegram || isLoading}
            >
              {isLoading ? (
                <svg className="animate-spin h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
              ) : (
                <img 
                  src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg" 
                  alt="Google"
                  className="w-5 h-5"
                />
              )}
              <span>{isLoading ? 'Подключение...' : 'Войти через Google'}</span>
            </button>
            
            {/* Разделитель */}
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300 dark:border-gray-600"></div>
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white dark:bg-gray-800 text-gray-500 dark:text-gray-400">или</span>
              </div>
            </div>
            
            {/* Telegram Login */}
            <button 
              className="group relative w-full bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-xl px-6 py-4 flex items-center justify-center gap-3 font-medium hover:from-blue-600 hover:to-indigo-700 hover:shadow-lg transition-all duration-300 shadow-lg disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:shadow-lg"
              onClick={handleTelegramLogin}
              disabled={isWaitingForTelegram || isLoading}
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                <path d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"/>
              </svg>
              <span>{isWaitingForTelegram ? 'Ожидание...' : 'Войти через Telegram'}</span>
            </button>
          </div>

          {/* Дополнительная информация */}
          <div className="mt-8 text-center">
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Безопасная авторизация через проверенные провайдеры
            </p>
          </div>
        </div>

        {/* Дополнительные элементы дизайна */}
        <div className="mt-6 text-center">
          <div className="flex justify-center space-x-2">
            <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
            <div className="w-2 h-2 bg-indigo-400 rounded-full animate-pulse" style={{animationDelay: '0.2s'}}></div>
            <div className="w-2 h-2 bg-purple-400 rounded-full animate-pulse" style={{animationDelay: '0.4s'}}></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;



