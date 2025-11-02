import React from 'react';
import { useAuth } from '../contexts/AuthContext';
import Login from './Login';

interface ProtectedRouteProps {
  children: React.ReactNode;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { user, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="theme-transition min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="theme-transition text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 dark:border-blue-400 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-300">Загрузка...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    return <Login />;
  }

  return <>{children}</>;
};

export default ProtectedRoute;




