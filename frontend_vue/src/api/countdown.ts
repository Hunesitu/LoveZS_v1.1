/**
 * 重要日 API 服务
 * 对应原: frontend/src/services/countdown.ts
 */

import { api } from './client'
import type {
  Countdown,
  CreateCountdownRequest,
} from '../types'

/**
 * Django REST Framework 分页响应
 */
interface DjangoPaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T
}

/**
 * 重要日列表结果
 */
interface CountdownsResult {
  countdowns: Countdown[]
}

/**
 * 获取重要日列表
 */
export const getCountdowns = async (params?: {
  type?: string
  direction?: string
}): Promise<{ countdowns: Countdown[] }> => {
  const response = await api.get<DjangoPaginatedResponse<CountdownsResult>>('/countdowns/', { params })
  return response.data.results || { countdowns: [] }
}

/**
 * 获取单个重要日
 */
export const getCountdown = async (id: number): Promise<{ countdown: Countdown }> => {
  const response = await api.get<{ countdown: Countdown }>(`/countdowns/${id}/`)
  return response.data
}

/**
 * 创建重要日
 */
export const createCountdown = async (data: CreateCountdownRequest): Promise<{ countdown: Countdown }> => {
  const response = await api.post<{ countdown: Countdown }>('/countdowns/', data)
  return response.data
}

/**
 * 更新重要日
 */
export const updateCountdown = async (
  id: number,
  data: Partial<CreateCountdownRequest>
): Promise<{ countdown: Countdown }> => {
  const response = await api.put<{ countdown: Countdown }>(`/countdowns/${id}/`, data)
  return response.data
}

/**
 * 删除重要日
 */
export const deleteCountdown = async (id: number): Promise<void> => {
  await api.delete(`/countdowns/${id}/`)
}

// 默认导出
const countdownService = {
  getCountdowns,
  getCountdown,
  createCountdown,
  updateCountdown,
  deleteCountdown,
}

export default countdownService
