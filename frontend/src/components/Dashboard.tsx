import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { api } from '../services/api';

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [protectedData, setProtectedData] = useState<string>('');
  const [loading, setLoading] = useState(false);

  const fetchProtectedData = async () => {
    setLoading(true);
    try {
      const response = await api.get('/users/protected');
      setProtectedData(JSON.stringify(response.data, null, 2));
    } catch (error) {
      console.error('Error fetching protected data:', error);
      setProtectedData('Ошибка при получении данных');
    } finally {
      setLoading(false);
    }
  };


  return (
    <div className="theme-transition min-h-screen bg-gray-50 dark:bg-gray-900 py-8 px-4">
      <div className="theme-transition max-w-4xl mx-auto bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">Панель управления</h1>
        <p className="text-gray-600 dark:text-gray-300 mb-8">Добро пожаловать, <strong className="text-gray-900 dark:text-white">{user?.name}</strong>!</p>
        
        <div className="mb-8">
          <button 
            className="bg-blue-600 dark:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 dark:hover:bg-blue-800 transition-colors duration-200 disabled:bg-gray-400 dark:disabled:bg-gray-600 disabled:cursor-not-allowed"
            onClick={fetchProtectedData}
            disabled={loading}
          >
            {loading ? (
              <span className="flex items-center gap-2">
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                Загрузка...
              </span>
            ) : (
              'Получить защищенные данные'
            )}
          </button>
        </div>

        {protectedData && (
          <div className="mt-8">
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Защищенные данные:</h3>
            <pre className="theme-transition bg-gray-100 dark:bg-gray-700 p-4 rounded-lg overflow-auto text-sm text-gray-800 dark:text-gray-200 border dark:border-gray-600">
              {protectedData}
            </pre>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;



