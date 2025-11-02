import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import type { User } from '../types/user';
import type { AuthContextType } from '../types/auth';

import { api } from '../services/api';

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isFetching, setIsFetching] = useState(false);

  useEffect(() => {
    const savedToken = localStorage.getItem('token');
    if (savedToken) {
      setToken(savedToken);
      fetchUserProfile(savedToken);
    } else {
      setIsLoading(false);
    }
  }, []);

  const fetchUserProfile = async (authToken: string, force: boolean = false) => {
    // Предотвращаем множественные одновременные запросы (кроме принудительных)
    if (isFetching && !force) {
      console.log('Уже загружаем профиль, пропускаем...');
      return;
    }
    
    setIsFetching(true);
    try {
      console.log('Загружаем профиль пользователя с токеном:', authToken.substring(0, 20) + '...');
      const response = await api.get('/auth/me', {
        headers: { Authorization: `Bearer ${authToken}` }
      });
      console.log('Профиль загружен:', response.data);
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch user profile:', error);
      // Не вызываем logout() автоматически, чтобы не сбрасывать токен
      // Пользователь может попробовать обновить страницу
      setUser(null);
    } finally {
      setIsLoading(false);
      setIsFetching(false);
    }
  };

  const login = async (authToken: string) => {
    console.log('Login вызван с токеном:', authToken.substring(0, 20) + '...');
    setToken(authToken);
    localStorage.setItem('token', authToken);
    console.log('Токен сохранен в localStorage');
    // Всегда загружаем профиль пользователя после логина (принудительно)
    await fetchUserProfile(authToken, true);
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem('token');
    setIsLoading(false);
  };

  const updateUser = (updatedUser: User) => {
    setUser(updatedUser);
  };

  const value: AuthContextType = {
    user,
    token,
    login,
    logout,
    updateUser,
    isLoading
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};



