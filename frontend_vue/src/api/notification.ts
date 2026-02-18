/**
 * 通知消息 API 服务
 */

import { api } from './client'
import type { Notification, NotificationsListResponse, PaginationParams } from '../types'

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
 * 通知列表结果
 */
interface NotificationsResult {
  notifications: Notification[]
  unread_count: number
}

/**
 * 获取通知列表
 */
export const getNotifications = async (
  params?: PaginationParams
): Promise<{ notifications: Notification[]; unread_count: number }> => {
  const response = await api.get<DjangoPaginatedResponse<NotificationsResult>>('/notifications/', {
    params,
  })
  const result = response.data.results
  return {
    notifications: result?.notifications ?? [],
    unread_count: result?.unread_count ?? 0,
  }
}

/**
 * 标记通知为已读
 */
export const markAsRead = async (id: number): Promise<{ notification: Notification }> => {
  const response = await api.patch<{ notification: Notification }>(`/notifications/${id}/`, {
    is_read: true,
  })
  return response.data
}

/**
 * 全部标记已读
 */
export const markAllAsRead = async (): Promise<{ updated_count: number }> => {
  const response = await api.post<{ updated_count: number }>('/notifications/read-all/')
  return response.data
}
