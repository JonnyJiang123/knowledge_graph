import client from './client'
import type { User, LoginRequest, RegisterRequest, TokenResponse } from '@/types'

// 认证 API
export const authApi = {
  // 注册
  async register(data: RegisterRequest): Promise<User> {
    const response = await client.post<User>('/auth/register', data)
    return response.data
  },

  // 登录
  async login(data: LoginRequest): Promise<TokenResponse> {
    const formData = new URLSearchParams()
    formData.append('username', data.username)
    formData.append('password', data.password)

    const response = await client.post<TokenResponse>('/auth/login', formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    })
    return response.data
  },

  // 获取当前用户
  async getMe(): Promise<User> {
    const response = await client.get<User>('/auth/me')
    return response.data
  },
}
