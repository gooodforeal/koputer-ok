// Feedback types and constants

export const FeedbackTypeValues = {
  BUG: 'BUG',
  FEATURE: 'FEATURE',
  IMPROVEMENT: 'IMPROVEMENT',
  GENERAL: 'GENERAL'
} as const;

export type FeedbackType = typeof FeedbackTypeValues[keyof typeof FeedbackTypeValues];

export const FeedbackStatusValues = {
  NEW: 'NEW',
  IN_REVIEW: 'IN_REVIEW',
  IN_PROGRESS: 'IN_PROGRESS',
  RESOLVED: 'RESOLVED',
  REJECTED: 'REJECTED'
} as const;

export type FeedbackStatus = typeof FeedbackStatusValues[keyof typeof FeedbackStatusValues];

export type FeedbackUserInfo = {
  id: number;
  name: string;
  email: string;
  picture?: string;
}

export type FeedbackCreate = {
  title: string;
  description: string;
  type: FeedbackType;
  rating?: number;
}

export type FeedbackUpdate = {
  title?: string;
  description?: string;
  type?: FeedbackType;
  rating?: number;
}

export type FeedbackAdminUpdate = {
  status?: FeedbackStatus;
  assigned_to_id?: number;
  admin_response?: string;
}

export type Feedback = {
  id: number;
  title: string;
  description: string;
  type: FeedbackType;
  status: FeedbackStatus;
  rating?: number;
  user_id: number;
  assigned_to_id?: number;
  admin_response?: string;
  created_at: string;
  updated_at?: string;
  user: FeedbackUserInfo;
  assigned_to?: FeedbackUserInfo;
}

export type FeedbackListResponse = {
  feedbacks: Feedback[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export type FeedbackStats = {
  total: number;
  new: number;
  in_review: number;
  in_progress: number;
  resolved: number;
  rejected: number;
  by_type: Record<string, number>;
  average_rating?: number;
}

