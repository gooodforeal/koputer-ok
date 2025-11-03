export const TransactionType = {
  DEPOSIT: "DEPOSIT",
  WITHDRAWAL: "WITHDRAWAL",
  PAYMENT: "PAYMENT",
  REFUND: "REFUND"
} as const;

export type TransactionType = typeof TransactionType[keyof typeof TransactionType];

export const TransactionStatus = {
  PENDING: "PENDING",
  COMPLETED: "COMPLETED",
  FAILED: "FAILED",
  CANCELLED: "CANCELLED"
} as const;

export type TransactionStatus = typeof TransactionStatus[keyof typeof TransactionStatus];

export interface Balance {
  id: number;
  user_id: number;
  balance: string;
  created_at: string;
  updated_at?: string;
}

export interface Transaction {
  id: number;
  balance_id: number;
  user_id: number;
  amount: string;
  transaction_type: TransactionType;
  status: TransactionStatus;
  payment_id?: string;
  payment_method?: string;
  description?: string;
  metadata_json?: string;
  created_at: string;
  updated_at?: string;
}

export interface TransactionListResponse {
  transactions: Transaction[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface PaymentCreate {
  amount: string;
  description?: string;
  return_url?: string;
}

export interface PaymentResponse {
  payment_id: string;
  confirmation_url: string;
  amount: string;
  status: string;
}

export interface BalanceStats {
  current_balance: string;
  total_deposited: string;
  total_withdrawn: string;
  total_spent: string;
  transactions_count: number;
}

export interface PaymentStatus {
  payment_id: string;
  status: string;
  paid: boolean;
  cancelled: boolean;
  transaction_status: string;
  amount: number;
}

