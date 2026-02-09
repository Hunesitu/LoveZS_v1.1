/**
 * API 客户端配置
 * 使用 axios 进行 HTTP 请求
 */

import axios from 'axios'

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

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 可以在这里添加 token 等认证信息
    // const token = localStorage.getItem('token')
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`
    // }
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
  (error) => {
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
