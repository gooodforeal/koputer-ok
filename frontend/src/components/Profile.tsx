import React, { useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { UserRole, type UserUpdate } from '../types/user';
import { userApi } from '../services/api';
import Balance from './Balance';

const Profile: React.FC = () => {
  const { user, logout, updateUser } = useAuth();
  const [activeTab, setActiveTab] = useState<'overview' | 'balance' | 'settings' | 'activity'>('overview');
  const [isEditing, setIsEditing] = useState(false);
  const [isEditingEmail, setIsEditingEmail] = useState(false);
  const [editData, setEditData] = useState<UserUpdate>({});
  const [emailData, setEmailData] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [emailError, setEmailError] = useState<string | null>(null);

  if (!user) {
    return (
      <div className="theme-transition min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="theme-transition text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 dark:border-blue-400 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-300">Загрузка...</p>
        </div>
      </div>
    );
  }

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('ru-RU', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getInitials = (name: string) => {
    return name.split(' ').map(n => n[0]).join('').toUpperCase();
  };

  const getRoleTranslation = (role: UserRole) => {
    switch (role) {
      case UserRole.USER:
        return 'Пользователь';
      case UserRole.ADMIN:
        return 'Администратор';
      case UserRole.SUPER_ADMIN:
        return 'Супер-администратор';
      default:
        return 'Пользователь';
    }
  };

  const getRoleColor = (role: UserRole) => {
    switch (role) {
      case UserRole.USER:
        return 'text-orange-600 dark:text-orange-400';
      case UserRole.ADMIN:
        return 'text-blue-600 dark:text-blue-400';
      case UserRole.SUPER_ADMIN:
        return 'text-purple-600 dark:text-purple-400';
      default:
        return 'text-orange-600 dark:text-orange-400';
    }
  };

  const getRoleIconColor = (role: UserRole) => {
    switch (role) {
      case UserRole.USER:
        return 'bg-orange-100 dark:bg-orange-900';
      case UserRole.ADMIN:
        return 'bg-blue-100 dark:bg-blue-900';
      case UserRole.SUPER_ADMIN:
        return 'bg-purple-100 dark:bg-purple-900';
      default:
        return 'bg-orange-100 dark:bg-orange-900';
    }
  };

  const isTelegramUser = user?.telegram_id && !user?.google_id;

  const validateEmail = (email: string): string | null => {
    if (!email.trim()) {
      return 'Email обязателен для заполнения';
    }
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      return 'Введите корректный email адрес';
    }
    
    // Ограничение для пользователей из Telegram: максимум 30 символов
    if (isTelegramUser && email.length > 30) {
      return 'Email для пользователей из Telegram не может быть длиннее 30 символов';
    }
    
    if (email.length > 254) {
      return 'Email слишком длинный';
    }
    
    return null;
  };

  const handleEditCancel = () => {
    setIsEditing(false);
    setEditData({});
    setError(null);
    setSuccess(null);
  };

  const handleEmailEditStart = () => {
    setEmailData(user?.email || '');
    setIsEditingEmail(true);
    setError(null);
    setSuccess(null);
    setEmailError(null);
  };

  const handleEmailEditCancel = () => {
    setIsEditingEmail(false);
    setEmailData('');
    setError(null);
    setSuccess(null);
    setEmailError(null);
  };

  const handleInputChange = (field: keyof UserUpdate, value: string) => {
    setEditData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleEmailChange = (value: string) => {
    setEmailData(value);
    const validationError = validateEmail(value);
    setEmailError(validationError);
  };

  const handleSave = async () => {
    if (!user) return;
    
    setIsLoading(true);
    setError(null);
    setSuccess(null);
    
    try {
      const updatedUser = await userApi.updateProfile(editData);
      updateUser(updatedUser);
      setIsEditing(false);
      setEditData({});
      setSuccess('Профиль успешно обновлен!');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при обновлении профиля');
    } finally {
      setIsLoading(false);
    }
  };

  const handleEmailSave = async () => {
    if (!user) return;
    
    // Проверяем валидацию перед отправкой
    const validationError = validateEmail(emailData);
    if (validationError) {
      setEmailError(validationError);
      return;
    }
    
    setIsLoading(true);
    setError(null);
    setSuccess(null);
    setEmailError(null);
    
    try {
      const updatedUser = await userApi.updateProfile({ email: emailData });
      updateUser(updatedUser);
      setIsEditingEmail(false);
      setEmailData('');
      setSuccess('Email успешно обновлен!');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при обновлении email');
    } finally {
      setIsLoading(false);
    }
  };

  const tabs = [
    { id: 'overview', label: 'Обзор', icon: '👤' },
    { id: 'balance', label: 'Баланс', icon: '💰' },
    { id: 'settings', label: 'Настройки', icon: '⚙️' },
    { id: 'activity', label: 'Активность', icon: '📊' }
  ];

  return (
    <div className="theme-transition min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 dark:from-blue-700 dark:via-purple-700 dark:to-indigo-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="flex flex-col md:flex-row items-center md:items-end space-y-6 md:space-y-0 md:space-x-8">
            {/* Avatar */}
            <div className="relative">
              <div className="w-32 h-32 rounded-full border-4 border-white dark:border-gray-200 shadow-2xl overflow-hidden bg-gradient-to-br from-blue-400 to-purple-500">
                {user.picture ? (
                  <img 
                    src={user.picture} 
                    alt={user.name}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-white text-4xl font-bold">
                    {getInitials(user.name)}
                  </div>
                )}
              </div>
              <div className="absolute -bottom-2 -right-2 w-8 h-8 bg-green-500 rounded-full border-4 border-white dark:border-gray-200 flex items-center justify-center">
                <svg className="w-4 h-4 text-white" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
              </div>
            </div>

            {/* User Info */}
            <div className="text-center md:text-left text-white">
              <h1 className="text-4xl font-bold mb-2">{user.name}</h1>
              <p className="text-blue-100 text-lg mb-4">{user.email}</p>
              <div className="flex flex-wrap justify-center md:justify-start gap-4 text-sm">
                <div className="flex items-center space-x-2 bg-white/20 rounded-full px-4 py-2">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <span>Участник с {formatDate(user.created_at)}</span>
                </div>
                <div className="flex items-center space-x-2 bg-white/20 rounded-full px-4 py-2">
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>Активный пользователь</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Tabs */}
        <div className="mb-8">
          <div className="border-b border-gray-200 dark:border-gray-700">
            <nav className="-mb-px flex space-x-8">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id as any)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm transition-colors duration-200 ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600 dark:text-blue-400'
                      : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 hover:border-gray-300 dark:hover:border-gray-600'
                  }`}
                >
                  <span className="mr-2">{tab.icon}</span>
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>
        </div>

        {/* Tab Content */}
        <div className="space-y-8">
          {activeTab === 'overview' && (
            <>
              {/* Stats Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="theme-transition bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
                  <div className="flex items-center">
                    <div className="p-3 rounded-full bg-blue-100 dark:bg-blue-900">
                      <svg className="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                      </svg>
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Профиль</p>
                      <p className="text-2xl font-semibold text-gray-900 dark:text-white">Полный</p>
                    </div>
                  </div>
                </div>

                <div className="theme-transition bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
                  <div className="flex items-center">
                    <div className="p-3 rounded-full bg-green-100 dark:bg-green-900">
                      <svg className="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Статус</p>
                      <p className="text-2xl font-semibold text-gray-900 dark:text-white">Активен</p>
                    </div>
                  </div>
                </div>

                <div className="theme-transition bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
                  <div className="flex items-center">
                    <div className="p-3 rounded-full bg-purple-100 dark:bg-purple-900">
                      <svg className="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Время в системе</p>
                      <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                        {Math.floor((Date.now() - new Date(user.created_at).getTime()) / (1000 * 60 * 60 * 24))} дн.
                      </p>
                    </div>
                  </div>
                </div>

                <div className="theme-transition bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
                  <div className="flex items-center">
                    <div className={`p-3 rounded-full ${getRoleIconColor(user.role)}`}>
                      <svg className={`w-6 h-6 ${getRoleColor(user.role)}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                      </svg>
                    </div>
                    <div className="ml-4">
                      <p className="text-sm font-medium text-gray-600 dark:text-gray-400">Уровень</p>
                      <p className={`text-2xl font-semibold ${getRoleColor(user.role)}`}>
                        {getRoleTranslation(user.role)}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Profile Details */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                <div className="theme-transition bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Информация о профиле</h3>
                  <div className="space-y-4">
                    <div className="flex justify-between items-center py-2 border-b border-gray-100 dark:border-gray-700">
                      <span className="text-sm font-medium text-gray-600 dark:text-gray-400">Имя</span>
                      <span className="text-sm text-gray-900 dark:text-white">{user.name}</span>
                    </div>
                    <div className="flex justify-between items-center py-2 border-b border-gray-100 dark:border-gray-700">
                      <span className="text-sm font-medium text-gray-600 dark:text-gray-400">Email</span>
                      <span className="text-sm text-gray-900 dark:text-white">{user.email}</span>
                    </div>
                    {(user.role === UserRole.ADMIN || user.role === UserRole.SUPER_ADMIN) && (
                      <div className="flex justify-between items-center py-2 border-b border-gray-100 dark:border-gray-700">
                        <span className="text-sm font-medium text-gray-600 dark:text-gray-400">ID пользователя</span>
                        <span className="text-sm text-gray-900 dark:text-white font-mono">#{user.id}</span>
                      </div>
                    )}
                    <div className="flex justify-between items-center py-2 border-b border-gray-100 dark:border-gray-700">
                      <span className="text-sm font-medium text-gray-600 dark:text-gray-400">Роль</span>
                      <span className={`text-sm font-medium ${getRoleColor(user.role)}`}>
                        {getRoleTranslation(user.role)}
                      </span>
                    </div>
                    <div className="flex justify-between items-center py-2">
                      <span className="text-sm font-medium text-gray-600 dark:text-gray-400">Дата регистрации</span>
                      <span className="text-sm text-gray-900 dark:text-white">{formatDate(user.created_at)}</span>
                    </div>
                  </div>
                </div>

                <div className="theme-transition bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Быстрые действия</h3>
                  <div className="space-y-3">
                    <button 
                      disabled
                      className="w-full flex items-center justify-center px-4 py-3 bg-gray-300 dark:bg-gray-600 text-gray-500 dark:text-gray-400 rounded-lg cursor-not-allowed transition-colors duration-200"
                    >
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                      Редактировать профиль (отключено)
                    </button>
                    <button className="w-full flex items-center justify-center px-4 py-3 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg transition-colors duration-200">
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      </svg>
                      Настройки
                    </button>
                    <button 
                      onClick={logout}
                      className="w-full flex items-center justify-center px-4 py-3 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors duration-200"
                    >
                      <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                      </svg>
                      Выйти
                    </button>
                  </div>
                </div>
              </div>
            </>
          )}

          {activeTab === 'balance' && (
            <Balance />
          )}

          {activeTab === 'settings' && (
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">Настройки профиля</h3>
              
              {/* Сообщения об успехе/ошибке */}
              {success && (
                <div className="mb-4 p-4 bg-green-100 dark:bg-green-900 border border-green-400 text-green-700 dark:text-green-300 rounded-lg">
                  {success}
                </div>
              )}
              {error && (
                <div className="mb-4 p-4 bg-red-100 dark:bg-red-900 border border-red-400 text-red-700 dark:text-red-300 rounded-lg">
                  {error}
                </div>
              )}
              
              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Имя пользователя
                  </label>
                  {isEditing ? (
                    <input
                      type="text"
                      value={editData.name || ''}
                      onChange={(e) => handleInputChange('name', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    />
                  ) : (
                    <input
                      type="text"
                      value={user.name}
                      disabled
                      className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-500 dark:text-gray-400"
                    />
                  )}
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    {isTelegramUser ? 'Имя нельзя редактировать' : 'Имя синхронизируется с Google аккаунтом'}
                  </p>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Email адрес
                  </label>
                  <div className="flex space-x-2">
                    {isEditingEmail ? (
                      <input
                        type="email"
                        value={emailData}
                        onChange={(e) => handleEmailChange(e.target.value)}
                        className={`flex-1 px-3 py-2 border rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                          emailError 
                            ? 'border-red-500 focus:ring-red-500 focus:border-red-500' 
                            : 'border-gray-300 dark:border-gray-600'
                        }`}
                        placeholder="Введите ваш email"
                      />
                    ) : (
                      <input
                        type="email"
                        value={user.email || 'Не указан'}
                        disabled
                        className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-700 text-gray-500 dark:text-gray-400"
                      />
                    )}
                    {!isEditingEmail && isTelegramUser ? (
                      <button
                        onClick={handleEmailEditStart}
                        className="px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors duration-200 flex items-center"
                        title="Редактировать email"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                      </button>
                    ) : !isEditingEmail ? null : (
                      <div className="flex space-x-1">
                        <button
                          onClick={handleEmailSave}
                          disabled={isLoading || !!emailError}
                          className="px-3 py-2 bg-green-600 hover:bg-green-700 disabled:bg-green-400 text-white rounded-lg transition-colors duration-200 flex items-center"
                          title="Сохранить email"
                        >
                          {isLoading ? (
                            <svg className="animate-spin h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                            </svg>
                          ) : (
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                            </svg>
                          )}
                        </button>
                        <button
                          onClick={handleEmailEditCancel}
                          disabled={isLoading}
                          className="px-3 py-2 bg-gray-300 hover:bg-gray-400 dark:bg-gray-600 dark:hover:bg-gray-500 text-gray-700 dark:text-gray-300 rounded-lg transition-colors duration-200 flex items-center"
                          title="Отменить редактирование"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                          </svg>
                        </button>
                      </div>
                    )}
                  </div>
                  {emailError && (
                    <p className="text-xs text-red-600 dark:text-red-400 mt-1">
                      {emailError}
                    </p>
                  )}
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    {isTelegramUser ? 'Укажите ваш email для получения уведомлений' : 'Email синхронизируется с Google аккаунтом'}
                  </p>
                </div>
                
                {isEditing && (
                  <div className="flex space-x-3">
                    <button
                      onClick={handleSave}
                      disabled={isLoading}
                      className="px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-lg transition-colors duration-200 flex items-center"
                    >
                      {isLoading && (
                        <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                      )}
                      {isLoading ? 'Сохранение...' : 'Сохранить'}
                    </button>
                    <button
                      onClick={handleEditCancel}
                      disabled={isLoading}
                      className="px-4 py-2 bg-gray-300 hover:bg-gray-400 dark:bg-gray-600 dark:hover:bg-gray-500 text-gray-700 dark:text-gray-300 rounded-lg transition-colors duration-200"
                    >
                      Отмена
                    </button>
                  </div>
                )}
                
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Уведомления
                  </label>
                  <div className="space-y-3">
                    <label className="flex items-center">
                      <input type="checkbox" defaultChecked className="rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
                      <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">Email уведомления</span>
                    </label>
                    <label className="flex items-center">
                      <input type="checkbox" defaultChecked className="rounded border-gray-300 text-blue-600 focus:ring-blue-500" />
                      <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">Обновления системы</span>
                    </label>
                  </div>
                </div>
              </div>
            </div>
          )}

          {activeTab === 'activity' && (
            <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-6">Активность</h3>
              <div className="space-y-4">
                <div className="theme-transition flex items-center space-x-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div className="w-10 h-10 bg-green-100 dark:bg-green-900 rounded-full flex items-center justify-center">
                    <svg className="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900 dark:text-white">Успешный вход в систему</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">Сегодня в {new Date().toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })}</p>
                  </div>
                </div>
                <div className="theme-transition flex items-center space-x-4 p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                  <div className="w-10 h-10 bg-blue-100 dark:bg-blue-900 rounded-full flex items-center justify-center">
                    <svg className="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                  <div className="flex-1">
                    <p className="text-sm font-medium text-gray-900 dark:text-white">Профиль создан</p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">{formatDate(user.created_at)}</p>
                  </div>
                </div>
              </div>
            </div>
          )}

        </div>
      </div>
    </div>
  );
};

export default Profile;



