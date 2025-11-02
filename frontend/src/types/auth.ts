import type { User } from './user';

export interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (token: string) => void;
  logout: () => void;
  updateUser: (user: User) => void;
  isLoading: boolean;
}

