import React, { useState } from 'react';
import { useTheme } from '../contexts/ThemeContext';

const ThemeToggle: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  const [isAnimating, setIsAnimating] = useState(false);

  const handleToggle = () => {
    setIsAnimating(true);
    toggleTheme();
    
    // Сбрасываем состояние анимации после завершения
    setTimeout(() => {
      setIsAnimating(false);
    }, 600);
  };

  return (
    <button
      onClick={handleToggle}
      className={`p-1.5 rounded-lg text-gray-600 hover:text-gray-900 hover:bg-gray-100 dark:text-gray-300 dark:hover:text-white dark:hover:bg-gray-700 transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 ${
        isAnimating ? 'scale-95' : 'scale-100'
      }`}
      aria-label={theme === 'light' ? 'Переключить на темную тему' : 'Переключить на светлую тему'}
      title={theme === 'light' ? 'Переключить на темную тему' : 'Переключить на светлую тему'}
    >
      <div className="relative w-4 h-4">
        {/* Иконка луны для темной темы */}
        <svg 
          className={`absolute inset-0 w-4 h-4 theme-icon ${
            theme === 'light' 
              ? 'opacity-100 rotate-0 scale-100' 
              : 'opacity-0 -rotate-180 scale-75'
          }`}
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
          style={{
            transition: 'all 600ms cubic-bezier(0.4, 0, 0.2, 1)'
          }}
        >
          <path 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            strokeWidth={2} 
            d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" 
          />
        </svg>
        
        {/* Иконка солнца для светлой темы */}
        <svg 
          className={`absolute inset-0 w-4 h-4 theme-icon ${
            theme === 'dark' 
              ? 'opacity-100 rotate-0 scale-100' 
              : 'opacity-0 rotate-180 scale-75'
          }`}
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
          style={{
            transition: 'all 600ms cubic-bezier(0.4, 0, 0.2, 1)'
          }}
        >
          <path 
            strokeLinecap="round" 
            strokeLinejoin="round" 
            strokeWidth={2} 
            d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" 
          />
        </svg>
      </div>
    </button>
  );
};

export default ThemeToggle;
