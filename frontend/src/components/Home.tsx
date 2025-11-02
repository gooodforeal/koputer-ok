import React from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import BackgroundDecorations from './BackgroundDecorations';

const Home: React.FC = () => {
  const { user } = useAuth();

  const features = [
    {
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
      ),
      title: 'Умный подбор комплектующих',
      description: 'Искусственный интеллект анализирует ваш бюджет и требования, подбирая оптимальное сочетание компонентов для максимальной производительности.'
    },
    {
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      title: 'Проверка совместимости',
      description: 'Автоматическая проверка совместимости всех компонентов между собой. Никаких несовместимых деталей - только работающие сборки.'
    },
    {
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
        </svg>
      ),
      title: 'Анализ производительности',
      description: 'Точный расчет FPS в популярных играх для вашей будущей сборки. Узнайте производительность до покупки.'
    },
    {
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 11V7a4 4 0 00-8 0v4M5 9h14l1 12H4L5 9z" />
        </svg>
      ),
      title: 'Ссылки на магазины',
      description: 'Прямые ссылки на проверенные интернет-магазины для покупки каждого компонента. Экономьте время на поиске.'
    },
    {
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      title: 'Гибкая модель монетизации',
      description: 'Бесплатный просмотр 3 компонентов для оценки качества подбора. Полный доступ после оплаты.'
    },
    {
      icon: (
        <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      title: 'Мгновенный результат',
      description: 'Получите готовую сборку за секунды. Не нужно тратить часы на изучение характеристик и совместимости.'
    }
  ];

  const steps = [
    {
      number: '01',
      title: 'Укажите параметры',
      description: 'Введите бюджет, цели использования (игры, работа, творчество) и ваши предпочтения.'
    },
    {
      number: '02',
      title: 'AI анализирует данные',
      description: 'Искусственный интеллект обрабатывает тысячи комплектующих и подбирает оптимальную конфигурацию.'
    },
    {
      number: '03',
      title: 'Проверка и тестирование',
      description: 'Система проверяет совместимость и рассчитывает производительность в играх.'
    },
    {
      number: '04',
      title: 'Получите результат',
      description: 'Готовая сборка с ценами, характеристиками и ссылками на покупку в магазинах.'
    }
  ];

  return (
    <div className="theme-transition min-h-screen bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-800">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        {/* Background decoration */}
        <div className="absolute inset-0 overflow-hidden">
          {/* Анимированные блобы */}
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-blue-400 dark:bg-blue-600 rounded-full mix-blend-multiply dark:mix-blend-soft-light filter blur-3xl opacity-20 animate-blob"></div>
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-purple-400 dark:bg-purple-600 rounded-full mix-blend-multiply dark:mix-blend-soft-light filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>
          <div className="absolute top-40 left-40 w-80 h-80 bg-pink-400 dark:bg-pink-600 rounded-full mix-blend-multiply dark:mix-blend-soft-light filter blur-3xl opacity-20 animate-blob animation-delay-4000"></div>
          
          {/* Дополнительные декоративные элементы */}
          <div className="absolute top-20 right-20 w-32 h-32 bg-gradient-to-br from-cyan-400 to-blue-500 rounded-full opacity-10"></div>
          <div className="absolute bottom-32 right-32 w-24 h-24 bg-gradient-to-br from-purple-400 to-pink-500 rounded-full opacity-15"></div>
          <div className="absolute top-1/2 left-10 w-16 h-16 bg-gradient-to-br from-green-400 to-teal-500 rounded-full opacity-20"></div>
          
          {/* Геометрические формы */}
          <div className="absolute top-32 left-1/4 w-20 h-20 bg-blue-300 dark:bg-blue-700 rounded-lg rotate-45"></div>
          <div className="absolute bottom-40 right-1/3 w-16 h-16 bg-purple-300 dark:bg-purple-700 rounded-full"></div>
          <div className="absolute top-1/3 right-1/4 w-12 h-12 bg-pink-300 dark:bg-pink-700 transform rotate-12"></div>
          
          {/* Сетка и узоры */}
          <div className="absolute inset-0 bg-pattern-circuit opacity-30"></div>
          <div className="absolute inset-0 bg-mesh opacity-20"></div>
          
          {/* SVG декоративные элементы */}
          <BackgroundDecorations variant="hero" />
        </div>

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-24">
          <div className="text-center">
            {/* Badge */}
            <div className="inline-flex items-center space-x-2 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 px-4 py-2 rounded-full text-sm font-medium mb-8">
              <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
              </svg>
              <span>Платформа на основе искусственного интеллекта</span>
            </div>

            {/* Main heading */}
            <h1 className="text-5xl md:text-6xl lg:text-7xl font-extrabold text-gray-900 dark:text-white mb-6">
              <span className="block text-reveal">Идеальный ПК</span>
              <span className="block bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent py-2 text-reveal" style={{animationDelay: '0.2s'}}>
                за минуты
              </span>
            </h1>

            <p className="text-xl md:text-2xl text-gray-600 dark:text-gray-300 mb-8 max-w-3xl mx-auto leading-relaxed">
              Веб-платформа, которая с помощью искусственного интеллекта подбирает оптимальную сборку компьютера 
              под ваш бюджет и задачи
            </p>

            {/* Key benefits */}
            <div className="flex flex-wrap justify-center gap-4 mb-12 text-sm md:text-base">
              <div className="flex items-center space-x-2 bg-white dark:bg-gray-800 px-4 py-2 rounded-lg shadow-sm">
                <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span className="text-gray-700 dark:text-gray-300">Проверка совместимости</span>
              </div>
              <div className="flex items-center space-x-2 bg-white dark:bg-gray-800 px-4 py-2 rounded-lg shadow-sm">
                <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span className="text-gray-700 dark:text-gray-300">Анализ FPS в играх</span>
              </div>
              <div className="flex items-center space-x-2 bg-white dark:bg-gray-800 px-4 py-2 rounded-lg shadow-sm">
                <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                <span className="text-gray-700 dark:text-gray-300">Ссылки на магазины</span>
              </div>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
              {user ? (
                <Link
                  to="/dashboard"
                  className="group relative inline-flex items-center justify-center px-8 py-4 text-lg font-medium text-white bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
                >
                  <span className="flex items-center">
                    Перейти к подбору
                    <svg className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                    </svg>
                  </span>
                </Link>
              ) : (
                <>
                  <Link
                    to="/login"
                    className="group relative inline-flex items-center justify-center px-8 py-4 text-lg font-medium text-white bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 btn-animated"
                  >
                    <span className="flex items-center">
                      Начать подбор
                      <svg className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                      </svg>
                    </span>
                  </Link>
                  <button className="inline-flex items-center justify-center px-8 py-4 text-lg font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700 transition-all duration-200 shadow-md hover:shadow-lg border border-gray-200 dark:border-gray-700">
                    Узнать больше
                  </button>
                </>
              )}
            </div>

            {/* Trust indicators */}
            <div className="mt-12 flex flex-wrap justify-center items-center gap-8 text-sm text-gray-500 dark:text-gray-400">
              <div className="flex items-center space-x-2">
                <svg className="w-5 h-5 text-yellow-500" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                </svg>
                <span>Бесплатный предпросмотр</span>
              </div>
              <div className="flex items-center space-x-2">
                <svg className="w-5 h-5 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
                </svg>
                <span>Безопасные платежи</span>
              </div>
              <div className="flex items-center space-x-2">
                <svg className="w-5 h-5 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
                <span>Мгновенный результат</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-20 bg-white dark:bg-gray-800 relative">
        {/* Фоновые узоры */}
        <div className="absolute inset-0 bg-pattern-dots opacity-20"></div>
        <div className="absolute inset-0 bg-pattern-hexagon opacity-10"></div>
        
        {/* SVG декоративные элементы */}
        <BackgroundDecorations variant="features" />
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">
              Почему выбирают нас?
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              Мы сочетаем передовые технологии AI с глубокими знаниями о компьютерном железе
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((feature, index) => (
              <div
                key={index}
                className="group bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800 p-8 rounded-2xl hover:shadow-xl transition-all duration-300 border border-gray-200 dark:border-gray-700 hover:border-blue-500 dark:hover:border-blue-500 relative texture-overlay feature-card shadow-glow"
              >
                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center text-white mb-6 group-hover:scale-110 transition-transform duration-300 pulse-glow">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">
                  {feature.title}
                </h3>
                <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works Section */}
      <section className="py-20 bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-800 relative">
        {/* Фоновые узоры */}
        <div className="absolute inset-0 bg-pattern-waves opacity-15"></div>
        <div className="absolute inset-0 bg-pattern-grid opacity-10"></div>
        
        {/* Декоративные элементы */}
        <div className="absolute top-10 left-10 w-24 h-24 bg-blue-200 dark:bg-blue-800 rounded-full opacity-20"></div>
        <div className="absolute bottom-10 right-10 w-32 h-32 bg-purple-200 dark:bg-purple-800 rounded-full opacity-15"></div>
        
        {/* SVG декоративные элементы */}
        <BackgroundDecorations variant="steps" />
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">
              Как это работает?
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
              Простой и понятный процесс от запроса до готовой сборки
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {steps.map((step, index) => (
              <div key={index} className="relative">
                {/* Connection line */}
                {index < steps.length - 1 && (
                  <div className="hidden lg:block absolute top-16 left-full w-full h-0.5 bg-gradient-to-r from-blue-500 to-purple-500 transform -translate-x-1/2 z-0"></div>
                )}
                
                <div className="relative z-10 text-center">
                  <div className="inline-flex items-center justify-center w-32 h-32 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full mb-6 shadow-lg">
                    <span className="text-4xl font-bold text-white">{step.number}</span>
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">
                    {step.title}
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400">
                    {step.description}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing hint Section */}
      <section className="py-20 bg-gradient-to-r from-blue-600 to-purple-600 relative overflow-hidden">
        {/* Анимированный градиент */}
        <div className="absolute inset-0 bg-gradient-animated opacity-80"></div>
        
        
        {/* SVG декоративные элементы */}
        <BackgroundDecorations variant="pricing" />
        
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-20">
          <div className="relative">
            <div className="absolute inset-0 bg-black/10 rounded-2xl -m-4"></div>
            <h2 className="text-4xl md:text-5xl font-bold text-white mb-6 relative z-10">
              Попробуйте бесплатно
            </h2>
            <p className="text-xl text-blue-100 mb-8 leading-relaxed relative z-10">
              Получите бесплатный доступ к 3 компонентам из подобранной сборки. 
              Оцените качество подбора перед покупкой полного доступа.
            </p>
          </div>
          <div className="flex flex-wrap justify-center gap-8 mb-10 relative z-10">
            <div className="bg-white/10 backdrop-blur-sm rounded-xl px-6 py-4">
              <div className="text-3xl font-bold text-white mb-2">3</div>
              <div className="text-blue-100">Бесплатных компонента</div>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-xl px-6 py-4">
              <div className="text-3xl font-bold text-white mb-2">∞</div>
              <div className="text-blue-100">Проверок совместимости</div>
            </div>
            <div className="bg-white/10 backdrop-blur-sm rounded-xl px-6 py-4">
              <div className="text-3xl font-bold text-white mb-2">100%</div>
              <div className="text-blue-100">Гарантия качества</div>
            </div>
          </div>
          {!user && (
            <Link
              to="/login"
              className="inline-flex items-center justify-center px-8 py-4 text-lg font-medium text-blue-600 bg-white rounded-xl hover:bg-gray-50 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 relative z-10"
            >
              <span className="flex items-center">
                Начать прямо сейчас
                <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </span>
            </Link>
          )}
        </div>
      </section>

      {/* FAQ Section */}
      <section id="faq" className="py-20 bg-gray-50 dark:bg-gray-900 relative">
        {/* Фоновые узоры */}
        <div className="absolute inset-0 bg-pattern-dots opacity-10"></div>
        <div className="absolute inset-0 bg-pattern-circuit opacity-5"></div>
        
        {/* Декоративные элементы */}
        <div className="absolute top-20 right-20 w-16 h-16 bg-blue-300 dark:bg-blue-700 rounded-lg rotate-45"></div>
        <div className="absolute bottom-20 left-20 w-20 h-20 bg-purple-300 dark:bg-purple-700 rounded-full"></div>
        
        {/* SVG декоративные элементы */}
        <BackgroundDecorations variant="faq" />
        
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">
              Часто задаваемые вопросы
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300">
              Ответы на популярные вопросы о нашей платформе
            </p>
          </div>

          <div className="space-y-4">
            {/* FAQ Item 1 */}
            <details className="group bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden">
              <summary className="flex justify-between items-center cursor-pointer p-6 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white pr-8">
                  Как работает подбор комплектующих?
                </h3>
                <svg className="w-6 h-6 text-gray-500 dark:text-gray-400 transform group-open:rotate-180 transition-transform duration-200 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </summary>
              <div className="px-6 pb-6 text-gray-600 dark:text-gray-300 leading-relaxed">
                Наша AI-система анализирует ваш бюджет, цели использования и предпочтения, затем обрабатывает базу данных с тысячами комплектующих. 
                Алгоритм учитывает совместимость компонентов, их производительность, актуальность и цену. В результате вы получаете оптимальную 
                сборку, которая максимально соответствует вашим требованиям.
              </div>
            </details>

            {/* FAQ Item 2 */}
            <details className="group bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden">
              <summary className="flex justify-between items-center cursor-pointer p-6 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white pr-8">
                  Что включает бесплатная версия?
                </h3>
                <svg className="w-6 h-6 text-gray-500 dark:text-gray-400 transform group-open:rotate-180 transition-transform duration-200 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </summary>
              <div className="px-6 pb-6 text-gray-600 dark:text-gray-300 leading-relaxed">
                Бесплатно вы получаете доступ к просмотру 3 случайных компонентов из подобранной сборки. Это позволяет оценить качество 
                подбора и убедиться, что система действительно учитывает ваши требования. Для получения полной сборки со всеми комплектующими, 
                ссылками на магазины и анализом производительности необходимо приобрести полный доступ.
              </div>
            </details>

            {/* FAQ Item 3 */}
            <details className="group bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden">
              <summary className="flex justify-between items-center cursor-pointer p-6 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white pr-8">
                  Как проверяется совместимость компонентов?
                </h3>
                <svg className="w-6 h-6 text-gray-500 dark:text-gray-400 transform group-open:rotate-180 transition-transform duration-200 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </summary>
              <div className="px-6 pb-6 text-gray-600 dark:text-gray-300 leading-relaxed">
                Система автоматически проверяет совместимость по множеству параметров: сокет процессора и материнской платы, поддержку оперативной памяти, 
                мощность блока питания, размеры компонентов относительно корпуса, интерфейсы подключения и многое другое. 
                Мы гарантируем, что все компоненты в предложенной сборке будут совместимы друг с другом.
              </div>
            </details>

            {/* FAQ Item 4 */}
            <details className="group bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden">
              <summary className="flex justify-between items-center cursor-pointer p-6 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white pr-8">
                  Как рассчитывается производительность в играх?
                </h3>
                <svg className="w-6 h-6 text-gray-500 dark:text-gray-400 transform group-open:rotate-180 transition-transform duration-200 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </summary>
              <div className="px-6 pb-6 text-gray-600 dark:text-gray-300 leading-relaxed">
                Мы используем базу данных реальных тестов и бенчмарков для различных сочетаний процессоров и видеокарт. 
                AI-модель анализирует эти данные и предсказывает FPS в популярных играх для вашей конкретной конфигурации. 
                Показатели основаны на тестах в разных разрешениях и настройках графики.
              </div>
            </details>

            {/* FAQ Item 5 */}
            <details className="group bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden">
              <summary className="flex justify-between items-center cursor-pointer p-6 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white pr-8">
                  Откуда берутся цены на комплектующие?
                </h3>
                <svg className="w-6 h-6 text-gray-500 dark:text-gray-400 transform group-open:rotate-180 transition-transform duration-200 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </summary>
              <div className="px-6 pb-6 text-gray-600 dark:text-gray-300 leading-relaxed">
                Мы сотрудничаем с крупнейшими интернет-магазинами компьютерной техники и регулярно обновляем цены. 
                В полной версии вы получите прямые ссылки на страницы товаров с актуальными ценами. 
                Система старается подобрать оптимальное соотношение цены и качества в рамках вашего бюджета.
              </div>
            </details>

            {/* FAQ Item 6 */}
            <details className="group bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden">
              <summary className="flex justify-between items-center cursor-pointer p-6 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white pr-8">
                  Могу ли я изменить компоненты в сборке?
                </h3>
                <svg className="w-6 h-6 text-gray-500 dark:text-gray-400 transform group-open:rotate-180 transition-transform duration-200 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </summary>
              <div className="px-6 pb-6 text-gray-600 dark:text-gray-300 leading-relaxed">
                Да, после получения подборки вы можете запросить новый вариант с другими параметрами. 
                Вы также можете указать предпочтения по производителям или конкретным компонентам. 
                Система учтет ваши пожелания и предложит альтернативные варианты сборки.
              </div>
            </details>

            {/* FAQ Item 7 */}
            <details className="group bg-white dark:bg-gray-800 rounded-xl shadow-md overflow-hidden">
              <summary className="flex justify-between items-center cursor-pointer p-6 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors duration-200">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white pr-8">
                  Как часто обновляется база данных комплектующих?
                </h3>
                <svg className="w-6 h-6 text-gray-500 dark:text-gray-400 transform group-open:rotate-180 transition-transform duration-200 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </summary>
              <div className="px-6 pb-6 text-gray-600 dark:text-gray-300 leading-relaxed">
                База данных обновляется ежедневно. Мы добавляем новые модели комплектующих, обновляем цены и удаляем снятые с производства 
                позиции. Это гарантирует, что вы получите актуальные рекомендации с доступными для покупки компонентами.
              </div>
            </details>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-20 bg-gray-50 dark:bg-gray-900 relative">
        {/* Фоновые узоры */}
        <div className="absolute inset-0 bg-pattern-waves opacity-10"></div>
        <div className="absolute inset-0 bg-pattern-hexagon opacity-5"></div>
        
        {/* Декоративные элементы */}
        <div className="absolute top-10 left-1/4 w-24 h-24 bg-gradient-to-br from-blue-400 to-purple-500 rounded-full opacity-20"></div>
        <div className="absolute bottom-10 right-1/4 w-32 h-32 bg-gradient-to-br from-purple-400 to-pink-500 rounded-full opacity-15"></div>
        
        {/* SVG декоративные элементы */}
        <BackgroundDecorations variant="testimonials" />
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">
              Что говорят наши пользователи?
            </h2>
            <p className="text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto mb-8">
              Тысячи пользователей уже доверились нашему сервису. Читайте отзывы реальных людей
            </p>
            <Link
              to="/feedback"
              className="inline-flex items-center justify-center px-6 py-3 text-base font-medium text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 transition-colors"
            >
              Посмотреть все отзывы
              <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </Link>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                name: "Алексей К.",
                rating: 5,
                text: "Отличный сервис! За несколько минут получил идеальную сборку под мой бюджет. Все компоненты совместимы и цены актуальные.",
                date: "2 дня назад"
              },
              {
                name: "Мария С.",
                rating: 5,
                text: "Долго искала подходящую конфигурацию для работы с графикой. AI подобрал именно то, что нужно. Рекомендую!",
                date: "5 дней назад"
              },
              {
                name: "Дмитрий В.",
                rating: 4,
                text: "Очень удобно, что есть расчет производительности в играх. Помогло определиться с выбором видеокарты.",
                date: "неделю назад"
              }
            ].map((testimonial, index) => (
              <div key={index} className="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 hover:shadow-xl transition-shadow">
                <div className="flex items-center gap-1 mb-4">
                  {[...Array(5)].map((_, i) => (
                    <svg
                      key={i}
                      className={`w-5 h-5 ${i < testimonial.rating ? 'text-yellow-400' : 'text-gray-300 dark:text-gray-600'}`}
                      fill="currentColor"
                      viewBox="0 0 20 20"
                    >
                      <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
                    </svg>
                  ))}
                </div>
                <p className="text-gray-700 dark:text-gray-300 mb-4 leading-relaxed">
                  "{testimonial.text}"
                </p>
                <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-700">
                  <div className="flex items-center gap-2">
                    <div className="w-10 h-10 bg-gradient-to-r from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white font-semibold">
                      {testimonial.name.charAt(0)}
                    </div>
                    <span className="font-medium text-gray-900 dark:text-white">{testimonial.name}</span>
                  </div>
                  <span className="text-sm text-gray-500 dark:text-gray-400">{testimonial.date}</span>
                </div>
              </div>
            ))}
          </div>

          <div className="text-center mt-12">
            <Link
              to="/feedback"
              className="inline-flex items-center justify-center px-8 py-4 text-lg font-medium text-white bg-gradient-to-r from-purple-600 to-blue-600 rounded-xl hover:from-purple-700 hover:to-blue-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
            >
              Оставить свой отзыв
            </Link>
          </div>
        </div>
      </section>

      {/* Final CTA Section */}
      <section className="py-20 bg-white dark:bg-gray-800 relative">
        {/* Фоновые узоры */}
        <div className="absolute inset-0 bg-pattern-grid opacity-15"></div>
        <div className="absolute inset-0 bg-pattern-dots opacity-10"></div>
        
        {/* Декоративные элементы */}
        <div className="absolute top-20 right-20 w-28 h-28 bg-blue-200 dark:bg-blue-800 rounded-lg rotate-12"></div>
        <div className="absolute bottom-20 left-20 w-24 h-24 bg-purple-200 dark:bg-purple-800 rounded-full"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-40 h-40 bg-gradient-to-br from-blue-300 to-purple-400 dark:from-blue-700 dark:to-purple-600 rounded-full opacity-10"></div>
        
        {/* SVG декоративные элементы */}
        <BackgroundDecorations variant="cta" />
        
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center relative z-10">
          <h2 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-6">
            Готовы собрать свой идеальный ПК?
          </h2>
          <p className="text-xl text-gray-600 dark:text-gray-300 mb-10">
            Присоединяйтесь к тысячам пользователей, которые уже нашли свою идеальную сборку
          </p>
          {user ? (
            <Link
              to="/dashboard"
              className="inline-flex items-center justify-center px-8 py-4 text-lg font-medium text-white bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
            >
              <span className="flex items-center">
                Перейти в панель управления
                <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </span>
            </Link>
          ) : (
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                to="/login"
                className="inline-flex items-center justify-center px-8 py-4 text-lg font-medium text-white bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-lg hover:shadow-xl transform hover:-translate-y-0.5"
              >
                <span className="flex items-center">
                  Войти через Google
                  <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </span>
              </Link>
            </div>
          )}
        </div>
      </section>

      {/* Add custom animations */}
      <style>{`
        @keyframes blob {
          0% {
            transform: translate(0px, 0px) scale(1);
          }
          33% {
            transform: translate(30px, -50px) scale(1.1);
          }
          66% {
            transform: translate(-20px, 20px) scale(0.9);
          }
          100% {
            transform: translate(0px, 0px) scale(1);
          }
        }
        .animate-blob {
          animation: blob 7s infinite;
        }
        .animation-delay-2000 {
          animation-delay: 2s;
        }
        .animation-delay-4000 {
          animation-delay: 4s;
        }
      `}</style>
    </div>
  );
};

export default Home;

