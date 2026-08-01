export enum UserRole {
  OWNER = 'OWNER',
  ADMIN = 'ADMIN',
  SUPPORT = 'SUPPORT',
  VIEWER = 'VIEWER'
}

export interface User {
  id: string;
  email: string;
  role: UserRole;
  is_active: boolean;
  organization_id?: string | null;
  last_login_at?: string | null;
  created_at: string;
}

export interface UserCreate {
  email: string;
  password: string;
  role?: UserRole;
  is_active?: boolean;
  organization_id?: string | null;
}

export interface UserUpdate {
  is_active?: boolean;
  role?: UserRole;
  organization_id?: string | null;
  password?: string;
}
