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

// 基础类型
export * from './ingestion'
export * from './extraction'

// 图相关类型
export * from './graph'

// 查询相关类型
// 注意：避免与graph.ts中的类型冲突
export type { SearchRecord, SavedQuery, QueryResult, NLQueryResponse } from './query'

// 可视化相关类型
// 注意：避免与graph.ts中的类型冲突
export type { LayoutMode, GraphFilters, FetchOptions, CentralityResult, CentralityAnalysisResponse, GraphStats } from './visualization'
