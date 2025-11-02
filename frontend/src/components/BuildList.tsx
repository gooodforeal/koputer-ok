import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { buildsApi } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import type { Build, BuildListResponse } from '../types/build';

const BuildList: React.FC = () => {
  const [builds, setBuilds] = useState<Build[]>([]);
  const [myBuilds, setMyBuilds] = useState<Build[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(0);
  const [totalBuilds, setTotalBuilds] = useState(0);
  const [sortOrder, setSortOrder] = useState<'newest' | 'oldest'>('newest');
  const [viewMode, setViewMode] = useState<1 | 2 | 4>(() => {
    const saved = localStorage.getItem('buildListViewMode');
    return saved ? (parseInt(saved) as 1 | 2 | 4) : 2;
  });
  const [activeTab, setActiveTab] = useState<'all' | 'my'>('all');
  const limit = 12;
  
  const { user } = useAuth();
  const isAuthenticated = !!user;

  useEffect(() => {
    fetchBuilds();
  }, [page, sortOrder, activeTab]);

  const fetchBuilds = async () => {
    try {
      setLoading(true);
      setError(null);
      // Очищаем старые данные при загрузке новой страницы
      setBuilds([]);
      setMyBuilds([]);
      
      const skip = (page - 1) * limit;
      const sortBy = 'created_at';
      const order = sortOrder === 'newest' ? 'desc' : 'asc';
      
      if (activeTab === 'my' && isAuthenticated) {
        const response: BuildListResponse = await buildsApi.getMyBuilds(skip, limit);
        setMyBuilds(response.builds);
        setTotalPages(response.total_pages);
        setTotalBuilds(response.total);
      } else {
        const response: BuildListResponse = await buildsApi.getBuilds(skip, limit, '', undefined, sortBy, order);
        setBuilds(response.builds);
        setTotalPages(response.total_pages);
        setTotalBuilds(response.total);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при загрузке сборок');
      setBuilds([]);
      setMyBuilds([]);
      setTotalPages(0);
      setTotalBuilds(0);
    } finally {
      setLoading(false);
    }
  };

  const handleViewModeChange = (mode: 1 | 2 | 4) => {
    setViewMode(mode);
    localStorage.setItem('buildListViewMode', mode.toString());
  };

  const getGridClasses = () => {
    switch (viewMode) {
      case 1:
        return 'grid-cols-1';
      case 2:
        return 'grid-cols-1 lg:grid-cols-2';
      case 4:
        return 'grid-cols-1 md:grid-cols-2 lg:grid-cols-4';
      default:
        return 'grid-cols-1 lg:grid-cols-2';
    }
  };

  const sortBuilds = (buildList: Build[]) => {
    return [...buildList].sort((a, b) => {
      const dateA = new Date(a.created_at).getTime();
      const dateB = new Date(b.created_at).getTime();
      return sortOrder === 'newest' ? dateB - dateA : dateA - dateB;
    });
  };

  const displayBuilds = sortBuilds(activeTab === 'my' ? myBuilds : builds);

  const renderStars = (rating: number) => {
    const fullStars = Math.floor(rating);
    const hasHalfStar = rating % 1 >= 0.5;
    const stars = [];

    for (let i = 0; i < 5; i++) {
      if (i < fullStars) {
        stars.push(
          <svg key={i} className="w-5 h-5 text-yellow-400 fill-current" viewBox="0 0 20 20">
            <path d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z" />
          </svg>
        );
      } else if (i === fullStars && hasHalfStar) {
        stars.push(
          <svg key={i} className="w-5 h-5 text-yellow-400" viewBox="0 0 20 20">
            <defs>
              <linearGradient id="half">
                <stop offset="50%" stopColor="currentColor" />
                <stop offset="50%" stopColor="transparent" />
              </linearGradient>
            </defs>
            <path fill="url(#half)" d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z" />
          </svg>
        );
      } else {
        stars.push(
          <svg key={i} className="w-5 h-5 text-gray-300" viewBox="0 0 20 20">
            <path fill="currentColor" d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z" />
          </svg>
        );
      }
    }

    return <div className="flex items-center gap-1">{stars}</div>;
  };

  if (loading && builds.length === 0) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="flex flex-col items-center gap-4">
          <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-200 border-t-blue-600"></div>
          <p className="text-gray-600 dark:text-gray-400">Загрузка сборок...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 py-8 px-4 transition-colors">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-6 rounded-2xl mb-6 shadow-lg">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-3xl font-bold mb-2 text-white">Каталог сборок</h1>
              <p className="text-purple-100">
                Найдено: <span className="font-semibold">{totalBuilds}</span> сборок
              </p>
            </div>
            <Link
              to="/builds/create"
              className="px-6 py-3 bg-white text-blue-600 rounded-lg hover:bg-blue-50 transition-colors font-medium shadow-md"
            >
              + Создать сборку
            </Link>
          </div>
        </div>

        {/* Tabs with Sort */}
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow mb-6 border border-gray-200 dark:border-gray-700">
          <div className="flex justify-between items-center border-b border-gray-200 dark:border-gray-700">
            <div className="flex">
              <button
                onClick={() => {
                  setActiveTab('all');
                  setPage(1);
                }}
                className={`px-6 py-3 font-medium transition-colors ${
                  activeTab === 'all'
                    ? 'border-b-2 border-purple-600 text-purple-600 dark:text-purple-400'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                }`}
              >
                Все сборки
              </button>
              {isAuthenticated && (
                <button
                  onClick={() => {
                    setActiveTab('my');
                    setPage(1);
                  }}
                  className={`px-6 py-3 font-medium transition-colors ${
                    activeTab === 'my'
                      ? 'border-b-2 border-purple-600 text-purple-600 dark:text-purple-400'
                      : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
                  }`}
                >
                  Мои сборки
                </button>
              )}
            </div>
            
            {/* Sort Button and View Mode */}
            <div className="flex items-center gap-3 px-6 py-3">
              {/* View Mode Buttons */}
              <div className="flex items-center gap-1 bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
                <button
                  onClick={() => handleViewModeChange(1)}
                  className={`p-2 rounded transition-colors ${
                    viewMode === 1
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                  title="1 колонка"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z" />
                  </svg>
                </button>
                <button
                  onClick={() => handleViewModeChange(2)}
                  className={`p-2 rounded transition-colors ${
                    viewMode === 2
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                  title="2 колонки"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v12a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v12a2 2 0 01-2 2h-2a2 2 0 01-2-2V6z" />
                  </svg>
                </button>
                <button
                  onClick={() => handleViewModeChange(4)}
                  className={`p-2 rounded transition-colors ${
                    viewMode === 4
                      ? 'bg-blue-600 text-white'
                      : 'text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                  title="4 колонки"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
                  </svg>
                </button>
              </div>

              {/* Sort Button */}
              <div className="flex items-center gap-2">
                <span className="text-sm text-gray-600 dark:text-gray-400">Сортировка:</span>
                <button
                  onClick={() => {
                    setSortOrder(sortOrder === 'newest' ? 'oldest' : 'newest');
                    setPage(1); // Сбрасываем на первую страницу при изменении сортировки
                  }}
                  className="flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    {sortOrder === 'newest' ? (
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4h13M3 8h9m-9 4h6m4 0l4-4m0 0l4 4m-4-4v12" />
                    ) : (
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4h13M3 8h9m-9 4h9m5-4v12m0 0l-4-4m4 4l4-4" />
                    )}
                  </svg>
                  <span className="text-sm font-medium">
                    {sortOrder === 'newest' ? 'Сначала новые' : 'Сначала старые'}
                  </span>
                </button>
              </div>
            </div>
          </div>
        </div>

        {error && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-800 dark:text-red-200 rounded-lg">
            {error}
          </div>
        )}

        {/* Список сборок */}
        <div className={`grid ${getGridClasses()} gap-6`}>
          {loading ? (
            <div className="col-span-full flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
          ) : displayBuilds.length === 0 ? (
            <div className={`col-span-full text-center py-12`}>
              <svg className="w-16 h-16 mx-auto mb-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
              </svg>
              <p className="text-gray-600 dark:text-gray-400 text-lg">
                {activeTab === 'my' ? 'У вас пока нет сборок' : 'Сборок пока нет'}
              </p>
            </div>
          ) : (
            displayBuilds.map((build) => (
              <Link
                key={build.id}
                to={`/builds/${build.id}`}
                className="bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-6 overflow-hidden"
              >
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white break-words overflow-hidden pr-2 flex-1 line-clamp-2">
                    {build.title}
                  </h3>
                </div>
                
                <p className="text-gray-600 dark:text-gray-400 mb-4 line-clamp-3 break-words whitespace-pre-wrap overflow-hidden">
                  {build.description}
                </p>
                
                <div className="flex items-center justify-between text-sm mb-4">
                  <div className="flex items-center gap-2 min-w-0 flex-1">
                    {build.author?.picture ? (
                      <img
                        src={build.author.picture}
                        alt={build.author.name}
                        className="w-8 h-8 rounded-full flex-shrink-0"
                      />
                    ) : (
                      <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-semibold flex-shrink-0">
                        {build.author?.name?.charAt(0)?.toUpperCase() || '?'}
                      </div>
                    )}
                    <span className="text-gray-700 dark:text-gray-300 truncate">{build.author?.name || 'Неизвестный автор'}</span>
                  </div>
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
                  <div className="flex items-center gap-3 flex-wrap">
                    <div className="flex items-center gap-2">
                      {renderStars(build.average_rating)}
                      <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                        {build.average_rating.toFixed(1)}
                      </span>
                      <span className="text-xs text-gray-500">
                        ({build.ratings_count})
                      </span>
                    </div>
                    {build.total_price > 0 && (
                      <div className="text-sm font-semibold text-green-600 dark:text-green-400">
                        {build.total_price.toLocaleString('ru-RU')} ₽
                      </div>
                    )}
                  </div>
                  <div className="flex items-center gap-1 text-sm text-gray-600 dark:text-gray-400">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    <span className="font-medium">{build.views_count}</span>
                  </div>
                </div>
              </Link>
            ))
          )}
        </div>

        {/* Pagination */}
        {totalPages > 1 && (
          <div className="mt-8 flex flex-col sm:flex-row justify-center items-center gap-4">
            {/* Информация о странице */}
            <div className="text-sm text-gray-600 dark:text-gray-400">
              Страница <span className="font-semibold text-gray-900 dark:text-white">{page}</span> из <span className="font-semibold text-gray-900 dark:text-white">{totalPages}</span>
              <span className="ml-2 text-gray-500 dark:text-gray-500">
                ({totalBuilds} сборок)
              </span>
            </div>

            {/* Навигация */}
            <div className="flex items-center gap-1">
              {/* Кнопка "В начало" */}
              <button
                onClick={() => {
                  setPage(1);
                  window.scrollTo({ top: 0, behavior: 'smooth' });
                }}
                disabled={page === 1}
                className="px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                title="В начало"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
                </svg>
              </button>

              {/* Кнопка "Предыдущая" */}
              <button
                onClick={() => {
                  setPage(page - 1);
                  window.scrollTo({ top: 0, behavior: 'smooth' });
                }}
                disabled={page === 1}
                className="px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                title="Предыдущая страница"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                </svg>
              </button>

              {/* Номера страниц */}
              <div className="flex items-center gap-1 flex-wrap justify-center">
                {(() => {
                  const pages: (number | string)[] = [];
                  const maxVisible = 7;
                  
                  if (totalPages <= maxVisible) {
                    // Показываем все страницы, если их немного
                    for (let i = 1; i <= totalPages; i++) {
                      pages.push(i);
                    }
                  } else {
                    // Всегда показываем первую страницу
                    pages.push(1);
                    
                    if (page <= 4) {
                      // Близко к началу: показываем первые страницы
                      for (let i = 2; i <= 5; i++) {
                        pages.push(i);
                      }
                      pages.push('...');
                      pages.push(totalPages);
                    } else if (page >= totalPages - 3) {
                      // Близко к концу: показываем последние страницы
                      pages.push('...');
                      for (let i = totalPages - 4; i <= totalPages; i++) {
                        pages.push(i);
                      }
                    } else {
                      // В середине: показываем текущую и соседние
                      pages.push('...');
                      for (let i = page - 1; i <= page + 1; i++) {
                        pages.push(i);
                      }
                      pages.push('...');
                      pages.push(totalPages);
                    }
                  }
                  
                  return pages.map((item, index) => {
                    if (item === '...') {
                      return (
                        <span key={`ellipsis-${index}`} className="px-2 text-gray-500 dark:text-gray-400">
                          ...
                        </span>
                      );
                    }
                    
                    const pageNumber = item as number;
                    return (
                      <button
                        key={pageNumber}
                        onClick={() => {
                          setPage(pageNumber);
                          window.scrollTo({ top: 0, behavior: 'smooth' });
                        }}
                        className={`min-w-[2.5rem] px-3 py-2 rounded-lg font-medium transition-colors ${
                          page === pageNumber
                            ? 'bg-blue-600 text-white shadow-md hover:bg-blue-700'
                            : 'bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                        }`}
                      >
                        {pageNumber}
                      </button>
                    );
                  });
                })()}
              </div>

              {/* Кнопка "Следующая" */}
              <button
                onClick={() => {
                  setPage(page + 1);
                  window.scrollTo({ top: 0, behavior: 'smooth' });
                }}
                disabled={page === totalPages}
                className="px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                title="Следующая страница"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                </svg>
              </button>

              {/* Кнопка "В конец" */}
              <button
                onClick={() => {
                  setPage(totalPages);
                  window.scrollTo({ top: 0, behavior: 'smooth' });
                }}
                disabled={page === totalPages}
                className="px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                title="В конец"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
                </svg>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default BuildList;


