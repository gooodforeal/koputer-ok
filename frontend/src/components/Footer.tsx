import React from 'react';
import { Link } from 'react-router-dom';

const Footer: React.FC = () => {
  return (
    <footer className="theme-transition bg-gray-900 dark:bg-gray-800 text-white">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Логотип и описание */}
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center space-x-3 mb-4">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
                </svg>
              </div>
              <h3 className="text-2xl font-bold">Компьютер.ок</h3>
            </div>
            <p className="text-gray-300 dark:text-gray-400 mb-4 max-w-md">
              Интеллектуальная платформа для подбора оптимальной сборки компьютера. 
              Искусственный интеллект поможет собрать идеальный ПК под ваш бюджет и задачи.
            </p>
            <div className="flex space-x-4">
              <a 
                href="https://vk.com" 
                className="text-gray-400 dark:text-gray-500 hover:text-white transition-colors duration-200"
                target="_blank"
                rel="noopener noreferrer"
                title="ВКонтакте"
              >
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M15.684 0H8.316C1.592 0 0 1.592 0 8.316v7.368C0 22.408 1.592 24 8.316 24h7.368C22.408 24 24 22.408 24 15.684V8.316C24 1.592 22.408 0 15.684 0zm3.692 17.123h-1.744c-.66 0-.864-.525-2.05-1.727-1.033-1-1.492-1.135-1.744-1.135-.356 0-.458.102-.458.593v1.575c0 .424-.135.678-1.253.678-1.846 0-3.896-1.118-5.335-3.202C4.624 10.857 4.03 8.57 4.03 8.096c0-.254.102-.491.593-.491h1.744c.44 0 .61.203.78.677.863 2.49 2.303 4.675 2.896 4.675.22 0 .322-.102.322-.66V9.721c-.068-1.186-.695-1.287-.695-1.711 0-.203.17-.407.44-.407h2.744c.373 0 .508.203.508.643v3.473c0 .372.17.508.271.508.22 0 .407-.136.813-.542 1.254-1.406 2.151-3.574 2.151-3.574.119-.254.322-.491.763-.491h1.744c.525 0 .644.27.525.643-.22 1.017-2.354 4.031-2.354 4.031-.186.305-.254.44 0 .78.186.254.796.78 1.203 1.253.745.847 1.32 1.558 1.473 2.05.17.49-.085.744-.576.744z"/>
                </svg>
              </a>
              <a 
                href="https://t.me" 
                className="text-gray-400 dark:text-gray-500 hover:text-white transition-colors duration-200"
                target="_blank"
                rel="noopener noreferrer"
                title="Telegram"
              >
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0C5.373 0 0 5.373 0 12s5.373 12 12 12 12-5.373 12-12S18.627 0 12 0zm5.562 8.161c-.18 1.897-.962 6.502-1.359 8.627-.168.9-.5 1.201-.82 1.23-.697.064-1.226-.461-1.901-.903-1.056-.692-1.653-1.123-2.678-1.799-1.185-.781-.417-1.21.258-1.911.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.139-5.062 3.345-.479.329-.913.489-1.302.481-.428-.008-1.252-.241-1.865-.44-.752-.244-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.831-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635.099-.002.321.023.465.14.122.098.155.231.171.325.016.093.036.306.02.472z"/>
                </svg>
              </a>
              <a 
                href="https://youtube.com" 
                className="text-gray-400 dark:text-gray-500 hover:text-white transition-colors duration-200"
                target="_blank"
                rel="noopener noreferrer"
                title="YouTube"
              >
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814zM9.545 15.568V8.432L15.818 12l-6.273 3.568z"/>
                </svg>
              </a>
            </div>
          </div>

          {/* Сервисы */}
          <div>
            <h4 className="text-lg font-semibold mb-4">Сервисы</h4>
            <ul className="space-y-2">
              <li>
                <Link 
                  to="/home" 
                  className="text-gray-300 dark:text-gray-400 hover:text-white transition-colors duration-200"
                >
                  Главная
                </Link>
              </li>
              <li>
                <Link 
                  to="/dashboard" 
                  className="text-gray-300 dark:text-gray-400 hover:text-white transition-colors duration-200"
                >
                  Подбор сборки
                </Link>
              </li>
              <li>
                <a 
                  href="#faq" 
                  className="text-gray-300 dark:text-gray-400 hover:text-white transition-colors duration-200"
                >
                  FAQ
                </a>
              </li>
              <li>
                <Link 
                  to="/login" 
                  className="text-gray-300 dark:text-gray-400 hover:text-white transition-colors duration-200"
                >
                  Вход
                </Link>
              </li>
            </ul>
          </div>

          {/* Поддержка */}
          <div>
            <h4 className="text-lg font-semibold mb-4">Поддержка</h4>
            <ul className="space-y-2 text-gray-300 dark:text-gray-400">
              <li className="flex items-start">
                <svg className="w-5 h-5 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M2.003 5.884L10 9.882l7.997-3.998A2 2 0 0016 4H4a2 2 0 00-1.997 1.884z"/>
                  <path d="M18 8.118l-8 4-8-4V14a2 2 0 002 2h12a2 2 0 002-2V8.118z"/>
                </svg>
                <span>support@компьютерок.рф</span>
              </li>
              <li className="flex items-start">
                <svg className="w-5 h-5 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd"/>
                </svg>
                <span>Помощь в подборе</span>
              </li>
              <li className="flex items-start">
                <svg className="w-5 h-5 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M18 13V5a2 2 0 00-2-2H4a2 2 0 00-2 2v8a2 2 0 002 2h3l3 3 3-3h3a2 2 0 002-2zM5 7a1 1 0 011-1h8a1 1 0 110 2H6a1 1 0 01-1-1zm1 3a1 1 0 100 2h3a1 1 0 100-2H6z" clipRule="evenodd"/>
                </svg>
                <span>Онлайн-консультации</span>
              </li>
              <li className="flex items-start">
                <svg className="w-5 h-5 mr-2 mt-0.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M2 3a1 1 0 011-1h2.153a1 1 0 01.986.836l.74 4.435a1 1 0 01-.54 1.06l-1.548.773a11.037 11.037 0 006.105 6.105l.774-1.548a1 1 0 011.059-.54l4.435.74a1 1 0 01.836.986V17a1 1 0 01-1 1h-2C7.82 18 2 12.18 2 5V3z"/>
                </svg>
                <span>8 (800) 555-35-35</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Разделитель */}
        <div className="border-t border-gray-700 dark:border-gray-600 mt-8 pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-gray-400 dark:text-gray-500 text-sm text-center md:text-left">
              © 2025 Компьютер.ок. Умный подбор компьютерных комплектующих. Все права защищены.
            </p>
            <div className="flex flex-wrap justify-center gap-4 md:gap-6 text-sm">
              <Link 
                to="/privacy" 
                className="text-gray-400 dark:text-gray-500 hover:text-white transition-colors duration-200"
              >
                Конфиденциальность
              </Link>
              <Link 
                to="/terms" 
                className="text-gray-400 dark:text-gray-500 hover:text-white transition-colors duration-200"
              >
                Условия использования
              </Link>
              <Link 
                to="/about" 
                className="text-gray-400 dark:text-gray-500 hover:text-white transition-colors duration-200"
              >
                О проекте
              </Link>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
