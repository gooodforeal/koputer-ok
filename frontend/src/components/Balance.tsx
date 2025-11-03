import React, { useState, useEffect } from 'react';
import { balanceApi } from '../services/api';
import type { Balance, Transaction, BalanceStats, PaymentCreate } from '../types/balance';
import { TransactionType, TransactionStatus } from '../types/balance';

const Balance: React.FC = () => {
  const [balance, setBalance] = useState<Balance | null>(null);
  const [stats, setStats] = useState<BalanceStats | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalTransactions, setTotalTransactions] = useState(0);
  const [showPaymentModal, setShowPaymentModal] = useState(false);
  const [paymentAmount, setPaymentAmount] = useState('');
  const [paymentLoading, setPaymentLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, [page]);

  const loadData = async () => {
    try {
      setLoading(true);
      const [balanceData, statsData, transactionsData] = await Promise.all([
        balanceApi.getBalance(),
        balanceApi.getBalanceStats(),
        balanceApi.getTransactions(page, 20)
      ]);
      setBalance(balanceData);
      setStats(statsData);
      setTransactions(transactionsData.transactions);
      setTotalPages(transactionsData.total_pages);
      setTotalTransactions(transactionsData.total);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при загрузке данных');
    } finally {
      setLoading(false);
    }
  };

  const handlePayment = async () => {
    const amount = parseFloat(paymentAmount);
    if (isNaN(amount) || amount < 50) {
      setError('Минимальная сумма пополнения: 50 ₽');
      return;
    }

    try {
      setPaymentLoading(true);
      setError(null);
      
      const paymentData: PaymentCreate = {
        amount: amount.toFixed(2),
        description: 'Пополнение баланса',
        return_url: window.location.origin + '/profile'
      };

      const response = await balanceApi.createPayment(paymentData);
      
      // Перенаправляем на страницу оплаты Юкассы
      window.location.href = response.confirmation_url;
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Ошибка при создании платежа');
      setPaymentLoading(false);
    }
  };

  const formatAmount = (amount: string | number) => {
    const num = typeof amount === 'string' ? parseFloat(amount) : amount;
    return new Intl.NumberFormat('ru-RU', {
      style: 'currency',
      currency: 'RUB',
      minimumFractionDigits: 2
    }).format(num);
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString('ru-RU', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getTransactionTypeLabel = (type: TransactionType) => {
    switch (type) {
      case TransactionType.DEPOSIT:
        return 'Пополнение';
      case TransactionType.WITHDRAWAL:
        return 'Списание';
      case TransactionType.PAYMENT:
        return 'Платеж';
      case TransactionType.REFUND:
        return 'Возврат';
      default:
        return type;
    }
  };

  const getTransactionStatusLabel = (status: TransactionStatus) => {
    switch (status) {
      case TransactionStatus.PENDING:
        return 'Ожидает';
      case TransactionStatus.COMPLETED:
        return 'Завершено';
      case TransactionStatus.FAILED:
        return 'Неудачно';
      case TransactionStatus.CANCELLED:
        return 'Отменено';
      default:
        return status;
    }
  };

  const getTransactionStatusColor = (status: TransactionStatus) => {
    switch (status) {
      case TransactionStatus.COMPLETED:
        return 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200';
      case TransactionStatus.PENDING:
        return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200';
      case TransactionStatus.FAILED:
        return 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200';
      case TransactionStatus.CANCELLED:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
      default:
        return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
    }
  };

  const getTransactionTypeColor = (type: TransactionType) => {
    switch (type) {
      case TransactionType.DEPOSIT:
        return 'text-green-600 dark:text-green-400';
      case TransactionType.WITHDRAWAL:
        return 'text-red-600 dark:text-red-400';
      case TransactionType.PAYMENT:
        return 'text-blue-600 dark:text-blue-400';
      case TransactionType.REFUND:
        return 'text-orange-600 dark:text-orange-400';
      default:
        return 'text-gray-600 dark:text-gray-400';
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 dark:border-blue-400"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Balance Card */}
      <div className="bg-gradient-to-r from-blue-600 via-purple-600 to-indigo-600 dark:from-blue-700 dark:via-purple-700 dark:to-indigo-700 rounded-xl shadow-lg p-6 text-white">
        <div className="flex justify-between items-start mb-4">
          <div>
            <p className="text-blue-100 text-sm mb-2">Текущий баланс</p>
            <p className="text-4xl font-bold text-white">
              {balance ? formatAmount(balance.balance) : '0,00 ₽'}
            </p>
          </div>
          <button
            onClick={() => setShowPaymentModal(true)}
            className="bg-white text-blue-600 hover:bg-blue-50 dark:bg-gray-800 dark:text-blue-400 dark:hover:bg-gray-700 px-4 py-2 rounded-lg font-medium transition-colors duration-200 flex items-center space-x-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
            </svg>
            <span>Пополнить</span>
          </button>
        </div>
      </div>

      {/* Stats Cards */}
      {stats && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4 border border-gray-200 dark:border-gray-700">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Всего пополнено</p>
            <p className="text-xl font-semibold text-green-600 dark:text-green-400">
              {formatAmount(stats.total_deposited)}
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4 border border-gray-200 dark:border-gray-700">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Всего потрачено</p>
            <p className="text-xl font-semibold text-red-600 dark:text-red-400">
              {formatAmount(stats.total_spent)}
            </p>
          </div>
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-4 border border-gray-200 dark:border-gray-700">
            <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">Транзакций</p>
            <p className="text-xl font-semibold text-gray-900 dark:text-white">
              {stats.transactions_count}
            </p>
          </div>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="bg-red-100 dark:bg-red-900 border border-red-400 text-red-700 dark:text-red-300 px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Transactions List */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6 border border-gray-200 dark:border-gray-700">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">История транзакций</h3>
        
        {transactions.length === 0 ? (
          <div className="text-center py-8 text-gray-500 dark:text-gray-400">
            <svg className="w-16 h-16 mx-auto mb-4 text-gray-300 dark:text-gray-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            <p>Нет транзакций</p>
          </div>
        ) : (
          <>
            <div className="space-y-3">
              {transactions.map((transaction) => (
                <div
                  key={transaction.id}
                  className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600"
                >
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-1">
                      <span className={`font-medium ${getTransactionTypeColor(transaction.transaction_type)}`}>
                        {getTransactionTypeLabel(transaction.transaction_type)}
                      </span>
                      <span className={`text-xs px-2 py-1 rounded-full ${getTransactionStatusColor(transaction.status)}`}>
                        {getTransactionStatusLabel(transaction.status)}
                      </span>
                    </div>
                    {transaction.description && (
                      <p className="text-sm text-gray-600 dark:text-gray-400">{transaction.description}</p>
                    )}
                    <p className="text-xs text-gray-500 dark:text-gray-500 mt-1">
                      {formatDate(transaction.created_at)}
                    </p>
                  </div>
                  <div className={`text-lg font-semibold ${
                    transaction.transaction_type === TransactionType.DEPOSIT || transaction.transaction_type === TransactionType.REFUND
                      ? 'text-green-600 dark:text-green-400'
                      : 'text-red-600 dark:text-red-400'
                  }`}>
                    {transaction.transaction_type === TransactionType.DEPOSIT || transaction.transaction_type === TransactionType.REFUND ? '+' : '-'}
                    {formatAmount(transaction.amount)}
                  </div>
                </div>
              ))}
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="mt-8 flex flex-col sm:flex-row justify-center items-center gap-4">
                {/* Информация о странице */}
                <div className="text-sm text-gray-600 dark:text-gray-400">
                  Страница <span className="font-semibold text-gray-900 dark:text-white">{page}</span> из <span className="font-semibold text-gray-900 dark:text-white">{totalPages}</span>
                  <span className="ml-2 text-gray-500 dark:text-gray-500">
                    ({totalTransactions} транзакций)
                  </span>
                </div>

                {/* Навигация */}
                <div className="flex items-center gap-1">
                  {/* Кнопка "В начало" */}
                  <button
                    onClick={() => {
                      setPage(1);
                      window.scrollTo({ top: 0, behavior: 'smooth' });
                    }}
                    disabled={page === 1}
                    className="px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    title="В начало"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 19l-7-7 7-7m8 14l-7-7 7-7" />
                    </svg>
                  </button>

                  {/* Кнопка "Предыдущая" */}
                  <button
                    onClick={() => {
                      setPage(page - 1);
                      window.scrollTo({ top: 0, behavior: 'smooth' });
                    }}
                    disabled={page === 1}
                    className="px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    title="Предыдущая страница"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
                    </svg>
                  </button>

                  {/* Номера страниц */}
                  <div className="flex items-center gap-1 flex-wrap justify-center">
                    {(() => {
                      const pages: (number | string)[] = [];
                      const maxVisible = 7;
                      
                      if (totalPages <= maxVisible) {
                        // Показываем все страницы, если их немного
                        for (let i = 1; i <= totalPages; i++) {
                          pages.push(i);
                        }
                      } else {
                        // Всегда показываем первую страницу
                        pages.push(1);
                        
                        if (page <= 4) {
                          // Близко к началу: показываем первые страницы
                          for (let i = 2; i <= 5; i++) {
                            pages.push(i);
                          }
                          pages.push('...');
                          pages.push(totalPages);
                        } else if (page >= totalPages - 3) {
                          // Близко к концу: показываем последние страницы
                          pages.push('...');
                          for (let i = totalPages - 4; i <= totalPages; i++) {
                            pages.push(i);
                          }
                        } else {
                          // В середине: показываем текущую и соседние
                          pages.push('...');
                          for (let i = page - 1; i <= page + 1; i++) {
                            pages.push(i);
                          }
                          pages.push('...');
                          pages.push(totalPages);
                        }
                      }
                      
                      return pages.map((item, index) => {
                        if (item === '...') {
                          return (
                            <span key={`ellipsis-${index}`} className="px-2 text-gray-500 dark:text-gray-400">
                              ...
                            </span>
                          );
                        }
                        
                        const pageNumber = item as number;
                        return (
                          <button
                            key={pageNumber}
                            onClick={() => {
                              setPage(pageNumber);
                              window.scrollTo({ top: 0, behavior: 'smooth' });
                            }}
                            className={`min-w-[2.5rem] px-3 py-2 rounded-lg font-medium transition-colors ${
                              page === pageNumber
                                ? 'bg-blue-600 text-white shadow-md hover:bg-blue-700'
                                : 'bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700'
                            }`}
                          >
                            {pageNumber}
                          </button>
                        );
                      });
                    })()}
                  </div>

                  {/* Кнопка "Следующая" */}
                  <button
                    onClick={() => {
                      setPage(page + 1);
                      window.scrollTo({ top: 0, behavior: 'smooth' });
                    }}
                    disabled={page === totalPages}
                    className="px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    title="Следующая страница"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                    </svg>
                  </button>

                  {/* Кнопка "В конец" */}
                  <button
                    onClick={() => {
                      setPage(totalPages);
                      window.scrollTo({ top: 0, behavior: 'smooth' });
                    }}
                    disabled={page === totalPages}
                    className="px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                    title="В конец"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 5l7 7-7 7M5 5l7 7-7 7" />
                    </svg>
                  </button>
                </div>
              </div>
            )}
          </>
        )}
      </div>

      {/* Payment Modal */}
      {showPaymentModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-xl shadow-xl p-6 max-w-md w-full mx-4">
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">Пополнение баланса</h3>
            
            {error && (
              <div className="mb-4 bg-red-100 dark:bg-red-900 border border-red-400 text-red-700 dark:text-red-300 px-4 py-3 rounded-lg text-sm">
                {error}
              </div>
            )}

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Сумма пополнения (₽)
              </label>
              <input
                type="number"
                min="50"
                step="0.01"
                value={paymentAmount}
                onChange={(e) => setPaymentAmount(e.target.value)}
                placeholder="1000.00"
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
              <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Минимальная сумма: 50 ₽
              </p>
            </div>

            <div className="flex space-x-3">
              <button
                onClick={() => {
                  setShowPaymentModal(false);
                  setPaymentAmount('');
                  setError(null);
                }}
                disabled={paymentLoading}
                className="flex-1 px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors disabled:opacity-50"
              >
                Отмена
              </button>
              <button
                onClick={handlePayment}
                disabled={paymentLoading || !paymentAmount}
                className="flex-1 px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              >
                {paymentLoading ? (
                  <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                ) : (
                  'Перейти к оплате'
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Balance;

