import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { User, LoginRequest, RegisterRequest } from '@/types'
import { authApi } from '@/api/auth'

// 认证 Store
export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(localStorage.getItem('access_token'))

  const isAuthenticated = computed(() => !!token.value)
  const isSuperuser = computed(() => user.value?.is_superuser ?? false)

  // 注册
  async function register(data: RegisterRequest): Promise<User> {
    const newUser = await authApi.register(data)
    return newUser
  }

  // 登录
  async function login(data: LoginRequest): Promise<void> {
    const response = await authApi.login(data)
    token.value = response.access_token
    localStorage.setItem('access_token', response.access_token)
    await fetchUser()
  }

  // 获取用户信息
  async function fetchUser(): Promise<void> {
    if (!token.value) return
    try {
      user.value = await authApi.getMe()
    } catch {
      logout()
    }
  }

  // 登出
  function logout(): void {
    user.value = null
    token.value = null
    localStorage.removeItem('access_token')
  }

  return {
    user,
    token,
    isAuthenticated,
    isSuperuser,
    register,
    login,
    fetchUser,
    logout,
  }
})
