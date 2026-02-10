// 用户接口
export interface User {
  id: string
  username: string
  email: string
  is_active: boolean
  is_superuser: boolean
}

// 项目接口
export interface Project {
  id: string
  name: string
  description?: string
  industry: 'FINANCE' | 'HEALTHCARE'
  owner_id: string
  created_at?: string
  updated_at?: string
}

// 登录请求
export interface LoginRequest {
  username: string
  password: string
}

// 注册请求
export interface RegisterRequest {
  username: string
  email: string
  password: string
}

// 令牌响应
export interface TokenResponse {
  access_token: string
  token_type: string
}

// 项目创建请求
export interface ProjectCreate {
  name: string
  description?: string
  industry: 'FINANCE' | 'HEALTHCARE'
}

// 项目更新请求
export interface ProjectUpdate {
  name?: string
  description?: string
  industry?: 'FINANCE' | 'HEALTHCARE'
}

// 项目列表响应
export interface ProjectListResponse {
  items: Project[]
  total: number
}
