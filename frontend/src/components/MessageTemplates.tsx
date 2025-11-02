import React, { useState, useCallback, useMemo } from 'react';

interface MessageTemplatesProps {
  onSelectTemplate: (template: string) => void;
  disabled?: boolean;
}

const MessageTemplates: React.FC<MessageTemplatesProps> = React.memo(({ onSelectTemplate, disabled = false }) => {
  const [isOpen, setIsOpen] = useState(false);

  const templates = useMemo(() => [
    {
      category: 'Приветствие',
      templates: [
        'Здравствуйте! Спасибо за обращение. Чем могу помочь?',
        'Добро пожаловать! Я готов ответить на ваши вопросы.',
        'Привет! Рад видеть вас здесь. Как дела?'
      ]
    },
    {
      category: 'Техническая поддержка',
      templates: [
        'Понял вашу проблему. Давайте разберемся пошагово.',
        'Спасибо за подробное описание. Сейчас проверю это.',
        'Это известная проблема. У нас есть решение для этого случая.',
        'Попробуйте выполнить следующие действия: 1) Перезагрузите страницу 2) Очистите кэш браузера'
      ]
    },
    {
      category: 'Решение проблем',
      templates: [
        'Проблема решена! Проверьте, пожалуйста.',
        'Я исправил эту ошибку. Попробуйте снова.',
        'Обновите страницу - изменения должны вступить в силу.',
        'Проблема была на нашей стороне. Извините за неудобства.'
      ]
    },
    {
      category: 'Завершение',
      templates: [
        'Проблема решена. Есть ли еще вопросы?',
        'Рад был помочь! Обращайтесь, если что-то еще понадобится.',
        'Все готово! Удачного дня!',
        'Если возникнут дополнительные вопросы, я всегда готов помочь.'
      ]
    },
    {
      category: 'Информационные',
      templates: [
        'К сожалению, эта функция пока недоступна.',
        'Мы работаем над улучшением этого функционала.',
        'Спасибо за предложение! Передам его команде разработки.',
        'Этот вопрос требует дополнительного изучения. Я свяжусь с вами позже.'
      ]
    }
  ], []);

  const handleTemplateSelect = useCallback((template: string) => {
    onSelectTemplate(template);
    setIsOpen(false);
  }, [onSelectTemplate]);

  const toggleOpen = useCallback(() => {
    setIsOpen(prev => !prev);
  }, []);

  const closeDropdown = useCallback(() => {
    setIsOpen(false);
  }, []);

  return (
    <div className="relative">
      <button
        onClick={toggleOpen}
        disabled={disabled}
        className="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center gap-2"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        Шаблоны
        <svg className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute bottom-full left-0 mb-2 w-96 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 z-50 max-h-96 overflow-y-auto">
          <div className="p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900 dark:text-white">Шаблоны ответов</h3>
              <button
                onClick={closeDropdown}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="space-y-4">
              {templates.map((category, categoryIndex) => (
                <div key={categoryIndex}>
                  <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2 px-2">
                    {category.category}
                  </h4>
                  <div className="space-y-1">
                    {category.templates.map((template, templateIndex) => (
                      <button
                        key={templateIndex}
                        onClick={() => handleTemplateSelect(template)}
                        className="w-full text-left p-3 text-sm text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-700 rounded-lg transition-colors"
                      >
                        {template}
                      </button>
                    ))}
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
              <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
                Выберите шаблон для быстрой вставки
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
});

MessageTemplates.displayName = 'MessageTemplates';

export default MessageTemplates;
