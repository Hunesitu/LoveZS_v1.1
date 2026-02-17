/**
 * API 客户端配置
 * 使用 axios 进行 HTTP 请求
 */

import axios from 'axios'
import { useUserStore } from '@/stores/user'

// 获取 API 基础 URL
const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

// 创建 axios 实例
export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30秒超时
})

// Token 刷新锁，防止并发刷新
let isRefreshing = false
let refreshSubscribers: Array<(token: string) => void> = []

/**
 * 订阅 token 刷新完成
 */
function subscribeTokenRefresh(callback: (token: string) => void) {
  refreshSubscribers.push(callback)
}

/**
 * 通知所有订阅者 token 刷新完成
 */
function onRefreshed(token: string) {
  refreshSubscribers.forEach(callback => callback(token))
  refreshSubscribers = []
}

/**
 * 尝试刷新 token
 */
async function attemptRefreshToken() {
  const userStore = useUserStore()
  const refreshTokenValue = userStore.refreshToken

  if (!refreshTokenValue) {
    throw new Error('No refresh token available')
  }

  const response = await axios.post(`${API_BASE_URL}/auth/login/`, {
    refresh: refreshTokenValue
  })

  // 更新 store 中的 token
  if (response.data?.data?.token) {
    userStore.updateToken(response.data.data.token)

    // 刷新 token 后同时更新用户信息（确保 is_staff 等最新）
    try {
      const profileResponse = await axios.get(`${API_BASE_URL}/auth/profile/`, {
        headers: { Authorization: `Bearer ${response.data.data.token.access}` }
      })
      if (profileResponse.data?.data?.user) {
        userStore.updateUser(profileResponse.data.data.user)
      }
    } catch (profileError) {
      console.warn('Failed to refresh user info:', profileError)
    }

    return response.data.data.token.access
  }

  throw new Error('Token refresh failed')
}

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 添加 token 到请求头
    const userStore = useUserStore()
    const token = userStore.token
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    const data = response.data
    if (data && typeof data === 'object' && data.success === true && 'data' in data) {
      return { ...response, data: data.data }
    }
    return response
  },
  async (error) => {
    const originalRequest = error.config

    // 处理 401 未授权错误
    if (error.response?.status === 401 && !originalRequest._retry) {
      const userStore = useUserStore()

      // 如果正在刷新 token，将请求加入队列
      if (isRefreshing) {
        return new Promise(resolve => {
          subscribeTokenRefresh((token: string) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            resolve(api(originalRequest))
          })
        })
      }

      // 尝试刷新 token
      if (userStore.refreshToken) {
        isRefreshing = true
        originalRequest._retry = true

        try {
          const newToken = await attemptRefreshToken()
          isRefreshing = false
          onRefreshed(newToken)

          // 重试原请求
          originalRequest.headers.Authorization = `Bearer ${newToken}`
          return api(originalRequest)
        } catch (refreshError) {
          isRefreshing = false
          refreshSubscribers = []

          // 刷新失败，清除认证信息并跳转到登录页
          userStore.logout()
          window.location.href = '/login'
          return Promise.reject(refreshError)
        }
      } else {
        // 没有 refresh token，直接清除认证信息
        userStore.logout()
        window.location.href = '/login'
      }
    }

    // 统一错误处理
    console.error('API Error:', error)

    if (error.response) {
      // 服务器返回错误状态码
      const { status, data } = error.response
      console.error(`API Error ${status}:`, data)
    } else if (error.request) {
      // 请求已发出但没有收到响应
      console.error('Network Error: 请求超时或网络问题')
    } else {
      // 发生了触发错误请求的事情
      console.error('Error:', error.message)
    }

    return Promise.reject(error)
  }
)

export default api
