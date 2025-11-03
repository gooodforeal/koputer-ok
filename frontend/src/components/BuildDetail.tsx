import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { buildsApi } from '../services/api';
import { useAuth } from '../contexts/AuthContext';
import type { Build, BuildRating, BuildComment, BuildCommentCreate } from '../types/build';

const BuildDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { user } = useAuth();
  
  const [build, setBuild] = useState<Build | null>(null);
  const [comments, setComments] = useState<BuildComment[]>([]);
  const [myRating, setMyRating] = useState<BuildRating | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [newComment, setNewComment] = useState('');
  const [replyToId, setReplyToId] = useState<number | null>(null);
  const [editingCommentId, setEditingCommentId] = useState<number | null>(null);
  const [editingContent, setEditingContent] = useState('');
  const [openMenuId, setOpenMenuId] = useState<number | null>(null);
  const [buildMenuOpen, setBuildMenuOpen] = useState(false);
  const [exportingPdf, setExportingPdf] = useState(false);

  const buildId = parseInt(id || '0');

  useEffect(() => {
    if (buildId) {
      fetchBuild();
      fetchComments();
      if (user) {
        fetchMyRating();
      }
    }
  }, [buildId, user]);

  const fetchBuild = async () => {
    try {
      setLoading(true);
      const data = await buildsApi.getBuild(buildId);
      setBuild(data);
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при загрузке сборки');
    } finally {
      setLoading(false);
    }
  };

  const fetchComments = async () => {
    try {
      const data = await buildsApi.getComments(buildId);
      setComments(data.comments);
    } catch (err) {
      console.error('Ошибка при загрузке комментариев:', err);
    }
  };

  const fetchMyRating = async () => {
    try {
      const rating = await buildsApi.getMyRating(buildId);
      setMyRating(rating);
    } catch (err) {
      // Нет оценки - это нормально
      setMyRating(null);
    }
  };

  const handleRating = async (score: number) => {
    if (!user) {
      alert('Войдите, чтобы оценить сборку');
      return;
    }

    try {
      if (myRating) {
        await buildsApi.updateRating(buildId, { score });
      } else {
        await buildsApi.createRating(buildId, { score });
      }
      await fetchBuild();
      await fetchMyRating();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка при оценке сборки');
    }
  };

  const handleSubmitComment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!user) {
      alert('Войдите, чтобы оставить комментарий');
      return;
    }
    if (!newComment.trim()) return;

    try {
      const commentData: BuildCommentCreate = {
        content: newComment,
        parent_id: replyToId
      };
      await buildsApi.createComment(buildId, commentData);
      setNewComment('');
      setReplyToId(null);
      setOpenMenuId(null);
      await fetchComments();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка при создании комментария');
    }
  };

  const handleEditComment = async (commentId: number) => {
    if (!editingContent.trim()) return;

    try {
      await buildsApi.updateComment(buildId, commentId, { content: editingContent });
      setEditingCommentId(null);
      setEditingContent('');
      setOpenMenuId(null);
      await fetchComments();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка при обновлении комментария');
    }
  };

  const handleDeleteComment = async (commentId: number) => {
    if (!confirm('Вы уверены, что хотите удалить комментарий?')) return;

    try {
      await buildsApi.deleteComment(buildId, commentId);
      setOpenMenuId(null);
      await fetchComments();
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка при удалении комментария');
    }
  };

  const handleDeleteBuild = async () => {
    if (!confirm('Вы уверены, что хотите удалить эту сборку?')) return;

    try {
      await buildsApi.deleteBuild(buildId);
      navigate('/builds');
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка при удалении сборки');
    }
  };

  const handleExportPdf = async () => {
    try {
      setExportingPdf(true);
      const blob = await buildsApi.exportPdf(buildId);
      
      // Функция для транслитерации русских символов
      const transliterate = (text: string): string => {
        const translitMap: { [key: string]: string } = {
          'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
          'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
          'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
          'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
          'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
          'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
          'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
          'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
          'Ф': 'F', 'Х': 'H', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Sch',
          'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
        };
        
        return text
          .split('')
          .map(char => translitMap[char] || (char.match(/[\w\s\-_\.]/) ? char : '_'))
          .join('')
          .replace(/\s+/g, '_')
          .replace(/_+/g, '_')
          .replace(/^_|_$/g, '')
          .substring(0, 80);
      };
      
      // Создаем безопасное имя файла
      const safeTitle = build?.title ? transliterate(build.title) : 'build';
      const filename = `build_${buildId}_${safeTitle}.pdf`;
      
      // Создаем ссылку для скачивания
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      alert(err.response?.data?.detail || 'Ошибка при экспорте PDF');
    } finally {
      setExportingPdf(false);
    }
  };

  const renderStars = (rating: number, interactive = false) => {
    const stars = [];
    for (let i = 1; i <= 5; i++) {
      const isFilled = i <= rating;
      stars.push(
        <button
          key={i}
          onClick={() => interactive && handleRating(i)}
          disabled={!interactive}
          className={`text-2xl ${isFilled ? 'text-yellow-400' : 'text-gray-300'} ${interactive ? 'hover:text-yellow-500 cursor-pointer' : ''}`}
        >
          ★
        </button>
      );
    }
    return <div className="flex gap-1">{stars}</div>;
  };

  const renderComment = (comment: BuildComment, depth = 0) => {
    const isEditing = editingCommentId === comment.id;
    const isOwner = user?.id === comment.user_id;
    const isMenuOpen = openMenuId === comment.id;
    const hasActions = (user && depth === 0) || isOwner;

    return (
      <div key={comment.id} className={`${depth > 0 ? 'ml-8 mt-4' : 'mt-4'}`}>
        <div className={`bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 p-5 shadow-sm hover:shadow-md transition-all duration-200 relative ${
          depth > 0 ? 'border-l-4 border-l-blue-400 dark:border-l-blue-500' : ''
        }`}>
          <div className="flex items-start gap-3 mb-3">
            {comment.user?.picture ? (
              <img
                src={comment.user.picture}
                alt={comment.user.name}
                className="w-10 h-10 rounded-full ring-2 ring-gray-200 dark:ring-gray-600 flex-shrink-0"
              />
            ) : (
              <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-semibold text-sm ring-2 ring-gray-200 dark:ring-gray-600 flex-shrink-0">
                {comment.user?.name?.charAt(0)?.toUpperCase() || '?'}
              </div>
            )}
            <div className="flex-1 min-w-0">
              <div className="flex items-center gap-2 mb-1 flex-wrap">
                <span className="font-semibold text-gray-900 dark:text-white">
                  {comment.user?.name || 'Неизвестный'}
                </span>
                <span className="text-xs text-gray-500 dark:text-gray-400">
                  {new Date(comment.created_at).toLocaleString('ru-RU', {
                    day: 'numeric',
                    month: 'short',
                    year: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </span>
                {depth > 0 && (
                  <span className="px-2 py-0.5 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs rounded-full font-medium">
                    Ответ
                  </span>
                )}
              </div>
            </div>
            
            {hasActions && !isEditing && (
              <div className="relative flex-shrink-0">
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setOpenMenuId(isMenuOpen ? null : comment.id);
                  }}
                  className="p-1.5 rounded-lg text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
                  aria-label="Действия с комментарием"
                >
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
                  </svg>
                </button>

                {isMenuOpen && (
                  <>
                    <div
                      className="fixed inset-0 z-10"
                      onClick={(e) => {
                        e.stopPropagation();
                        setOpenMenuId(null);
                      }}
                    />
                    <div className="absolute right-0 top-8 z-20 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1">
                      {user && depth === 0 && (
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setReplyToId(comment.id);
                            setOpenMenuId(null);
                          }}
                          className="w-full px-4 py-2 text-left text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2 transition-colors"
                        >
                          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6" />
                          </svg>
                          Ответить
                        </button>
                      )}
                      {isOwner && (
                        <>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              setEditingCommentId(comment.id);
                              setEditingContent(comment.content);
                              setOpenMenuId(null);
                            }}
                            className="w-full px-4 py-2 text-left text-sm text-green-600 dark:text-green-400 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2 transition-colors"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                            </svg>
                            Редактировать
                          </button>
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              handleDeleteComment(comment.id);
                              setOpenMenuId(null);
                            }}
                            className="w-full px-4 py-2 text-left text-sm text-red-600 dark:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2 transition-colors"
                          >
                            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                            </svg>
                            Удалить
                          </button>
                        </>
                      )}
                    </div>
                  </>
                )}
              </div>
            )}
          </div>

          {isEditing ? (
            <div className="space-y-3">
              <textarea
                value={editingContent}
                onChange={(e) => setEditingContent(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-700 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all break-words resize-y overflow-x-hidden"
                rows={4}
                placeholder="Введите текст комментария..."
              />
              <div className="flex gap-2">
                <button
                  onClick={() => handleEditComment(comment.id)}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium shadow-sm hover:shadow-md"
                >
                  Сохранить
                </button>
                <button
                  onClick={() => {
                    setEditingCommentId(null);
                    setEditingContent('');
                    setOpenMenuId(null);
                  }}
                  className="px-4 py-2 bg-gray-200 dark:bg-gray-600 text-gray-700 dark:text-gray-200 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-500 transition-colors font-medium"
                >
                  Отмена
                </button>
              </div>
            </div>
          ) : (
            <p className="text-gray-700 dark:text-gray-300 leading-relaxed whitespace-pre-wrap break-words">
              {comment.content}
            </p>
          )}
        </div>

        {comment.replies && depth < 1 && (
          <div className="ml-4 mt-3 space-y-2 border-l-2 border-gray-200 dark:border-gray-700 pl-4">
            {comment.replies.map((reply) => renderComment(reply, depth + 1))}
          </div>
        )}
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error || !build) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 p-4 rounded-lg">
          {error || 'Сборка не найдена'}
        </div>
        <Link 
          to="/builds" 
          className="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors font-medium shadow-sm hover:shadow-md"
        >
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          Вернуться к списку
        </Link>
      </div>
    );
  }

  const isOwner = user?.id === build.author_id;

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
        <div className="flex justify-between items-start mb-4">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white break-words overflow-hidden">{build.title}</h1>
          {/* Меню троеточия - доступно всем */}
          <div className="relative">
            <button
              onClick={(e) => {
                e.stopPropagation();
                setBuildMenuOpen(!buildMenuOpen);
              }}
              className="p-1.5 rounded-lg text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
              aria-label="Действия со сборкой"
            >
              <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                <path d="M10 6a2 2 0 110-4 2 2 0 010 4zM10 12a2 2 0 110-4 2 2 0 010 4zM10 18a2 2 0 110-4 2 2 0 010 4z" />
              </svg>
            </button>

            {buildMenuOpen && (
              <>
                <div
                  className="fixed inset-0 z-10"
                  onClick={(e) => {
                    e.stopPropagation();
                    setBuildMenuOpen(false);
                  }}
                />
                <div className="absolute right-0 top-8 z-20 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1">
                  {/* Кнопка экспорта PDF - доступна всем */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleExportPdf();
                      setBuildMenuOpen(false);
                    }}
                    disabled={exportingPdf}
                    className="w-full px-4 py-2 text-left text-sm text-blue-600 dark:text-blue-400 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {exportingPdf ? (
                      <>
                        <svg className="animate-spin h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        <span>Экспорт...</span>
                      </>
                    ) : (
                      <>
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
                        </svg>
                        Экспорт в PDF
                      </>
                    )}
                  </button>
                  {/* Дополнительные действия только для автора */}
                  {isOwner && (
                    <>
                      <Link
                        to={`/builds/${build.id}/edit`}
                        onClick={(e) => {
                          e.stopPropagation();
                          setBuildMenuOpen(false);
                        }}
                        className="w-full px-4 py-2 text-left text-sm text-green-600 dark:text-green-400 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2 transition-colors"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                        </svg>
                        Редактировать
                      </Link>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          handleDeleteBuild();
                          setBuildMenuOpen(false);
                        }}
                        className="w-full px-4 py-2 text-left text-sm text-red-600 dark:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-700 flex items-center gap-2 transition-colors"
                      >
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                        </svg>
                        Удалить
                      </button>
                    </>
                  )}
                </div>
              </>
            )}
          </div>
        </div>

        <div className="flex items-center gap-3 mb-6">
          {build.author?.picture && (
            <img
              src={build.author.picture}
              alt={build.author.name}
              className="w-12 h-12 rounded-full"
            />
          )}
          <div>
            <div className="font-medium text-gray-900 dark:text-white">
              {build.author?.name || 'Неизвестный автор'}
            </div>
            <div className="text-sm text-gray-500">
              {new Date(build.created_at).toLocaleString('ru-RU')}
            </div>
          </div>
        </div>

        <p className="text-gray-700 dark:text-gray-300 mb-6 break-words overflow-x-hidden whitespace-pre-wrap">{build.description}</p>

        {/* Компоненты сборки */}
        <div className="mb-8 space-y-4">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
            Комплектующие:
          </h2>
          {build.components && build.components.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {build.components.map((component) => {
                // Определяем название категории для отображения
                const categoryNames: { [key: string]: string } = {
                  'PROCESSORY': 'Процессор (CPU)',
                  'VIDEOKARTY': 'Видеокарта (GPU)',
                  'MATERINSKIE_PLATY': 'Материнская плата',
                  'OPERATIVNAYA_PAMYAT': 'Оперативная память (RAM)',
                  'ZHESTKIE_DISKI': 'Накопитель (HDD)',
                  'SSD_NAKOPITELI': 'Накопитель (SSD)',
                  'BLOKI_PITANIYA': 'Блок питания (PSU)',
                  'KORPUSA': 'Корпус',
                  'OHLAZHDENIE': 'Охлаждение',
                };

                return (
                  <div
                    key={component.id}
                    className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-start gap-4">
                      {component.image ? (
                        <img
                          src={component.image}
                          alt={component.name}
                          className="w-20 h-20 object-contain flex-shrink-0 rounded border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-800 p-2"
                          onError={(e) => {
                            (e.target as HTMLImageElement).style.display = 'none';
                          }}
                        />
                      ) : (
                        <div className="w-20 h-20 flex-shrink-0 rounded border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-800 flex items-center justify-center p-2">
                          <svg className="w-10 h-10 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                          </svg>
                        </div>
                      )}
                      <div className="flex-1 min-w-0">
                        <div className="text-sm text-gray-500 dark:text-gray-400 mb-1">
                          {categoryNames[component.category] || component.category}
                        </div>
                        <div className="font-medium text-gray-900 dark:text-white break-words overflow-hidden mb-2">
                          {component.name}
                        </div>
                        <div className="flex items-center justify-between">
                          {component.price && (
                            <div className="text-sm font-semibold text-blue-600 dark:text-blue-400">
                              {component.price.toLocaleString('ru-RU')} ₽
                            </div>
                          )}
                          <a
                            href={component.link}
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
                    </div>
                  </div>
                );
              })}
            </div>
          ) : (
            <div className="text-gray-500 dark:text-gray-400 italic">
              Комплектующие не указаны
            </div>
          )}

          {build.additional_info && (
            <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4 mt-4">
              <div className="text-sm text-gray-500 dark:text-gray-400 mb-1">Дополнительная информация</div>
              <div className="text-gray-900 dark:text-white whitespace-pre-wrap break-words overflow-x-hidden">
                {build.additional_info}
              </div>
            </div>
          )}

          {/* Итоговая цена сборки */}
          {build.total_price > 0 && (
            <div className="mt-4 p-4 bg-gradient-to-r from-green-50 to-blue-50 dark:from-green-900/20 dark:to-blue-900/20 rounded-lg border border-green-200 dark:border-green-800">
              <div className="flex items-center justify-between">
                <div className="text-sm text-gray-600 dark:text-gray-400 font-medium">
                  Итоговая стоимость сборки:
                </div>
                <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                  {build.total_price.toLocaleString('ru-RU')} ₽
                </div>
              </div>
            </div>
          )}
        </div>

        <div className="flex items-center gap-6 border-t border-gray-200 dark:border-gray-700 pt-6">
          <div>
            <div className="text-sm text-gray-500 mb-1">Средний рейтинг</div>
            {renderStars(Math.round(build.average_rating))}
            <div className="text-sm text-gray-500 mt-1">
              {build.average_rating.toFixed(1)} ({build.ratings_count} оценок)
            </div>
          </div>
          <div className="text-sm text-gray-500">
            <div>Просмотров: {build.views_count}</div>
          </div>
        </div>

        {user && !isOwner && (
          <div className="border-t border-gray-200 dark:border-gray-700 pt-6 mt-6">
            <div className="text-sm text-gray-500 mb-2">Ваша оценка:</div>
            {renderStars(myRating?.score || 0, true)}
          </div>
        )}
      </div>

      {/* Комментарии */}
      <div className="mt-8 bg-white dark:bg-gray-800 rounded-xl shadow-lg border border-gray-200 dark:border-gray-700 p-8">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-500 rounded-lg flex items-center justify-center">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
            </svg>
          </div>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
            Комментарии <span className="text-lg font-normal text-gray-500 dark:text-gray-400">({comments.length})</span>
          </h2>
        </div>

        {user && (
          <form onSubmit={handleSubmitComment} className="mb-8">
            <div className="bg-gray-50 dark:bg-gray-700/50 rounded-xl p-5 border border-gray-200 dark:border-gray-600">
              {replyToId && (
                <div className="mb-3 px-3 py-2 bg-blue-100 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800 rounded-lg flex items-center justify-between">
                  <span className="text-sm text-blue-700 dark:text-blue-300 font-medium">
                    Ответ на комментарий
                  </span>
                  <button
                    type="button"
                    onClick={() => setReplyToId(null)}
                    className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 font-medium transition-colors"
                  >
                    Отменить
                  </button>
                </div>
              )}
              <div className="flex items-start gap-3 mb-3">
                {user.picture ? (
                  <img
                    src={user.picture}
                    alt={user.name}
                    className="w-10 h-10 rounded-full ring-2 ring-gray-200 dark:ring-gray-600 flex-shrink-0"
                  />
                ) : (
                  <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center text-white font-semibold text-sm ring-2 ring-gray-200 dark:ring-gray-600 flex-shrink-0">
                    {user.name?.charAt(0)?.toUpperCase() || '?'}
                  </div>
                )}
                <textarea
                  value={newComment}
                  onChange={(e) => setNewComment(e.target.value)}
                  placeholder="Напишите комментарий..."
                  className="flex-1 px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg dark:bg-gray-800 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all resize-none break-words overflow-x-hidden"
                  rows={4}
                />
              </div>
              <div className="flex justify-end">
                <button
                  type="submit"
                  className="px-6 py-2.5 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all font-medium shadow-sm hover:shadow-md disabled:opacity-50 disabled:cursor-not-allowed"
                  disabled={!newComment.trim()}
                >
                  Отправить комментарий
                </button>
              </div>
            </div>
          </form>
        )}

        {!user && (
          <div className="mb-8 p-5 bg-gradient-to-r from-gray-50 to-gray-100 dark:from-gray-700/50 dark:to-gray-700 border border-gray-200 dark:border-gray-600 rounded-xl flex items-center gap-3">
            <svg className="w-5 h-5 text-gray-500 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
            <span className="text-gray-600 dark:text-gray-300 font-medium">
              Войдите, чтобы оставить комментарий
            </span>
          </div>
        )}

        <div className="space-y-4">
          {comments.length === 0 ? (
            <div className="text-center py-12">
              <div className="w-16 h-16 mx-auto mb-4 bg-gray-100 dark:bg-gray-700 rounded-full flex items-center justify-center">
                <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
              </div>
              <p className="text-gray-500 dark:text-gray-400 font-medium">Комментариев пока нет</p>
              <p className="text-sm text-gray-400 dark:text-gray-500 mt-1">Будьте первым, кто оставит комментарий!</p>
            </div>
          ) : (
            comments.map((comment) => renderComment(comment))
          )}
        </div>
      </div>
    </div>
  );
};

export default BuildDetail;


