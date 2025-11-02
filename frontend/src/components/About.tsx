import React from 'react';
import { Link } from 'react-router-dom';

const About: React.FC = () => {
  return (
    <div className="theme-transition min-h-screen bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-800">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center space-x-3 mb-6">
            <div className="w-16 h-16 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl flex items-center justify-center">
              <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
              </svg>
            </div>
            <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white">
              О проекте
            </h1>
          </div>
          <p className="text-xl text-gray-600 dark:text-gray-400">
            Компьютер.ок — интеллектуальная платформа для подбора компьютерных комплектующих
          </p>
        </div>

        {/* Mission */}
        <section className="mb-16">
          <div className="bg-gradient-to-br from-blue-50 to-purple-50 dark:from-gray-800 dark:to-gray-700 rounded-2xl p-8 md:p-12 border border-blue-100 dark:border-gray-600">
            <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-6 flex items-center">
              <svg className="w-8 h-8 mr-3 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              Наша миссия
            </h2>
            <p className="text-lg text-gray-700 dark:text-gray-300 leading-relaxed mb-4">
              Мы создали платформу, которая помогает каждому собрать идеальный компьютер, независимо от уровня технических знаний. 
              С помощью искусственного интеллекта мы делаем процесс подбора комплектующих простым, быстрым и понятным.
            </p>
            <p className="text-lg text-gray-700 dark:text-gray-300 leading-relaxed">
              Наша цель — избавить вас от часов изучения характеристик, форумов и обзоров. Просто укажите ваши требования, 
              и AI подберёт оптимальную сборку с учётом совместимости, производительности и бюджета.
            </p>
          </div>
        </section>

        {/* What we do */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
            Что мы делаем
          </h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow duration-300">
              <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">
                Умный подбор
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Искусственный интеллект анализирует тысячи комплектующих и подбирает оптимальную сборку под ваши задачи и бюджет.
              </p>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow duration-300">
              <div className="w-12 h-12 bg-green-100 dark:bg-green-900 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">
                Проверка совместимости
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Автоматическая проверка всех компонентов на совместимость друг с другом — никаких несовместимых деталей.
              </p>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow duration-300">
              <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">
                Анализ производительности
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Предсказание FPS в популярных играх для вашей будущей сборки на основе реальных тестов и бенчмарков.
              </p>
            </div>

            <div className="bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700 hover:shadow-lg transition-shadow duration-300">
              <div className="w-12 h-12 bg-orange-100 dark:bg-orange-900 rounded-lg flex items-center justify-center mb-4">
                <svg className="w-6 h-6 text-orange-600 dark:text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">
                Прямые ссылки
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Ссылки на проверенные интернет-магазины для покупки каждого компонента с актуальными ценами.
              </p>
            </div>
          </div>
        </section>

        {/* Technology */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
            Технологии
          </h2>
          <div className="bg-white dark:bg-gray-800 rounded-xl p-8 border border-gray-200 dark:border-gray-700">
            <p className="text-lg text-gray-700 dark:text-gray-300 leading-relaxed mb-4">
              Платформа Компьютер.ок построена на современных технологиях машинного обучения и анализа больших данных. 
              Наш AI обучен на тысячах конфигураций компьютеров, результатах тестов производительности и 
              данных о совместимости комплектующих.
            </p>
            <p className="text-lg text-gray-700 dark:text-gray-300 leading-relaxed mb-6">
              Мы регулярно обновляем базу данных комплектующих, отслеживаем появление новых моделей и изменения цен. 
              Это позволяет предлагать актуальные решения, доступные для покупки прямо сейчас.
            </p>
            <div className="flex flex-wrap gap-3">
              <span className="px-4 py-2 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full text-sm font-medium">
                Искусственный интеллект
              </span>
              <span className="px-4 py-2 bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 rounded-full text-sm font-medium">
                Машинное обучение
              </span>
              <span className="px-4 py-2 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded-full text-sm font-medium">
                Анализ данных
              </span>
              <span className="px-4 py-2 bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200 rounded-full text-sm font-medium">
                Автоматизация
              </span>
            </div>
          </div>
        </section>

        {/* Values */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
            Наши ценности
          </h2>
          <div className="space-y-4">
            <div className="flex items-start space-x-4 bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-blue-600 dark:text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">Простота</h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Мы делаем сложные технологии доступными для всех — от новичков до профессионалов.
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-4 bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
              <div className="flex-shrink-0 w-8 h-8 bg-green-100 dark:bg-green-900 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">Качество</h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Мы предлагаем только проверенные решения с гарантированной совместимостью компонентов.
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-4 bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
              <div className="flex-shrink-0 w-8 h-8 bg-purple-100 dark:bg-purple-900 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-purple-600 dark:text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">Прозрачность</h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Мы показываем, как работает система подбора, и предлагаем бесплатный предпросмотр результата.
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-4 bg-white dark:bg-gray-800 rounded-xl p-6 border border-gray-200 dark:border-gray-700">
              <div className="flex-shrink-0 w-8 h-8 bg-orange-100 dark:bg-orange-900 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-orange-600 dark:text-orange-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
              </div>
              <div>
                <h3 className="text-lg font-bold text-gray-900 dark:text-white mb-2">Инновации</h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Мы постоянно совершенствуем наши алгоритмы и добавляем новые функции на основе отзывов пользователей.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Team */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
            Команда
          </h2>
          <div className="bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-700 rounded-xl p-8 border border-gray-200 dark:border-gray-600">
            <p className="text-lg text-gray-700 dark:text-gray-300 leading-relaxed">
              Наша команда состоит из опытных разработчиков, специалистов по машинному обучению и экспертов 
              в области компьютерного железа. Мы объединили свои знания и опыт, чтобы создать платформу, 
              которая действительно помогает людям выбрать правильные комплектующие для своих задач.
            </p>
          </div>
        </section>

        {/* Contact */}
        <section className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
            Связь с нами
          </h2>
          <div className="bg-white dark:bg-gray-800 rounded-xl p-8 border border-gray-200 dark:border-gray-700">
            <p className="text-lg text-gray-700 dark:text-gray-300 mb-6">
              Мы всегда рады обратной связи и готовы ответить на ваши вопросы:
            </p>
            <div className="space-y-3">
              <div className="flex items-center space-x-3 text-gray-700 dark:text-gray-300">
                <svg className="w-6 h-6 text-blue-600 dark:text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z"/>
                  <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z"/>
                </svg>
                <span className="text-lg">support@компьютерок.рф</span>
              </div>
              <div className="flex items-center space-x-3 text-gray-700 dark:text-gray-300">
                <svg className="w-6 h-6 text-green-600 dark:text-green-400" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z"/>
                </svg>
                <span className="text-lg">8 (800) 555-35-35</span>
              </div>
            </div>
          </div>
        </section>

        {/* CTA */}
        <div className="text-center bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-10">
          <h3 className="text-3xl font-bold text-white mb-4">
            Готовы начать?
          </h3>
          <p className="text-xl text-blue-100 mb-8">
            Попробуйте подобрать комплектующие с помощью нашего AI прямо сейчас
          </p>
          <Link
            to="/dashboard"
            className="inline-flex items-center justify-center px-8 py-4 text-lg font-medium text-blue-600 bg-white rounded-xl hover:bg-gray-50 transition-all duration-200 shadow-lg hover:shadow-xl"
          >
            <span className="flex items-center">
              Начать подбор
              <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </span>
          </Link>
        </div>
      </div>
    </div>
  );
};

export default About;

