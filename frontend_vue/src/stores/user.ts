/**
 * Pinia 状态管理 - User Store
 * 管理用户认证状态和 token
 */

import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { User, TokenResponse } from '@/types'

const TOKEN_KEY = 'lovezs_token'
const REFRESH_TOKEN_KEY = 'lovezs_refresh_token'
const USER_KEY = 'lovezs_user'

export const useUserStore = defineStore('user', () => {
  // 状态
  const token = ref<string | null>(localStorage.getItem(TOKEN_KEY))
  const refreshToken = ref<string | null>(localStorage.getItem(REFRESH_TOKEN_KEY))
  const user = ref<User | null>(null)

  // 从 localStorage 加载用户信息
  try {
    const savedUser = localStorage.getItem(USER_KEY)
    if (savedUser) {
      user.value = JSON.parse(savedUser)
    }
  } catch {
    localStorage.removeItem(USER_KEY)
  }

  // 计算属性
  const isAuthenticated = computed(() => !!token.value && !!user.value)
  const username = computed(() => user.value?.username || '')
  const email = computed(() => user.value?.email || '')
  const isAdmin = computed(() => !!user.value?.is_staff)

  /**
   * 保存认证信息到状态和 localStorage
   */
  const setAuth = (authToken: TokenResponse, authUser: User) => {
    token.value = authToken.access
    refreshToken.value = authToken.refresh
    user.value = authUser

    localStorage.setItem(TOKEN_KEY, authToken.access)
    localStorage.setItem(REFRESH_TOKEN_KEY, authToken.refresh)
    localStorage.setItem(USER_KEY, JSON.stringify(authUser))
  }

  /**
   * 更新 token
   */
  const updateToken = (authToken: TokenResponse) => {
    token.value = authToken.access
    refreshToken.value = authToken.refresh
    localStorage.setItem(TOKEN_KEY, authToken.access)
    localStorage.setItem(REFRESH_TOKEN_KEY, authToken.refresh)
  }

  /**
   * 更新用户信息
   */
  const updateUser = (authUser: User) => {
    user.value = authUser
    localStorage.setItem(USER_KEY, JSON.stringify(authUser))
  }

  /**
   * 清除认证信息
   */
  const clearAuth = () => {
    token.value = null
    refreshToken.value = null
    user.value = null

    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
    localStorage.removeItem(USER_KEY)
  }

  /**
   * 登录
   */
  const login = (authToken: TokenResponse, authUser: User) => {
    setAuth(authToken, authUser)
  }

  /**
   * 登出
   */
  const logout = () => {
    clearAuth()
  }

  /**
   * 检查 token 是否需要刷新
   * 解析 JWT 获取过期时间
   */
  const shouldRefreshToken = (): boolean => {
    if (!token.value) return false

    try {
      const payload = parseJwt(token.value)
      const exp = payload.exp * 1000 // 转换为毫秒
      const now = Date.now()
      // 如果在 5 分钟内过期，则需要刷新
      return exp - now < 5 * 60 * 1000
    } catch {
      return false
    }
  }

  /**
   * 解析 JWT token
   */
  function parseJwt(token: string) {
    const base64Url = token.split('.')[1]
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/')
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map(c => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    )
    return JSON.parse(jsonPayload)
  }

  return {
    // 状态
    token,
    refreshToken,
    user,

    // 计算属性
    isAuthenticated,
    username,
    email,
    isAdmin,

    // 方法
    setAuth,
    updateToken,
    updateUser,
    clearAuth,
    login,
    logout,
    shouldRefreshToken,
  }
})
