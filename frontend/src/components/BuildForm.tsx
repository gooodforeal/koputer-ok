import React, { useEffect, useState, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { buildsApi, componentsApi } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import type { BuildCreate, BuildUpdate, Component } from '../types/build';

// Маппинг категорий компонентов
const CATEGORY_MAP: { [key: string]: string } = {
  cpu: 'PROCESSORY',
  gpu: 'VIDEOKARTY',
  motherboard: 'MATERINSKIE_PLATY',
  ram: 'OPERATIVNAYA_PAMYAT',
  storage: 'SSD_NAKOPITELI', // Будет использоваться для HDD и SSD
  psu: 'BLOKI_PITANIYA',
  case: 'KORPUSA',
  cooling: 'OHLAZHDENIE',
};

const BuildForm: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [selectedComponents, setSelectedComponents] = useState<{ [key: string]: Component | null }>({
    cpu: null,
    gpu: null,
    motherboard: null,
    ram: null,
    storage: null,
    psu: null,
    case: null,
    cooling: null,
  });
  
  const [searchQueries, setSearchQueries] = useState<{ [key: string]: string }>({
    cpu: '',
    gpu: '',
    motherboard: '',
    ram: '',
    storage: '',
    psu: '',
    case: '',
    cooling: '',
  });
  
  const [suggestions, setSuggestions] = useState<{ [key: string]: Component[] }>({
    cpu: [],
    gpu: [],
    motherboard: [],
    ram: [],
    storage: [],
    psu: [],
    case: [],
    cooling: [],
  });
  
  const [additionalInfo, setAdditionalInfo] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const isEdit = !!id;
  const buildId = parseInt(id || '0');

  useEffect(() => {
    if (!user) {
      navigate('/login');
      return;
    }

    if (isEdit) {
      fetchBuild();
    }
  }, [isEdit, buildId, user]);

  const fetchBuild = async () => {
    try {
      setLoading(true);
      const build = await buildsApi.getBuild(buildId);
      
      // Проверяем, что пользователь является автором
      if (build.author_id !== user?.id) {
        setError('У вас нет прав для редактирования этой сборки');
        return;
      }

      setTitle(build.title);
      setDescription(build.description);
      setAdditionalInfo(build.additional_info || '');
      
      // Заполняем выбранные компоненты из сборки
      const selected: { [key: string]: Component | null } = {
        cpu: null,
        gpu: null,
        motherboard: null,
        ram: null,
        storage: null,
        psu: null,
        case: null,
        cooling: null,
      };
      
      build.components.forEach((component) => {
        // Определяем, к какому полю относится компонент
        if (component.category === 'PROCESSORY') {
          selected.cpu = component;
        } else if (component.category === 'VIDEOKARTY') {
          selected.gpu = component;
        } else if (component.category === 'MATERINSKIE_PLATY') {
          selected.motherboard = component;
        } else if (component.category === 'OPERATIVNAYA_PAMYAT') {
          selected.ram = component;
        } else if (component.category === 'SSD_NAKOPITELI' || component.category === 'ZHESTKIE_DISKI') {
          selected.storage = component;
        } else if (component.category === 'BLOKI_PITANIYA') {
          selected.psu = component;
        } else if (component.category === 'KORPUSA') {
          selected.case = component;
        } else if (component.category === 'OHLAZHDENIE') {
          selected.cooling = component;
        }
      });
      
      setSelectedComponents(selected);
      
      // Устанавливаем поисковые запросы на названия выбранных компонентов
      Object.keys(selected).forEach((key) => {
        if (selected[key as keyof typeof selected]) {
          setSearchQueries((prev) => ({
            ...prev,
            [key]: selected[key as keyof typeof selected]?.name || '',
          }));
        }
      });
      
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при загрузке сборки');
    } finally {
      setLoading(false);
    }
  };

  // Функция для поиска компонентов с задержкой (debounce)
  const searchComponents = useCallback(
    async (field: string, query: string) => {
      if (query.length < 2) {
        setSuggestions((prev) => ({ ...prev, [field]: [] }));
        return;
      }

      try {
        // Для накопителей используем обе категории
        if (field === 'storage') {
          const [ssdResults, hddResults] = await Promise.all([
            componentsApi.getComponentsByCategory('SSD_NAKOPITELI', query, 0, 50),
            componentsApi.getComponentsByCategory('ZHESTKIE_DISKI', query, 0, 50),
          ]);
          setSuggestions((prev) => ({
            ...prev,
            [field]: [...ssdResults, ...hddResults],
          }));
        } else {
          const category = CATEGORY_MAP[field];
          if (category) {
            const results = await componentsApi.getComponentsByCategory(category, query, 0, 50);
            setSuggestions((prev) => ({ ...prev, [field]: results }));
          }
        }
      } catch (err) {
        console.error(`Ошибка при поиске компонентов для ${field}:`, err);
      }
    },
    []
  );

  // Debounce функция для поиска
  useEffect(() => {
    const timers: { [key: string]: number } = {};
    
    Object.keys(searchQueries).forEach((field) => {
      const query = searchQueries[field];
      if (timers[field]) {
        clearTimeout(timers[field]);
      }
      
      timers[field] = setTimeout(() => {
        searchComponents(field, query);
      }, 300);
    });

    return () => {
      Object.values(timers).forEach((timer) => clearTimeout(timer));
    };
  }, [searchQueries, searchComponents]);

  const handleInputChange = (field: string, value: string) => {
    setSearchQueries((prev) => ({ ...prev, [field]: value }));
    // Сбрасываем выбранный компонент при изменении текста
    if (selectedComponents[field]?.name !== value) {
      setSelectedComponents((prev) => ({ ...prev, [field]: null }));
    }
  };

  const handleSelectComponent = (field: string, component: Component) => {
    setSelectedComponents((prev) => ({ ...prev, [field]: component }));
    setSearchQueries((prev) => ({ ...prev, [field]: component.name }));
    setSuggestions((prev) => ({ ...prev, [field]: [] }));
  };

  const handleRemoveComponent = (field: string) => {
    setSelectedComponents((prev) => ({ ...prev, [field]: null }));
    setSearchQueries((prev) => ({ ...prev, [field]: '' }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!title.trim() || !description.trim()) {
      setError('Название и описание обязательны для заполнения');
      return;
    }

    if (title.length < 3 || title.length > 200) {
      setError('Название должно быть от 3 до 200 символов');
      return;
    }

    if (description.length < 10 || description.length > 5000) {
      setError('Описание должно быть от 10 до 5000 символов');
      return;
    }

    // Собираем ID всех выбранных компонентов
    const componentIds: number[] = [];
    const componentsWithoutId: string[] = [];
    const missingRequiredFields: string[] = [];
    
    // Обязательные поля для сборки
    const requiredFields = ['cpu', 'gpu', 'motherboard', 'ram', 'psu', 'case', 'cooling'];
    const requiredFieldNames: { [key: string]: string } = {
      cpu: 'Процессор',
      gpu: 'Видеокарта',
      motherboard: 'Материнская плата',
      ram: 'Оперативная память',
      storage: 'Накопитель',
      psu: 'Блок питания',
      case: 'Корпус',
      cooling: 'Охлаждение',
    };
    
    // Проверяем обязательные поля
    requiredFields.forEach((field) => {
      if (!selectedComponents[field]) {
        missingRequiredFields.push(requiredFieldNames[field]);
      }
    });
    
    // Проверяем наличие накопителя (SSD или HDD)
    if (!selectedComponents.storage) {
      missingRequiredFields.push(requiredFieldNames.storage);
    }
    
    // Если отсутствуют обязательные компоненты
    if (missingRequiredFields.length > 0) {
      setError(`Сборка должна содержать все обязательные компоненты. Отсутствуют: ${missingRequiredFields.join(', ')}`);
      return;
    }
    
    Object.entries(selectedComponents).forEach(([field, component]) => {
      if (component) {
        // Проверяем, что компонент имеет валидный ID из базы данных
        if (!component.id || component.id <= 0) {
          componentsWithoutId.push(requiredFieldNames[field] || field);
        } else {
          componentIds.push(component.id);
        }
      }
    });

    // Проверяем, что все выбранные компоненты имеют валидные ID из базы
    if (componentsWithoutId.length > 0) {
      setError(`Невозможно создать сборку: компоненты (${componentsWithoutId.join(', ')}) не выбраны из базы данных. Все компоненты должны быть выбраны из базы данных.`);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      if (isEdit) {
        // При редактировании всегда передаем component_ids для проверки валидности
        const updateData: BuildUpdate = {
          title,
          description,
          component_ids: componentIds,
          additional_info: additionalInfo || undefined,
        };
        await buildsApi.updateBuild(buildId, updateData);
        navigate(`/builds/${buildId}`);
      } else {
        const createData: BuildCreate = {
          title,
          description,
          component_ids: componentIds,
          additional_info: additionalInfo || undefined,
        };
        const newBuild = await buildsApi.createBuild(createData);
        navigate(`/builds/${newBuild.id}`);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при сохранении сборки');
    } finally {
      setLoading(false);
    }
  };

  if (loading && isEdit && !title) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const renderComponentField = (
    field: string,
    label: string,
    placeholder: string
  ) => {
    const selected = selectedComponents[field];
    const query = searchQueries[field];
    const fieldSuggestions = suggestions[field];

    return (
      <div className="relative">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          {label}
        </label>
        <div className="relative">
          <input
            type="text"
            value={query}
            onChange={(e) => handleInputChange(field, e.target.value)}
            onFocus={() => {
              if (query.length >= 2) {
                searchComponents(field, query);
              }
            }}
            className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
            placeholder={placeholder}
          />
          {selected && (
            <button
              type="button"
              onClick={() => handleRemoveComponent(field)}
              className="absolute right-2 top-1/2 -translate-y-1/2 text-red-500 hover:text-red-700"
              title="Удалить компонент"
            >
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          )}
        </div>
        
        {fieldSuggestions.length > 0 && !selected && (
          <div className="absolute z-10 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg max-h-60 overflow-y-auto">
            {fieldSuggestions.map((component) => (
              <button
                key={component.id}
                type="button"
                onClick={() => handleSelectComponent(field, component)}
                className="w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-start gap-3"
              >
                {component.image ? (
                  <img
                    src={component.image}
                    alt={component.name}
                    className="w-12 h-12 object-contain flex-shrink-0 rounded border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-700"
                    onError={(e) => {
                      (e.target as HTMLImageElement).style.display = 'none';
                    }}
                  />
                ) : (
                  <div className="w-12 h-12 flex-shrink-0 rounded border border-gray-200 dark:border-gray-600 bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
                    <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                  </div>
                )}
                <span className="flex-1 min-w-0 text-gray-900 dark:text-white break-words whitespace-normal">{component.name}</span>
                {component.price && (
                  <span className="text-sm text-gray-500 dark:text-gray-400 whitespace-nowrap">
                    {component.price.toLocaleString('ru-RU')} ₽
                  </span>
                )}
              </button>
            ))}
          </div>
        )}
        
        {selected && (
          <div className="mt-2 p-3 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
            <div className="flex items-center justify-between">
              <div className="flex-1 min-w-0">
                <div className="font-medium text-green-900 dark:text-green-200 break-words">{selected.name}</div>
                {selected.price && (
                  <div className="text-sm text-green-700 dark:text-green-300">
                    {selected.price.toLocaleString('ru-RU')} ₽
                  </div>
                )}
              </div>
              <a
                href={selected.link}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center w-8 h-8 text-blue-600 dark:text-blue-400 hover:bg-blue-100 dark:hover:bg-blue-900/30 rounded-lg transition-colors"
                title="Открыть в магазине"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                </svg>
              </a>
            </div>
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="mb-6">
        <Link
          to="/builds"
          className="inline-flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors font-medium shadow-sm hover:shadow-md"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Вернуться к списку
        </Link>
      </div>

      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-8">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-6">
          {isEdit ? 'Редактировать сборку' : 'Создать сборку'}
        </h1>

        {error && (
          <div className="mb-6 p-4 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 rounded-lg">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Название сборки *
            </label>
            <input
              type="text"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white"
              placeholder="Введите название сборки (3-200 символов)"
              maxLength={200}
              required
            />
            <div className="text-sm text-gray-500 mt-1">
              {title.length}/200 символов
            </div>
          </div>

          <div className="mb-6 p-4 bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg">
            <div className="flex items-start gap-2">
              <svg className="w-5 h-5 text-yellow-600 dark:text-yellow-400 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div className="text-sm text-yellow-800 dark:text-yellow-200">
                <strong>Важно:</strong> Все компоненты (отмеченные *) обязательны для заполнения и должны быть выбраны из базы данных. Используйте автодополнение для выбора компонентов. Сборка должна содержать: процессор, видеокарту, материнскую плату, оперативную память, блок питания, корпус, охлаждение и накопитель (SSD или HDD).
              </div>
            </div>
          </div>

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Краткое описание *
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white resize-y"
              placeholder="Введите краткое описание сборки (10-5000 символов)"
              rows={4}
              maxLength={5000}
              required
            />
            <div className="text-sm text-gray-500 mt-1">
              {description.length}/5000 символов
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            {renderComponentField('cpu', 'Процессор (CPU) *', 'Начните вводить название процессора...')}
            {renderComponentField('gpu', 'Видеокарта (GPU) *', 'Начните вводить название видеокарты...')}
            {renderComponentField('motherboard', 'Материнская плата *', 'Начните вводить название материнской платы...')}
            {renderComponentField('ram', 'Оперативная память (RAM) *', 'Начните вводить название ОЗУ...')}
            {renderComponentField('psu', 'Блок питания (PSU) *', 'Начните вводить название БП...')}
            {renderComponentField('case', 'Корпус *', 'Начните вводить название корпуса...')}
            {renderComponentField('cooling', 'Охлаждение *', 'Начните вводить название системы охлаждения...')}
          </div>

          <div className="mb-6">
            {renderComponentField('storage', 'Накопитель (HDD/SSD) *', 'Начните вводить название накопителя (SSD или HDD)...')}
            <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
              Можно выбрать компонент из категорий SSD или HDD. Все поля, отмеченные *, обязательны для заполнения.
            </p>
          </div>

          {/* Итоговая цена сборки */}
          {(() => {
            const totalPrice = Object.values(selectedComponents).reduce((sum, component) => {
              return sum + (component?.price || 0);
            }, 0);
            
            return totalPrice > 0 ? (
              <div className="mb-6 p-4 bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-900/20 dark:to-blue-900/20 rounded-lg border border-green-200 dark:border-green-800">
                <div className="flex items-center justify-between">
                  <div className="text-sm text-gray-600 dark:text-gray-400 font-medium">
                    Итоговая стоимость сборки:
                  </div>
                  <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                    {totalPrice.toLocaleString('ru-RU')} ₽
                  </div>
                </div>
              </div>
            ) : null;
          })()}

          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
              Дополнительная информация
            </label>
            <textarea
              value={additionalInfo}
              onChange={(e) => setAdditionalInfo(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white resize-y"
              placeholder="Любая дополнительная информация о сборке"
              rows={4}
            />
          </div>

          <div className="flex gap-4">
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {loading ? 'Сохранение...' : isEdit ? 'Сохранить изменения' : 'Создать сборку'}
            </button>
            <Link
              to={isEdit ? `/builds/${buildId}` : '/builds'}
              className="px-6 py-2 bg-gray-300 dark:bg-gray-600 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-400 dark:hover:bg-gray-500 transition-colors"
            >
              Отмена
            </Link>
          </div>
        </form>
      </div>

      <div className="mt-6 bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
        <h3 className="font-medium text-blue-900 dark:text-blue-200 mb-2">
          💡 Советы по созданию сборки:
        </h3>
        <ul className="list-disc list-inside space-y-1 text-sm text-blue-800 dark:text-blue-300">
          <li>Дайте сборке понятное и информативное название</li>
          <li>В описании укажите назначение сборки и её основные преимущества</li>
          <li>Укажите все компоненты сборки для полной картины</li>
          <li>Используйте автодополнение - начните вводить название компонента (минимум 2 символа)</li>
          <li>Вы можете выбрать компоненты только из базы данных компонентов</li>
          <li>Для накопителей доступны как SSD, так и HDD</li>
          <li>В дополнительной информации можно указать цены, ссылки и другие детали</li>
        </ul>
      </div>
    </div>
  );
};

export default BuildForm;
