/**
 * 认证相关 API
 *
 * 注意：client.ts 的响应拦截器会自动解包 { success: true, data: ... } 格式，
 * 所以这里 response.data 已经是内层 data 的内容。
 * 认证接口需要原始响应（包含 success 字段），因此使用独立的 axios 实例。
 */

import axios from 'axios'
import type {
  ApiResponse,
  AuthResponse,
  LoginRequest,
  RegisterRequest,
  User
} from '@/types'

const API_BASE_URL = import.meta.env.VITE_API_URL || '/api'

// 认证专用 axios 实例（不经过响应拦截器解包）
const authApi = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
  timeout: 30000,
})

/**
 * 用户注册
 */
export async function register(data: RegisterRequest): Promise<ApiResponse<AuthResponse>> {
  const response = await authApi.post<ApiResponse<AuthResponse>>('/auth/register/', data)
  return response.data
}

/**
 * 用户登录
 */
export async function login(data: LoginRequest): Promise<ApiResponse<AuthResponse>> {
  const response = await authApi.post<ApiResponse<AuthResponse>>('/auth/login/', data)
  return response.data
}

/**
 * 用户登出
 */
export async function logout(): Promise<ApiResponse> {
  const token = localStorage.getItem('lovezs_token')
  const response = await authApi.post<ApiResponse>('/auth/logout/', {
    refresh: localStorage.getItem('lovezs_refresh_token')
  }, {
    headers: token ? { Authorization: `Bearer ${token}` } : {}
  })
  return response.data
}

/**
 * 获取当前用户信息
 */
export async function getProfile(): Promise<ApiResponse<{ user: User }>> {
  const token = localStorage.getItem('lovezs_token')
  const response = await authApi.get<ApiResponse<{ user: User }>>('/auth/profile/', {
    headers: token ? { Authorization: `Bearer ${token}` } : {}
  })
  return response.data
}

/**
 * 更新当前用户信息
 */
export async function updateProfile(data: Partial<User>): Promise<ApiResponse<{ user: User }>> {
  const token = localStorage.getItem('lovezs_token')
  const response = await authApi.put<ApiResponse<{ user: User }>>('/auth/profile/', data, {
    headers: token ? { Authorization: `Bearer ${token}` } : {}
  })
  return response.data
}

/**
 * 修改密码
 */
export async function changePassword(oldPassword: string, newPassword: string): Promise<ApiResponse> {
  const token = localStorage.getItem('lovezs_token')
  const response = await authApi.post<ApiResponse>('/auth/change-password/', {
    old_password: oldPassword,
    new_password: newPassword
  }, {
    headers: token ? { Authorization: `Bearer ${token}` } : {}
  })
  return response.data
}
