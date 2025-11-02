import React from 'react';
import { Link } from 'react-router-dom';

const Privacy: React.FC = () => {
  return (
    <div className="theme-transition min-h-screen bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-800">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        {/* Header */}
        <div className="text-center mb-16">
          <div className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-r from-green-500 to-blue-600 rounded-2xl mb-6">
            <svg className="w-10 h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <h1 className="text-4xl md:text-5xl font-bold text-gray-900 dark:text-white mb-4">
            Политика конфиденциальности
          </h1>
          <p className="text-lg text-gray-600 dark:text-gray-400">
            Последнее обновление: 29 октября 2025 г.
          </p>
        </div>

        {/* Introduction */}
        <section className="mb-12">
          <div className="bg-green-50 dark:bg-gray-800 rounded-xl p-8 border border-green-100 dark:border-gray-700">
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0">
                <svg className="w-8 h-8 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-3">
                  Ваша конфиденциальность важна для нас
                </h3>
                <p className="text-lg text-gray-700 dark:text-gray-300 leading-relaxed">
                  Компьютер.ок уважает вашу конфиденциальность и обязуется защищать ваши персональные данные. 
                  Эта политика объясняет, какую информацию мы собираем, как мы её используем и какие у вас есть права.
                </p>
              </div>
            </div>
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
                Какие данные мы собираем
              </h2>
            </div>
            <div className="ml-12 space-y-4 text-gray-700 dark:text-gray-300">
              <div>
                <p className="font-semibold mb-2">Информация, которую вы предоставляете:</p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>Имя и email при регистрации через Google OAuth</li>
                  <li>Аватар и публичный профиль Google (если разрешено)</li>
                  <li>Параметры поиска (бюджет, цели использования, предпочтения)</li>
                  <li>История подборок комплектующих</li>
                  <li>Сообщения в чате поддержки</li>
                  <li>Отзывы и оценки сервиса</li>
                </ul>
              </div>
              <div>
                <p className="font-semibold mb-2">Автоматически собираемая информация:</p>
                <ul className="list-disc list-inside space-y-2 ml-4">
                  <li>IP-адрес и данные о браузере</li>
                  <li>Информация об устройстве (тип, операционная система)</li>
                  <li>Логи активности на сайте</li>
                  <li>Cookies и аналогичные технологии отслеживания</li>
                  <li>Время и продолжительность визитов</li>
                  <li>Страницы, которые вы посещаете на нашем сайте</li>
                </ul>
              </div>
            </div>
          </section>

          {/* Section 2 */}
          <section className="bg-white dark:bg-gray-800 rounded-xl p-8 border border-gray-200 dark:border-gray-700">
            <div className="flex items-start space-x-4 mb-4">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                <span className="text-blue-600 dark:text-blue-400 font-bold">2</span>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                Как мы используем ваши данные
              </h2>
            </div>
            <div className="ml-12 space-y-3 text-gray-700 dark:text-gray-300">
              <p>
                Мы используем собранную информацию для следующих целей:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>
                  <span className="font-semibold">Предоставление услуг:</span> подбор комплектующих, 
                  сохранение истории, персонализация рекомендаций
                </li>
                <li>
                  <span className="font-semibold">Улучшение качества:</span> анализ использования сервиса, 
                  выявление проблем, разработка новых функций
                </li>
                <li>
                  <span className="font-semibold">Коммуникация:</span> отправка уведомлений о статусе подборки, 
                  ответы на запросы поддержки
                </li>
                <li>
                  <span className="font-semibold">Безопасность:</span> предотвращение мошенничества, 
                  защита от злоупотреблений, обеспечение безопасности аккаунтов
                </li>
                <li>
                  <span className="font-semibold">Аналитика:</span> понимание того, как пользователи 
                  взаимодействуют с сервисом
                </li>
                <li>
                  <span className="font-semibold">Маркетинг:</span> отправка информации о новых функциях 
                  и специальных предложениях (с вашего согласия)
                </li>
                <li>
                  <span className="font-semibold">Соблюдение законов:</span> выполнение юридических обязательств
                </li>
              </ul>
            </div>
          </section>

          {/* Section 3 */}
          <section className="bg-white dark:bg-gray-800 rounded-xl p-8 border border-gray-200 dark:border-gray-700">
            <div className="flex items-start space-x-4 mb-4">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                <span className="text-blue-600 dark:text-blue-400 font-bold">3</span>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                Cookies и технологии отслеживания
              </h2>
            </div>
            <div className="ml-12 space-y-3 text-gray-700 dark:text-gray-300">
              <p>
                Мы используем cookies и аналогичные технологии для:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>
                  <span className="font-semibold">Необходимые cookies:</span> обеспечивают работу сайта, 
                  аутентификацию, безопасность (нельзя отключить)
                </li>
                <li>
                  <span className="font-semibold">Функциональные cookies:</span> запоминают ваши настройки 
                  (язык, тема оформления)
                </li>
                <li>
                  <span className="font-semibold">Аналитические cookies:</span> помогают нам понять, 
                  как используется сайт (можно отключить)
                </li>
              </ul>
              <p className="mt-4">
                Вы можете управлять cookies через настройки браузера, но отключение некоторых cookies может 
                ограничить функциональность сервиса.
              </p>
            </div>
          </section>

          {/* Section 4 */}
          <section className="bg-white dark:bg-gray-800 rounded-xl p-8 border border-gray-200 dark:border-gray-700">
            <div className="flex items-start space-x-4 mb-4">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                <span className="text-blue-600 dark:text-blue-400 font-bold">4</span>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                Передача данных третьим лицам
              </h2>
            </div>
            <div className="ml-12 space-y-3 text-gray-700 dark:text-gray-300">
              <p className="font-semibold text-green-600 dark:text-green-400 mb-3">
                Мы НЕ продаём ваши персональные данные третьим лицам!
              </p>
              <p>
                Мы можем передавать данные только:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>
                  <span className="font-semibold">Сервисным провайдерам:</span> Google (аутентификация), 
                  платёжные системы, хостинг-провайдеры, аналитические сервисы — только в объёме, 
                  необходимом для предоставления услуг
                </li>
                <li>
                  <span className="font-semibold">По требованию закона:</span> государственным органам 
                  при наличии законного требования
                </li>
                <li>
                  <span className="font-semibold">При реорганизации:</span> в случае слияния, поглощения 
                  или продажи бизнеса (с уведомлением пользователей)
                </li>
                <li>
                  <span className="font-semibold">С вашего согласия:</span> в других случаях только 
                  с вашего явного разрешения
                </li>
              </ul>
              <p className="mt-4">
                Все партнёры обязаны соблюдать конфиденциальность и использовать данные только для указанных целей.
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
                Защита данных
              </h2>
            </div>
            <div className="ml-12 space-y-3 text-gray-700 dark:text-gray-300">
              <p>
                Мы применяем современные меры безопасности для защиты ваших данных:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Шифрование данных при передаче (HTTPS/TLS)</li>
                <li>Шифрование конфиденциальных данных в базе данных</li>
                <li>Регулярные проверки безопасности и аудит кода</li>
                <li>Контроль доступа к данным (только авторизованный персонал)</li>
                <li>Мониторинг подозрительной активности</li>
                <li>Регулярное резервное копирование</li>
                <li>Защита от DDoS-атак и других киберугроз</li>
              </ul>
              <p className="mt-4 text-orange-600 dark:text-orange-400">
                Однако никакая система не может гарантировать 100% безопасность. Мы рекомендуем использовать 
                надёжные пароли и не передавать свои учётные данные третьим лицам.
              </p>
            </div>
          </section>

          {/* Section 6 */}
          <section className="bg-white dark:bg-gray-800 rounded-xl p-8 border border-gray-200 dark:border-gray-700">
            <div className="flex items-start space-x-4 mb-4">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                <span className="text-blue-600 dark:text-blue-400 font-bold">6</span>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                Ваши права
              </h2>
            </div>
            <div className="ml-12 space-y-3 text-gray-700 dark:text-gray-300">
              <p>
                В соответствии с законодательством о защите персональных данных вы имеете право:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>
                  <span className="font-semibold">Доступ:</span> запросить копию всех ваших данных, 
                  которые мы храним
                </li>
                <li>
                  <span className="font-semibold">Исправление:</span> запросить исправление неточных или 
                  неполных данных
                </li>
                <li>
                  <span className="font-semibold">Удаление:</span> запросить удаление ваших персональных данных 
                  ("право на забвение")
                </li>
                <li>
                  <span className="font-semibold">Ограничение обработки:</span> ограничить способы 
                  использования ваших данных
                </li>
                <li>
                  <span className="font-semibold">Переносимость:</span> получить ваши данные в 
                  структурированном формате
                </li>
                <li>
                  <span className="font-semibold">Возражение:</span> возразить против обработки данных 
                  в маркетинговых целях
                </li>
                <li>
                  <span className="font-semibold">Отзыв согласия:</span> отозвать ранее данное согласие 
                  на обработку данных
                </li>
              </ul>
              <p className="mt-4 font-semibold">
                Для реализации этих прав свяжитесь с нами по адресу: support@компьютерок.рф
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
                Хранение данных
              </h2>
            </div>
            <div className="ml-12 space-y-3 text-gray-700 dark:text-gray-300">
              <p>
                Мы храним ваши данные только в течение необходимого срока:
              </p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Данные аккаунта — пока он активен или пока вы не запросите удаление</li>
                <li>История подборок — в течение 3 лет с последней активности</li>
                <li>Логи и аналитика — 12 месяцев</li>
                <li>Данные об оплатах — в соответствии с законодательством (обычно 5 лет)</li>
                <li>Резервные копии — до 90 дней</li>
              </ul>
              <p className="mt-4">
                После удаления аккаунта мы удаляем все персональные данные в течение 30 дней, 
                за исключением информации, которую мы обязаны хранить по закону.
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
                Дети
              </h2>
            </div>
            <div className="ml-12 space-y-3 text-gray-700 dark:text-gray-300">
              <p>
                Наш сервис не предназначен для детей младше 18 лет. Мы сознательно не собираем персональные 
                данные от детей. Если вы родитель или опекун и узнали, что ваш ребёнок предоставил нам 
                персональные данные, пожалуйста, свяжитесь с нами для удаления этих данных.
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
                Международная передача данных
              </h2>
            </div>
            <div className="ml-12 space-y-3 text-gray-700 dark:text-gray-300">
              <p>
                Ваши данные обрабатываются и хранятся на серверах, расположенных в Российской Федерации. 
                В некоторых случаях данные могут передаваться за пределы РФ (например, при использовании 
                международных сервисов). Мы обеспечиваем, что такая передача осуществляется в соответствии 
                с применимым законодательством и с адекватными мерами защиты.
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
                Изменения политики
              </h2>
            </div>
            <div className="ml-12 space-y-3 text-gray-700 dark:text-gray-300">
              <p>
                Мы можем периодически обновлять эту Политику конфиденциальности. Об существенных изменениях 
                мы уведомим вас по электронной почте или через заметное уведомление на сайте. Рекомендуем 
                периодически просматривать эту страницу для получения актуальной информации.
              </p>
              <p className="mt-4">
                Дата последнего обновления всегда указана в начале документа.
              </p>
            </div>
          </section>

          {/* Section 11 */}
          <section className="bg-white dark:bg-gray-800 rounded-xl p-8 border border-gray-200 dark:border-gray-700">
            <div className="flex items-start space-x-4 mb-4">
              <div className="flex-shrink-0 w-8 h-8 bg-blue-100 dark:bg-blue-900 rounded-lg flex items-center justify-center">
                <span className="text-blue-600 dark:text-blue-400 font-bold">11</span>
              </div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
                Контактная информация
              </h2>
            </div>
            <div className="ml-12 space-y-3 text-gray-700 dark:text-gray-300">
              <p>
                Если у вас есть вопросы о нашей Политике конфиденциальности или вы хотите воспользоваться 
                своими правами в отношении персональных данных, свяжитесь с нами:
              </p>
              <div className="space-y-3 mt-4">
                <div className="flex items-center space-x-3">
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
              <p className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                <span className="font-semibold text-blue-900 dark:text-blue-300">Ответственное лицо по вопросам защиты персональных данных:</span><br/>
                Мы обработаем ваш запрос в течение 30 дней.
              </p>
            </div>
          </section>
        </div>

        {/* Footer note */}
        <div className="mt-12 text-center">
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            Используя Сервис Компьютер.ок, вы подтверждаете, что прочитали и поняли эту Политику конфиденциальности
          </p>
          <div className="flex justify-center gap-6">
            <Link
              to="/terms"
              className="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium"
            >
              Условия использования
            </Link>
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
    </div>
  );
};

export default Privacy;

