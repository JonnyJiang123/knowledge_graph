export interface User {
  id: string;
  username: string;
  email: string;
  password: string;
  created_at: Date;
  updated_at: Date;
}

export interface UserCreate {
  username: string;
  email: string;
  password: string;
}

export interface UserResponse {
  id: string;
  username: string;
  email: string;
  created_at: Date;
  updated_at: Date;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  user: UserResponse;
}