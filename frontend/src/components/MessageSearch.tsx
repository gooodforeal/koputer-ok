import React, { useState } from 'react';
import type { Message } from '../types/chat-types';

interface MessageSearchProps {
  messages: Message[];
  onSearchResults: (results: Message[]) => void;
  onClearSearch: () => void;
}

const MessageSearch: React.FC<MessageSearchProps> = ({
  messages,
  onSearchResults,
  onClearSearch
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [isSearching, setIsSearching] = useState(false);
  const [searchResults, setSearchResults] = useState<Message[]>([]);
  const [currentResultIndex, setCurrentResultIndex] = useState(0);

  const handleSearch = (query: string) => {
    setSearchQuery(query);
    
    if (!query.trim()) {
      setSearchResults([]);
      onClearSearch();
      return;
    }

    setIsSearching(true);
    
    // Имитация поиска (в реальном приложении это может быть API вызов)
    setTimeout(() => {
      const results = messages.filter(message =>
        message.content.toLowerCase().includes(query.toLowerCase())
      );
      
      setSearchResults(results);
      setCurrentResultIndex(0);
      onSearchResults(results);
      setIsSearching(false);
    }, 300);
  };

  const goToNextResult = () => {
    if (searchResults.length > 0) {
      const nextIndex = (currentResultIndex + 1) % searchResults.length;
      setCurrentResultIndex(nextIndex);
      scrollToMessage(searchResults[nextIndex].id);
    }
  };

  const goToPreviousResult = () => {
    if (searchResults.length > 0) {
      const prevIndex = currentResultIndex === 0 ? searchResults.length - 1 : currentResultIndex - 1;
      setCurrentResultIndex(prevIndex);
      scrollToMessage(searchResults[prevIndex].id);
    }
  };

  const scrollToMessage = (messageId: number) => {
    const element = document.getElementById(`message-${messageId}`);
    if (element) {
      element.scrollIntoView({ behavior: 'smooth', block: 'center' });
      element.classList.add('bg-yellow-100', 'dark:bg-yellow-900/30');
      setTimeout(() => {
        element.classList.remove('bg-yellow-100', 'dark:bg-yellow-900/30');
      }, 2000);
    }
  };

  const clearSearch = () => {
    setSearchQuery('');
    setSearchResults([]);
    setCurrentResultIndex(0);
    onClearSearch();
  };

  return (
    <div className="bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-600 p-4">
      <div className="flex items-center gap-3">
        <div className="flex-1 relative">
          <input
            type="text"
            placeholder="Поиск в сообщениях..."
            value={searchQuery}
            onChange={(e) => handleSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
          />
          <svg className="absolute left-3 top-2.5 w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
        </div>

        {searchQuery && (
          <div className="flex items-center gap-2">
            {searchResults.length > 0 && (
              <div className="flex items-center gap-1">
                <button
                  onClick={goToPreviousResult}
                  className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                  title="Предыдущий результат"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                  </svg>
                </button>
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  {currentResultIndex + 1} из {searchResults.length}
                </span>
                <button
                  onClick={goToNextResult}
                  className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                  title="Следующий результат"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                </button>
              </div>
            )}
            
            <button
              onClick={clearSearch}
              className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              title="Очистить поиск"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        )}

        {isSearching && (
          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
        )}
      </div>

      {searchQuery && !isSearching && (
        <div className="mt-2 text-sm text-gray-500 dark:text-gray-400">
          {searchResults.length === 0 ? (
            <span>Результаты не найдены</span>
          ) : (
            <span>Найдено {searchResults.length} сообщений</span>
          )}
        </div>
      )}
    </div>
  );
};

export default MessageSearch;


