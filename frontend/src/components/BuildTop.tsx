import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { buildsApi } from '../services/api';
import type { Build } from '../types/build';

const BuildTop: React.FC = () => {
  const [builds, setBuilds] = useState<Build[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchTopBuilds();
  }, []);

  const fetchTopBuilds = async () => {
    try {
      setLoading(true);
      const response = await buildsApi.getTopBuilds(10);
      setBuilds(response.builds);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при загрузке топа сборок');
    } finally {
      setLoading(false);
    }
  };

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
              <linearGradient id={`half-${i}`}>
                <stop offset="50%" stopColor="currentColor" />
                <stop offset="50%" stopColor="transparent" />
              </linearGradient>
            </defs>
            <path fill={`url(#half-${i})`} d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z" />
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

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Топ сборок</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-2">
            Лучшие сборки по рейтингу пользователей
          </p>
        </div>
        <Link
          to="/builds"
          className="px-4 py-2 bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
        >
          Все сборки
        </Link>
      </div>

      {error && (
        <div className="mb-6 p-4 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 rounded-lg">
          {error}
        </div>
      )}

      {/* Топ сборок */}
      <div className="space-y-4">
        {builds.map((build, index) => (
          <Link
            key={build.id}
            to={`/builds/${build.id}`}
            className="block bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-lg transition-shadow p-6"
          >
            <div className="flex items-start gap-4">
              {/* Место в топе */}
              <div className="flex-shrink-0">
                <div className={`w-12 h-12 rounded-full flex items-center justify-center text-2xl font-bold ${
                  index === 0 ? 'bg-yellow-400 text-yellow-900' :
                  index === 1 ? 'bg-gray-300 text-gray-700' :
                  index === 2 ? 'bg-orange-400 text-orange-900' :
                  'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                }`}>
                  {index + 1}
                </div>
              </div>

              {/* Информация о сборке */}
              <div className="flex-grow">
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
                  {build.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-300 mb-3 line-clamp-2">
                  {build.description}
                </p>

                <div className="flex items-center gap-4 flex-wrap">
                  {/* Автор */}
                  <div className="flex items-center gap-2">
                    {build.author?.picture && (
                      <img
                        src={build.author.picture}
                        alt={build.author.name}
                        className="w-6 h-6 rounded-full"
                      />
                    )}
                    <span className="text-sm text-gray-600 dark:text-gray-400">
                      {build.author?.name || 'Неизвестный автор'}
                    </span>
                  </div>

                  {/* Рейтинг */}
                  <div className="flex items-center gap-2">
                    {renderStars(build.average_rating)}
                    <span className="text-sm font-semibold text-gray-700 dark:text-gray-300">
                      {build.average_rating.toFixed(1)}
                    </span>
                    <span className="text-sm text-gray-500">
                      ({build.ratings_count} оценок)
                    </span>
                  </div>

                  {/* Просмотры */}
                  <div className="flex items-center gap-1 text-sm text-gray-500">
                    <span>👁</span>
                    <span>{build.views_count}</span>
                  </div>
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>

      {builds.length === 0 && !loading && (
        <div className="text-center py-12">
          <div className="text-6xl mb-4">🏆</div>
          <p className="text-xl text-gray-500 dark:text-gray-400">
            Топ сборок пока пуст
          </p>
          <p className="text-sm text-gray-400 dark:text-gray-500 mt-2">
            Создайте первую сборку и получите оценки от пользователей!
          </p>
          <Link
            to="/builds/create"
            className="mt-4 inline-block px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Создать сборку
          </Link>
        </div>
      )}
    </div>
  );
};

export default BuildTop;


