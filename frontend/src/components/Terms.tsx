import React from 'react';
import { Link } from 'react-router-dom';

const Terms: React.FC = () => {
  return (
    <div className="theme-transition min-h-screen bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-800">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        {/* Header */}
        <div className="text-center mb-16">
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">
            Условия использования
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400">
            Последнее обновление: 29 октября 2025 г.
          </p>
        </div>

        {/* Introduction */}
        <section className="mb-12">
          <div className="bg-blue-50 dark:bg-gray-800 rounded-xl p-8 border border-blue-100 dark:border-gray-700">
            <p className="text-lg text-gray-700 dark:text-gray-300 leading-relaxed">
              Добро пожаловать на платформу <span className="font-bold">Компьютер.ок</span>. Используя наш сервис, 
              вы соглашаетесь соблюдать эти условия использования. Пожалуйста, внимательно прочитайте их перед началом работы.
            </p>
          </div>
        </section>

        {/* Content */}
        <div className="space-y-8">
          {/* Section 1 */}
          <section className="bg-white dark:bg-gray-800 rounded-xl p-8 border border-gray-200 dark:border-gray-700">
            <div className="flex items-start space-x-4 mb-4">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                <span className="text-blue-600 dark:text-blue-400 font-bold">1</span>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                Общие положения
              </h2>
            </div>
            <div className="ml-12 space-y-3 text-gray-700 dark:text-gray-300">
              <p>
                Платформа Компьютер.ок (далее — "Сервис") предоставляет услуги по подбору компьютерных комплектующих 
                с использованием технологий искусственного интеллекта.
              </p>
              <p>
                Используя Сервис, вы подтверждаете, что:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Вы достигли возраста 18 лет или используете Сервис под контролем родителей/опекунов</li>
                <li>Вы предоставляете достоверную информацию при регистрации</li>
                <li>Вы соглашаетесь использовать Сервис в законных целях</li>
                <li>Вы несёте ответственность за сохранность своей учётной записи</li>
              </ul>
            </div>
          </section>

          {/* Section 2 */}
          <section className="bg-white dark:bg-gray-800 rounded-xl p-8 border border-gray-200 dark:border-gray-700">
            <div className="flex items-start space-x-4 mb-4">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                <span className="text-blue-600 dark:text-blue-400 font-bold">2</span>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                Использование Сервиса
              </h2>
            </div>
            <div className="ml-12 space-y-3 text-gray-700 dark:text-gray-300">
              <p className="font-semibold">Бесплатный доступ:</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Просмотр до 3 случайных компонентов из подобранной сборки</li>
                <li>Базовая информация о совместимости</li>
                <li>Общие рекомендации по сборке</li>
              </ul>
              <p className="font-semibold mt-4">Платный доступ:</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Полный список всех подобранных комплектующих</li>
                <li>Прямые ссылки на магазины для покупки</li>
                <li>Детальный анализ производительности в играх</li>
                <li>Расширенная информация о совместимости</li>
              </ul>
              <p className="mt-4">
                Платные услуги предоставляются на основании отдельных тарифов, которые публикуются на сайте. 
                Оплата производится через безопасные платёжные системы.
              </p>
            </div>
          </section>

          {/* Section 3 */}
          <section className="bg-white dark:bg-gray-800 rounded-xl p-8 border border-gray-200 dark:border-gray-700">
            <div className="flex items-start space-x-4 mb-4">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                <span className="text-blue-600 dark:text-blue-400 font-bold">3</span>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                Интеллектуальная собственность
              </h2>
            </div>
            <div className="ml-12 space-y-3 text-gray-700 dark:text-gray-300">
              <p>
                Все материалы Сервиса, включая алгоритмы подбора, дизайн, тексты, графику и программный код, 
                защищены авторским правом и являются собственностью Компьютер.ок.
              </p>
              <p>
                Запрещается:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Копирование, модификация или распространение материалов Сервиса без письменного разрешения</li>
                <li>Реверс-инжиниринг алгоритмов подбора</li>
                <li>Автоматизированный сбор данных (парсинг, скрейпинг)</li>
                <li>Использование Сервиса для создания конкурирующих продуктов</li>
              </ul>
            </div>
          </section>

          {/* Section 4 */}
          <section className="bg-white dark:bg-gray-800 rounded-xl p-8 border border-gray-200 dark:border-gray-700">
            <div className="flex items-start space-x-4 mb-4">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                <span className="text-blue-600 dark:text-blue-400 font-bold">4</span>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                Ограничение ответственности
              </h2>
            </div>
            <div className="ml-12 space-y-3 text-gray-700 dark:text-gray-300">
              <p className="font-semibold text-orange-600 dark:text-orange-400">
                Важно! Сервис предоставляется "как есть" без каких-либо гарантий.
              </p>
              <p>
                Компьютер.ок не несёт ответственности за:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Точность информации о комплектующих (цены, характеристики, наличие)</li>
                <li>Качество товаров, приобретённых в сторонних магазинах</li>
                <li>Изменение цен и наличия товаров после формирования подборки</li>
                <li>Реальную производительность собранного компьютера (показатели могут отличаться от прогнозов)</li>
                <li>Проблемы совместимости, возникшие из-за особенностей конкретных модификаций комплектующих</li>
                <li>Любые прямые или косвенные убытки, связанные с использованием Сервиса</li>
              </ul>
              <p className="mt-4 font-semibold">
                Рекомендуем всегда проверять характеристики и совместимость компонентов перед покупкой, 
                а также консультироваться со специалистами при сомнениях.
              </p>
            </div>
          </section>

          {/* Section 5 */}
          <section className="bg-white dark:bg-gray-800 rounded-xl p-8 border border-gray-200 dark:border-gray-700">
            <div className="flex items-start space-x-4 mb-4">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                <span className="text-blue-600 dark:text-blue-400 font-bold">5</span>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                Оплата и возврат средств
              </h2>
            </div>
            <div className="ml-12 space-y-3 text-gray-700 dark:text-gray-300">
              <p>
                Все платежи обрабатываются через защищённые платёжные системы. Мы не храним данные ваших банковских карт.
              </p>
              <p className="font-semibold">Политика возврата:</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Возврат средств возможен в течение 14 дней с момента оплаты</li>
                <li>Возврат осуществляется только если вы не получили доступ к полной подборке</li>
                <li>После просмотра полной сборки возврат не производится</li>
                <li>Для возврата необходимо обратиться в службу поддержки</li>
              </ul>
            </div>
          </section>

          {/* Section 6 */}
          <section className="bg-white dark:bg-gray-800 rounded-xl p-8 border border-gray-200 dark:border-gray-700">
            <div className="flex items-start space-x-4 mb-4">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                <span className="text-blue-600 dark:text-blue-400 font-bold">6</span>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                Конфиденциальность данных
              </h2>
            </div>
            <div className="ml-12 space-y-3 text-gray-700 dark:text-gray-300">
              <p>
                Мы серьёзно относимся к защите ваших персональных данных. Подробная информация о том, 
                как мы собираем, используем и защищаем ваши данные, содержится в нашей{' '}
                <Link to="/privacy" className="text-blue-600 dark:text-blue-400 hover:underline font-semibold">
                  Политике конфиденциальности
                </Link>.
              </p>
            </div>
          </section>

          {/* Section 7 */}
          <section className="bg-white dark:bg-gray-800 rounded-xl p-8 border border-gray-200 dark:border-gray-700">
            <div className="flex items-start space-x-4 mb-4">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                <span className="text-blue-600 dark:text-blue-400 font-bold">7</span>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                Запрещённые действия
              </h2>
            </div>
            <div className="ml-12 space-y-3 text-gray-700 dark:text-gray-300">
              <p>
                При использовании Сервиса запрещается:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Нарушать законодательство РФ или международные законы</li>
                <li>Создавать множественные аккаунты для обхода ограничений</li>
                <li>Пытаться получить несанкционированный доступ к системам Сервиса</li>
                <li>Распространять вредоносное ПО или проводить кибератаки</li>
                <li>Использовать Сервис в коммерческих целях без согласования</li>
                <li>Публиковать ложную, вводящую в заблуждение информацию</li>
                <li>Нарушать права других пользователей</li>
              </ul>
              <p className="mt-4 text-orange-600 dark:text-orange-400 font-semibold">
                За нарушение этих правил мы можем заблокировать ваш аккаунт без возврата средств.
              </p>
            </div>
          </section>

          {/* Section 8 */}
          <section className="bg-white dark:bg-gray-800 rounded-xl p-8 border border-gray-200 dark:border-gray-700">
            <div className="flex items-start space-x-4 mb-4">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                <span className="text-blue-600 dark:text-blue-400 font-bold">8</span>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                Изменения условий
              </h2>
            </div>
            <div className="ml-12 space-y-3 text-gray-700 dark:text-gray-300">
              <p>
                Мы оставляем за собой право изменять эти Условия использования в любое время. 
                Об изменениях мы уведомим вас по электронной почте или через уведомление на сайте.
              </p>
              <p>
                Продолжение использования Сервиса после вступления изменений в силу означает ваше согласие с новыми условиями.
              </p>
            </div>
          </section>

          {/* Section 9 */}
          <section className="bg-white dark:bg-gray-800 rounded-xl p-8 border border-gray-200 dark:border-gray-700">
            <div className="flex items-start space-x-4 mb-4">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                <span className="text-blue-600 dark:text-blue-400 font-bold">9</span>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                Применимое право
              </h2>
            </div>
            <div className="ml-12 space-y-3 text-gray-700 dark:text-gray-300">
              <p>
                Эти Условия регулируются законодательством Российской Федерации. 
                Все споры, возникающие в связи с использованием Сервиса, подлежат рассмотрению в судах РФ.
              </p>
            </div>
          </section>

          {/* Section 10 */}
          <section className="bg-white dark:bg-gray-800 rounded-xl p-8 border border-gray-200 dark:border-gray-700">
            <div className="flex items-start space-x-4 mb-4">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                <span className="text-blue-600 dark:text-blue-400 font-bold">10</span>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                Контактная информация
              </h2>
            </div>
            <div className="ml-12 space-y-3 text-gray-700 dark:text-gray-300">
              <p>
                По вопросам, связанным с этими Условиями использования, вы можете связаться с нами:
              </p>
              <div className="flex items-center space-x-3 mt-4">
                <svg className="w-6 h-6 text-blue-600 dark:text-blue-400" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z"/>
                  <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z"/>
                </svg>
                <span className="text-lg">support@компьютерок.рф</span>
              </div>
              <div className="flex items-center space-x-3">
                <svg className="w-6 h-6 text-green-600 dark:text-green-400" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z"/>
                </svg>
                <span className="text-lg">8 (800) 555-35-35</span>
              </div>
            </div>
          </section>
        </div>

        {/* Footer note */}
        <div className="mt-12 text-center">
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            Используя Сервис Компьютер.ок, вы подтверждаете, что прочитали и согласны с этими Условиями использования
          </p>
          <Link
            to="/home"
            className="inline-flex items-center text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium"
          >
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
            </svg>
            Вернуться на главную
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Terms;

