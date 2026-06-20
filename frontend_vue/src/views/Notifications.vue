<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Bell, Check, CheckCheck, MessageCircle } from 'lucide-vue-next'
import dayjs from 'dayjs'
import relativeTime from 'dayjs/plugin/relativeTime'
import 'dayjs/locale/zh-cn'
import { useNotificationStore } from '@/stores/notification'
import type { Notification } from '@/types'

dayjs.locale('zh-cn')
dayjs.extend(relativeTime)

const router = useRouter()
const notificationStore = useNotificationStore()

onMounted(() => {
  notificationStore.fetchNotifications()
})

const handleNotificationClick = async (notification: Notification) => {
  if (!notification.is_read) {
    await notificationStore.markNotificationAsRead(notification.id)
  }
  if (notification.diary) {
    router.push(`/diaries/${notification.diary}`)
  }
}

const handleMarkAllAsRead = async () => {
  await notificationStore.markAllNotificationsAsRead()
}
</script>

<template>
  <div class="notifications-page page-narrow">
    <div class="page-header">
      <div>
        <p class="romance-kicker">Backstage Messages</p>
        <h1 class="page-title">
          <Bell :size="24" class="title-icon" />
          消息通知
        </h1>
        <p class="page-subtitle">每一条互动，都是片尾仍然亮着的灯。</p>
      </div>
      <button v-if="notificationStore.unreadCount > 0" class="btn-secondary" type="button" @click="handleMarkAllAsRead">
        <CheckCheck :size="16" />
        全部已读
      </button>
    </div>

    <div v-if="notificationStore.isLoading" class="loading-container glass-card">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <div v-else-if="notificationStore.notifications.length === 0" class="empty-state-card">
      <div class="empty-state">
        <Bell :size="46" />
        <p>暂无消息通知</p>
        <p>安静也很好，说明今晚的银幕正在等下一句留言。</p>
      </div>
    </div>

    <div v-else class="notifications-list">
      <article
        v-for="notification in notificationStore.notifications"
        :key="notification.id"
        class="notification-item cinematic-card"
        :class="{ unread: !notification.is_read }"
        @click="handleNotificationClick(notification)"
      >
        <div class="notification-icon">
          <MessageCircle :size="20" />
        </div>
        <div class="notification-content">
          <div class="notification-header">
            <strong>{{ notification.title }}</strong>
            <span v-if="!notification.is_read" class="unread-dot"></span>
          </div>
          <p>{{ notification.content }}</p>
          <div class="notification-meta">
            <span>{{ notification.from_user_details?.username || '未知用户' }}</span>
            <span>{{ dayjs(notification.created_at).fromNow() }}</span>
          </div>
        </div>
        <Check v-if="notification.is_read" :size="15" class="read-indicator" />
      </article>
    </div>
  </div>
</template>

<style scoped>
.notifications-list {
  display: grid;
  gap: 0.75rem;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  gap: 0.9rem;
  padding: 1rem;
  cursor: pointer;
  transition: transform var(--dur-base) ease, border-color var(--dur-base) ease;
}

.notification-item:hover {
  transform: translateY(-2px);
}

.notification-item.unread {
  border-color: rgba(255, 143, 200, 0.3);
  background:
    linear-gradient(135deg, rgba(55, 28, 63, 0.92), rgba(20, 17, 37, 0.9)),
    radial-gradient(circle at 95% 5%, rgba(240, 120, 182, 0.22), transparent 40%);
}

.notification-icon {
  display: grid;
  flex: 0 0 auto;
  width: 40px;
  height: 40px;
  place-items: center;
  border-radius: 50%;
  color: var(--rose-bright);
  background: rgba(240, 120, 182, 0.15);
}

.notification-content {
  min-width: 0;
  flex: 1;
}

.notification-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--ink);
}

.unread-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--rose-bright);
  box-shadow: 0 0 10px rgba(255, 143, 200, 0.6);
}

.notification-content p {
  display: -webkit-box;
  margin: 0.25rem 0 0.45rem;
  overflow: hidden;
  color: var(--ink-soft);
  font-size: 0.9rem;
  line-height: 1.55;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.notification-meta {
  display: flex;
  gap: 0.75rem;
  color: var(--ink-muted);
  font-size: 0.76rem;
}

.read-indicator {
  color: var(--ink-muted);
}

.empty-state-card {
  padding: 1rem;
}

.empty-state {
  gap: 0.65rem;
}

.empty-state svg {
  color: var(--rose-bright);
}
</style>
