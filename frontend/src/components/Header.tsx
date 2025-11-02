import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { UserRole } from '../types/user';
import ThemeToggle from './ThemeToggle';

const Header: React.FC = () => {
  const { user, logout } = useAuth();
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  const handleLogout = () => {
    logout();
    setIsMobileMenuOpen(false);
  };

  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };

  const closeMobileMenu = () => {
    setIsMobileMenuOpen(false);
  };

  const isAdmin = user?.role === UserRole.ADMIN || user?.role === UserRole.SUPER_ADMIN;

  // Закрытие меню при изменении размера экрана на desktop
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth >= 768) {
        setIsMobileMenuOpen(false);
      }
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  // Закрытие меню при клике вне его области
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as Element;
      if (isMobileMenuOpen && !target.closest('[data-mobile-menu]')) {
        setIsMobileMenuOpen(false);
      }
    };

    if (isMobileMenuOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [isMobileMenuOpen]);

  return (
    <header className="theme-transition bg-white dark:bg-gray-800 shadow-lg border-b border-gray-200 dark:border-gray-700 pb-1 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-12">
          {/* Логотип и название */}
          <div className="flex items-center">
            <Link to="/home" className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                </svg>
              </div>
              <div className="hidden sm:block">
                <h1 className="text-lg font-bold text-gray-900 dark:text-white">Компьютер.ок</h1>
                <p className="text-xs text-gray-500 dark:text-gray-400">Умный подбор комплектующих</p>
              </div>
            </Link>
          </div>

          {/* Навигационное меню */}
          <nav className="hidden md:flex space-x-6">
            <Link
              to="/builds"
              className={`px-2 py-1 rounded-md text-sm font-medium transition-colors duration-200 ${
                location.pathname.startsWith('/builds')
                  ? 'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300'
                  : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              Сборки
            </Link>
            <Link
              to="/reviews"
              className={`px-2 py-1 rounded-md text-sm font-medium transition-colors duration-200 ${
                isActive('/reviews') || isActive('/feedback')
                  ? 'bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300'
                  : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700'
              }`}
            >
              Отзывы
            </Link>
            {user && (
              <>
                <Link
                  to="/dashboard"
                  className={`px-2 py-1 rounded-md text-sm font-medium transition-colors duration-200 ${
                    isActive('/dashboard')
                      ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                      : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700'
                  }`}
                >
                  Панель управления
                </Link>
                {isAdmin && (
                  <Link
                    to="/admin"
                    className={`px-2 py-1 rounded-md text-sm font-medium transition-colors duration-200 ${
                      isActive('/admin')
                        ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                        : 'text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700'
                    }`}
                  >
                    Администрирование
                  </Link>
                )}
              </>
            )}
          </nav>

          {/* Пользовательское меню */}
          <div className="flex items-center space-x-4">
            {/* Кнопка переключения темы */}
            <ThemeToggle />
            
            {user ? (
              <div className="flex items-center space-x-4">
                {/* Информация о пользователе */}
                <div className="hidden sm:flex items-center space-x-3">
                  {user.picture && (
                    <img
                      src={user.picture}
                      alt={user.name}
                      className="w-6 h-6 rounded-full border-2 border-gray-200 dark:border-gray-600"
                    />
                  )}
                  <div className="text-sm">
                    <Link
                      to="/profile"
                      className={`font-medium transition-colors duration-200 ${
                        isActive('/profile')
                          ? 'text-blue-600 dark:text-blue-400'
                          : 'text-gray-900 dark:text-white hover:text-blue-600 dark:hover:text-blue-400'
                      }`}
                    >
                      {user.name}
                    </Link>
                    <p className="text-gray-500 dark:text-gray-400">{user.email}</p>
                  </div>
                </div>

                {/* Кнопка выхода - скрывается только на мобильных при открытом меню */}
                <button
                  onClick={handleLogout}
                  className={`bg-red-600 text-white p-1.5 rounded-lg hover:bg-red-700 dark:bg-red-700 dark:hover:bg-red-800 transition-all duration-200 shadow-sm ${
                    isMobileMenuOpen ? 'hidden md:block' : 'hidden md:block'
                  }`}
                  title="Выйти"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                  </svg>
                </button>
              </div>
            ) : (
              <Link
                to="/login"
                className={`bg-blue-600 text-white px-3 py-1.5 rounded-lg text-sm font-medium hover:bg-blue-700 dark:bg-blue-700 dark:hover:bg-blue-800 transition-all duration-200 shadow-sm ${
                  isMobileMenuOpen ? 'hidden md:block' : 'hidden md:block'
                }`}
              >
                Войти
              </Link>
            )}

            {/* Мобильное меню (гамбургер) */}
            <div className="md:hidden">
              <button
                type="button"
                onClick={toggleMobileMenu}
                className="relative inline-flex items-center justify-center p-1.5 rounded-md text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-inset focus:ring-blue-500 transition-colors duration-200"
                aria-label={isMobileMenuOpen ? 'Закрыть меню' : 'Открыть меню'}
                aria-expanded={isMobileMenuOpen}
              >
                <span className="sr-only">
                  {isMobileMenuOpen ? 'Закрыть меню' : 'Открыть меню'}
                </span>
                {/* Анимированная иконка гамбургера */}
                <div className="w-5 h-5 flex flex-col justify-center items-center">
                  <span
                    className={`block h-0.5 w-5 bg-current transform transition-all duration-300 ease-in-out ${
                      isMobileMenuOpen ? 'rotate-45 translate-y-1.5' : '-translate-y-1'
                    }`}
                  />
                  <span
                    className={`block h-0.5 w-5 bg-current transform transition-all duration-300 ease-in-out ${
                      isMobileMenuOpen ? 'opacity-0' : 'opacity-100'
                    }`}
                  />
                  <span
                    className={`block h-0.5 w-5 bg-current transform transition-all duration-300 ease-in-out ${
                      isMobileMenuOpen ? '-rotate-45 -translate-y-1.5' : 'translate-y-1'
                    }`}
                  />
                </div>
              </button>
            </div>
          </div>
        </div>

        {/* Мобильное меню */}
        <div 
          data-mobile-menu
          className={`md:hidden transition-all duration-300 ease-in-out overflow-hidden ${
            isMobileMenuOpen ? 'max-h-screen opacity-100' : 'max-h-0 opacity-0'
          }`}
        >
          <div className="theme-transition border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 shadow-lg">
            <div className="px-4 py-4 space-y-4">
              {/* Навигационные ссылки */}
              <div className="space-y-2">
                <Link
                  to="/builds"
                  onClick={closeMobileMenu}
                  className={`flex items-center px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                    location.pathname.startsWith('/builds')
                      ? 'bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 shadow-sm'
                      : 'text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-700'
                  }`}
                >
                  <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                  Сборки
                </Link>
                <Link
                  to="/reviews"
                  onClick={closeMobileMenu}
                  className={`flex items-center px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                    isActive('/reviews') || isActive('/feedback')
                      ? 'bg-purple-100 dark:bg-purple-900 text-purple-700 dark:text-purple-300 shadow-sm'
                      : 'text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-700'
                  }`}
                >
                  <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
                  </svg>
                  Отзывы
                </Link>
                {user && (
                  <>
                    <Link
                      to="/dashboard"
                      onClick={closeMobileMenu}
                      className={`flex items-center px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                        isActive('/dashboard')
                          ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 shadow-sm'
                          : 'text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-700'
                      }`}
                    >
                      <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                      </svg>
                      Панель управления
                    </Link>
                    {isAdmin && (
                      <Link
                        to="/admin"
                        onClick={closeMobileMenu}
                        className={`flex items-center px-4 py-3 rounded-lg text-sm font-medium transition-all duration-200 ${
                          isActive('/admin')
                            ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300 shadow-sm'
                            : 'text-gray-700 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-50 dark:hover:bg-gray-700'
                        }`}
                      >
                        <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                        </svg>
                        Администрирование
                      </Link>
                    )}
                  </>
                )}
              </div>
              
              {user && (
                <div className="space-y-4">
                  {/* Разделитель */}
                  <div className="border-t border-gray-200 dark:border-gray-600"></div>

                  {/* Информация о пользователе */}
                  <Link
                    to="/profile"
                    onClick={closeMobileMenu}
                    className={`flex items-center space-x-3 px-4 py-3 bg-gray-50 dark:bg-gray-700 rounded-lg transition-colors duration-200 ${
                      isActive('/profile')
                        ? 'bg-blue-50 dark:bg-blue-900/20'
                        : 'hover:bg-gray-100 dark:hover:bg-gray-600'
                    }`}
                  >
                    {user.picture && (
                      <img
                        src={user.picture}
                        alt={user.name}
                        className="w-10 h-10 rounded-full border-2 border-white dark:border-gray-600 shadow-sm"
                      />
                    )}
                    <div className="flex-1 min-w-0">
                      <p className={`text-sm font-medium truncate transition-colors duration-200 ${
                        isActive('/profile')
                          ? 'text-blue-600 dark:text-blue-400'
                          : 'text-gray-900 dark:text-white'
                      }`}>
                        {user.name}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{user.email}</p>
                    </div>
                  </Link>

                  {/* Кнопка выхода */}
                  <button
                    onClick={handleLogout}
                    className="w-full flex items-center justify-center px-4 py-3 text-sm font-medium text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors duration-200"
                    title="Выйти"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                    </svg>
                  </button>
                </div>
              )}
              
              {!user && (
                <div className="space-y-2 border-t border-gray-200 dark:border-gray-600 pt-4">
                  <Link
                    to="/login"
                    onClick={closeMobileMenu}
                    className="w-full flex items-center justify-center px-4 py-3 bg-blue-600 dark:bg-blue-700 text-white rounded-lg text-sm font-medium hover:bg-blue-700 dark:hover:bg-blue-800 transition-colors duration-200 shadow-sm"
                  >
                    <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1" />
                    </svg>
                    Войти
                  </Link>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
