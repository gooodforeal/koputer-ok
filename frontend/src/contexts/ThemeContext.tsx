import React, { createContext, useContext, useState, useEffect } from 'react';
import type { ReactNode } from 'react';

type Theme = 'light' | 'dark';

interface ThemeContextType {
  theme: Theme;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

interface ThemeProviderProps {
  children: ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [theme, setTheme] = useState<Theme>(() => {
    // Проверяем, что мы в браузере
    if (typeof window === 'undefined') {
      return 'light';
    }
    
    // Проверяем сохраненную тему в localStorage или системные настройки
    const savedTheme = localStorage.getItem('theme') as Theme;
    if (savedTheme) {
      return savedTheme;
    }
    
    // Проверяем системные настройки
    if (window.matchMedia('(prefers-color-scheme: dark)').matches) {
      return 'dark';
    }
    
    return 'light';
  });

  useEffect(() => {
    // Проверяем, что мы в браузере
    if (typeof window === 'undefined') {
      return;
    }
    
    // Применяем тему к документу с плавным переходом
    const root = document.documentElement;
    const body = document.body;
    
    // Добавляем класс для анимации
    body.classList.add('theme-transition');
    
    if (theme === 'dark') {
      root.classList.add('dark');
    } else {
      root.classList.remove('dark');
    }
    
    // Убираем класс анимации после завершения перехода
    const timeoutId = setTimeout(() => {
      body.classList.remove('theme-transition');
    }, 600);
    
    // Сохраняем тему в localStorage
    try {
      localStorage.setItem('theme', theme);
    } catch (error) {
      console.error('Error saving theme to localStorage:', error);
    }
    
    // Очищаем таймаут при размонтировании
    return () => {
      clearTimeout(timeoutId);
    };
  }, [theme]);

  const toggleTheme = () => {
    setTheme(prevTheme => {
      const newTheme = prevTheme === 'light' ? 'dark' : 'light';
      return newTheme;
    });
  };

  const value: ThemeContextType = {
    theme,
    toggleTheme
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};
