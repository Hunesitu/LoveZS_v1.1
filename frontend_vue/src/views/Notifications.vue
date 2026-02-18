<!--
Notifications 页面
显示用户的消息通知列表
-->
<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useNotificationStore } from '@/stores/notification'
import { Bell, Check, CheckCheck, MessageCircle } from 'lucide-vue-next'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'

dayjs.locale('zh-cn')
dayjs.extend(relativeTime)

const router = useRouter()
const notificationStore = useNotificationStore()

// 加载消息列表
onMounted(() => {
  notificationStore.fetchNotifications()
})

// 点击消息跳转到对应日记
const handleNotificationClick = async (notification: any) => {
  // 标记为已读
  if (!notification.is_read) {
    await notificationStore.markNotificationAsRead(notification.id)
  }

  // 跳转到日记详情页
  if (notification.diary) {
    router.push(`/diaries/${notification.diary}`)
  }
}

// 全部标记已读
const handleMarkAllAsRead = async () => {
  await notificationStore.markAllNotificationsAsRead()
}

// 格式化时间
const formatTime = (time: string) => {
  return dayjs(time).fromNow()
}
</script>

<template>
  <div class="notifications-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-title">
        <Bell :size="24" class="title-icon" />
        <h1>消息通知</h1>
      </div>
      <button
        v-if="notificationStore.unreadCount > 0"
        class="mark-all-btn"
        @click="handleMarkAllAsRead"
      >
        <CheckCheck :size="16" />
        全部已读
      </button>
    </div>

    <!-- 加载状态 -->
    <div v-if="notificationStore.isLoading" class="loading-state">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- 空状态 -->
    <div v-else-if="notificationStore.notifications.length === 0" class="empty-state">
      <Bell :size="48" class="empty-icon" />
      <p>暂无消息通知</p>
    </div>

    <!-- 消息列表 -->
    <div v-else class="notifications-list">
      <div
        v-for="notification in notificationStore.notifications"
        :key="notification.id"
        class="notification-item"
        :class="{ unread: !notification.is_read }"
        @click="handleNotificationClick(notification)"
      >
        <!-- 通知图标 -->
        <div class="notification-icon">
          <MessageCircle :size="20" />
        </div>

        <!-- 通知内容 -->
        <div class="notification-content">
          <div class="notification-header">
            <span class="notification-title">{{ notification.title }}</span>
            <span v-if="!notification.is_read" class="unread-dot"></span>
          </div>
          <p class="notification-content-text">{{ notification.content }}</p>
          <div class="notification-meta">
            <span class="notification-from">
              {{ notification.from_user_details?.username || '未知用户' }}
            </span>
            <span class="notification-time">{{ formatTime(notification.created_at) }}</span>
          </div>
        </div>

        <!-- 已读标记 -->
        <div v-if="notification.is_read" class="read-indicator">
          <Check :size="14" />
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.notifications-page {
  max-width: 800px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.header-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.title-icon {
  color: var(--pink-500);
}

.header-title h1 {
  margin: 0;
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--text-primary);
}

.mark-all-btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.875rem;
  background: var(--pink-50);
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-md);
  color: var(--pink-600);
  font-size: 0.875rem;
  cursor: pointer;
  transition: all var(--dur-fast);
}

.mark-all-btn:hover {
  background: var(--pink-100);
  border-color: var(--pink-300);
}

/* 加载状态 */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: var(--text-secondary);
}

.spinner {
  width: 32px;
  height: 32px;
  border: 3px solid var(--border-soft);
  border-top-color: var(--pink-500);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 0.75rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: var(--text-secondary);
}

.empty-icon {
  color: var(--border-soft);
  margin-bottom: 1rem;
}

/* 消息列表 */
.notifications-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  gap: 0.875rem;
  padding: 1rem;
  background: #fff;
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all var(--dur-fast);
}

.notification-item:hover {
  border-color: var(--pink-300);
  box-shadow: 0 2px 8px rgba(232, 143, 176, 0.12);
}

.notification-item.unread {
  background: linear-gradient(135deg, #fff5f8 0%, #fffafc 100%);
  border-color: var(--pink-200);
}

.notification-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--pink-100);
  border-radius: 50%;
  color: var(--pink-500);
  flex-shrink: 0;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}

.notification-title {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.9375rem;
}

.unread-dot {
  width: 8px;
  height: 8px;
  background: var(--pink-500);
  border-radius: 50%;
  flex-shrink: 0;
}

.notification-content-text {
  margin: 0 0 0.5rem 0;
  font-size: 0.875rem;
  color: var(--text-secondary);
  line-height: 1.5;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.notification-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 0.75rem;
  color: var(--text-tertiary);
}

.notification-from {
  font-weight: 500;
}

.read-indicator {
  color: var(--text-tertiary);
  flex-shrink: 0;
}
</style>
