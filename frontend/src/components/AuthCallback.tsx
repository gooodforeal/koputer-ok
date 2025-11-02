import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { useNavigate, useSearchParams } from 'react-router-dom';

const AuthCallback: React.FC = () => {
  const { login, user, isLoading } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState<string>('Обработка авторизации...');
  const [hasProcessed, setHasProcessed] = useState(false);

  useEffect(() => {
    // Предотвращаем повторную обработку
    if (hasProcessed) return;

    const token = searchParams.get('token');
    const error = searchParams.get('error');
    const message = searchParams.get('message');

    if (error || message) {
      console.error('Auth error:', error || message);
      setStatus('Ошибка авторизации: ' + (error || message || 'Unknown error'));
      setHasProcessed(true);
      setTimeout(() => {
        navigate('/login?error=' + encodeURIComponent(error || message || 'Unknown error'));
      }, 2000);
      return;
    }

    if (token) {
      setStatus('Токен получен, вход в систему...');
      setHasProcessed(true);
      try {
        login(token);
        setStatus('Успешный вход! Перенаправление...');
        setTimeout(() => {
          navigate('/profile');
        }, 1000);
      } catch (error) {
        console.error('Login error:', error);
        setStatus('Ошибка входа в систему');
        setTimeout(() => {
          navigate('/login?error=' + encodeURIComponent('Login failed'));
        }, 2000);
      }
    } else {
      setStatus('Токен не получен');
      setHasProcessed(true);
      setTimeout(() => {
        navigate('/login?error=' + encodeURIComponent('No token received'));
      }, 2000);
    }
  }, [searchParams, login, navigate, hasProcessed]);

  // Если пользователь уже загружен, перенаправляем
  useEffect(() => {
    if (user && !isLoading && hasProcessed) {
      setStatus('Успешный вход! Перенаправление...');
      setTimeout(() => {
        navigate('/profile');
      }, 500);
    }
  }, [user, isLoading, hasProcessed, navigate]);

  return (
    <div className="theme-transition min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center px-4">
      <div className="theme-transition max-w-md w-full bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8 text-center">
        <div className="mb-6">
          {status.includes('Ошибка') ? (
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <svg className="w-8 h-8 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </div>
          ) : (
            <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          )}
        </div>
        <p className={`theme-transition text-lg font-medium ${status.includes('Ошибка') ? 'text-red-600 dark:text-red-400' : 'text-gray-700 dark:text-gray-300'}`}>
          {status}
        </p>
        {status.includes('Ошибка') && (
          <p className="theme-transition text-gray-500 dark:text-gray-400 mt-4">Вы будете перенаправлены на страницу входа...</p>
        )}
      </div>
    </div>
  );
};

export default AuthCallback;



