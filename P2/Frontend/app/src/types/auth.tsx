export type RoleName = "ADMIN" | "CLIENTE";

export interface RegistroSchema {
  first_name: string;
  last_name: string;
  email: string;
  password: string;
  password_confirmation: string;
}

export interface LoginSchema {
  email: string;
  password: string;
}

export interface AuthenticatedUser {
  id: string;
  first_name: string;
  last_name: string;
  email: string;
  role: RoleName;
}

export interface AuthSchema {
  message: string;
  user: AuthenticatedUser;
}

export interface ApiError {
  error?: {
    code?: string;
    message?: string;
  };

  detail?: string | Array<{
    msg: string;
  }>;
}