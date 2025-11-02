import React from 'react';

interface AdminMetricsProps {
  totalMessages: number;
  averageResponseTime: number;
  resolvedChats: number;
  activeAdmins: number;
  customerSatisfaction?: number;
}

const AdminMetrics: React.FC<AdminMetricsProps> = ({
  totalMessages,
  averageResponseTime,
  resolvedChats,
  activeAdmins,
  customerSatisfaction
}) => {
  const metrics = [
    {
      title: 'Всего сообщений',
      value: totalMessages.toLocaleString(),
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
        </svg>
      ),
      color: 'from-blue-500 to-blue-600',
      bgColor: 'bg-blue-50 dark:bg-blue-900/20',
      textColor: 'text-blue-600 dark:text-blue-400'
    },
    {
      title: 'Среднее время ответа',
      value: `${averageResponseTime} мин`,
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      color: 'from-green-500 to-emerald-500',
      bgColor: 'bg-green-50 dark:bg-green-900/20',
      textColor: 'text-green-600 dark:text-green-400'
    },
    {
      title: 'Решенных обращений',
      value: resolvedChats.toLocaleString(),
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      color: 'from-purple-500 to-indigo-500',
      bgColor: 'bg-purple-50 dark:bg-purple-900/20',
      textColor: 'text-purple-600 dark:text-purple-400'
    },
    {
      title: 'Активных администраторов',
      value: activeAdmins,
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.5 2.5 0 11-5 0 2.5 2.5 0 015 0z" />
        </svg>
      ),
      color: 'from-orange-500 to-red-500',
      bgColor: 'bg-orange-50 dark:bg-orange-900/20',
      textColor: 'text-orange-600 dark:text-orange-400'
    }
  ];

  if (customerSatisfaction !== undefined) {
    metrics.push({
      title: 'Удовлетворенность клиентов',
      value: `${customerSatisfaction}%`,
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" />
        </svg>
      ),
      color: 'from-pink-500 to-rose-500',
      bgColor: 'bg-pink-50 dark:bg-pink-900/20',
      textColor: 'text-pink-600 dark:text-pink-400'
    });
  }

  const getPerformanceLevel = (responseTime: number) => {
    if (responseTime <= 5) return { level: 'Отлично', color: 'text-green-600 dark:text-green-400' };
    if (responseTime <= 15) return { level: 'Хорошо', color: 'text-yellow-600 dark:text-yellow-400' };
    if (responseTime <= 30) return { level: 'Удовлетворительно', color: 'text-orange-600 dark:text-orange-400' };
    return { level: 'Требует улучшения', color: 'text-red-600 dark:text-red-400' };
  };

  const performance = getPerformanceLevel(averageResponseTime);

  return (
    <div className="space-y-6">
      {/* Основные метрики */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {metrics.map((metric, index) => (
          <div
            key={index}
            className={`${metric.bgColor} rounded-xl p-4 border border-gray-200 dark:border-gray-700 hover:shadow-md transition-shadow duration-200`}
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
                  {metric.title}
                </p>
                <p className={`text-2xl font-bold ${metric.textColor}`}>
                  {metric.value}
                </p>
              </div>
              <div className={`p-3 rounded-lg bg-gradient-to-r ${metric.color} text-white`}>
                {metric.icon}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Дополнительная информация */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-3">Производительность</h3>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">Время ответа:</span>
              <span className={`text-sm font-medium ${performance.color}`}>
                {performance.level}
              </span>
            </div>
            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
              <div
                className={`h-2 rounded-full ${
                  averageResponseTime <= 5 ? 'bg-green-500' :
                  averageResponseTime <= 15 ? 'bg-yellow-500' :
                  averageResponseTime <= 30 ? 'bg-orange-500' : 'bg-red-500'
                }`}
                style={{ width: `${Math.min((30 - averageResponseTime) / 30 * 100, 100)}%` }}
              ></div>
            </div>
          </div>
        </div>

        <div className="bg-white dark:bg-gray-800 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
          <h3 className="font-semibold text-gray-900 dark:text-white mb-3">Статистика</h3>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">Сообщений на админа:</span>
              <span className="text-sm font-medium text-gray-900 dark:text-white">
                {activeAdmins > 0 ? Math.round(totalMessages / activeAdmins) : 0}
              </span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600 dark:text-gray-400">Решенных за день:</span>
              <span className="text-sm font-medium text-gray-900 dark:text-white">
                {Math.round(resolvedChats / 30)} {/* Предполагаем 30 дней */}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AdminMetrics;


