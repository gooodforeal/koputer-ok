// Типы для сборок

export interface BuildAuthor {
  id: number;
  name: string;
  picture: string | null;
}

export interface Component {
  id: number;
  name: string;
  link: string;
  price: number | null;
  image: string | null;
  category: string;
  created_at: string;
  updated_at: string | null;
}

export interface Build {
  id: number;
  title: string;
  description: string;
  component_ids: number[];
  components: Component[];
  additional_info?: string | null;
  author_id: number;
  author: BuildAuthor | null;
  views_count: number;
  average_rating: number;
  ratings_count: number;
  total_price: number;
  created_at: string;
  updated_at: string | null;
}

export interface BuildCreate {
  title: string;
  description: string;
  component_ids?: number[];
  additional_info?: string | null;
}

export interface BuildUpdate {
  title?: string;
  description?: string;
  component_ids?: number[];
  additional_info?: string | null;
}

export interface BuildListResponse {
  builds: Build[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export interface BuildTopResponse {
  builds: Build[];
  total: number;
}

// Типы для оценок
export interface BuildRating {
  id: number;
  build_id: number;
  user_id: number;
  score: number;
  created_at: string;
  updated_at: string | null;
}

export interface BuildRatingCreate {
  score: number;
}

export interface BuildRatingUpdate {
  score: number;
}

// Типы для комментариев
export interface BuildCommentUser {
  id: number;
  name: string;
  picture: string | null;
}

export interface BuildComment {
  id: number;
  build_id: number;
  user_id: number;
  user: BuildCommentUser | null;
  content: string;
  parent_id: number | null;
  created_at: string;
  updated_at: string | null;
  replies?: BuildComment[];
}

export interface BuildCommentCreate {
  content: string;
  parent_id?: number | null;
}

export interface BuildCommentUpdate {
  content: string;
}

export interface BuildCommentListResponse {
  comments: BuildComment[];
  total: number;
}

// Типы для статистики
export interface BuildStats {
  total_builds: number;
  total_ratings: number;
  total_comments: number;
  average_rating: number;
}

// Типы для уникальных компонентов (сгруппированных по категориям)
export interface BuildComponents {
  components_by_category: {
    [category: string]: Component[];
  };
}


