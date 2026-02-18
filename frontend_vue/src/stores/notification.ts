/**
 * Pinia 状态管理 - Notification Store
 * 管理通知消息状态
 */

import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { Notification } from '@/types'
import { getNotifications, markAsRead, markAllAsRead } from '@/api/notification'

export const useNotificationStore = defineStore('notification', () => {
  // 状态
  const notifications = ref<Notification[]>([])
  const unreadCount = ref(0)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const hasUnread = computed(() => unreadCount.value > 0)

  /**
   * 获取通知列表
   */
  const fetchNotifications = async (params?: { page?: number; page_size?: number }) => {
    isLoading.value = true
    error.value = null

    try {
      const result = await getNotifications(params)
      notifications.value = result.notifications
      unreadCount.value = result.unread_count
    } catch (err: any) {
      error.value = err.response?.data?.message || '获取通知失败'
      console.error('获取通知失败:', err)
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 标记单条通知为已读
   */
  const markNotificationAsRead = async (id: number) => {
    try {
      await markAsRead(id)
      // 更新本地状态
      const notification = notifications.value.find(n => n.id === id)
      if (notification) {
        notification.is_read = true
        if (unreadCount.value > 0) {
          unreadCount.value--
        }
      }
    } catch (err: any) {
      error.value = err.response?.data?.message || '标记已读失败'
      console.error('标记已读失败:', err)
    }
  }

  /**
   * 全部标记已读
   */
  const markAllNotificationsAsRead = async () => {
    try {
      await markAllAsRead()
      // 更新本地状态
      notifications.value.forEach(n => {
        n.is_read = true
      })
      unreadCount.value = 0
    } catch (err: any) {
      error.value = err.response?.data?.message || '标记全部已读失败'
      console.error('标记全部已读失败:', err)
    }
  }

  /**
   * 清除错误
   */
  const clearError = () => {
    error.value = null
  }

  return {
    // 状态
    notifications,
    unreadCount,
    isLoading,
    error,

    // 计算属性
    hasUnread,

    // 方法
    fetchNotifications,
    markNotificationAsRead,
    markAllNotificationsAsRead,
    clearError,
  }
})
