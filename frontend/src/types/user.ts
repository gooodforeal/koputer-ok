export const UserRole = {
    USER: "USER",
    ADMIN: "ADMIN",
    SUPER_ADMIN: "SUPER_ADMIN"
} as const;

export type UserRole = typeof UserRole[keyof typeof UserRole];

export interface User {
    id: number;
    email?: string;
    name: string;
    picture?: string;
    google_id?: string;
    telegram_id?: string;
    username?: string;
    is_active: boolean;
    role: UserRole;
    created_at: string;
    updated_at?: string;
}

export interface UserUpdate {
    name?: string;
    email?: string;
    picture?: string;
}