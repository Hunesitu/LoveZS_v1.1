<!--
Dashboard 页面
显示最近日记、恋爱天数与快速入口
-->
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useDiaries } from '@/composables/useDiaries'
import { resolveMediaUrl, isVideo } from '@/utils/media'
import { BookOpen, Heart, Calendar, Plus } from 'lucide-vue-next'
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'

import type { Photo } from '@/types'

dayjs.locale('zh-cn')

const { diaries, isLoading, loadDiaries, totalCount } = useDiaries()

// 相恋纪念日（硬编码）
const LOVE_ANNIVERSARY = '2023-09-09'

const loveDays = ref<number>(0)
const nextMilestone = ref<{ target: number; remaining: number } | null>(null)

// 计算恋爱天数（当天算第1天）
const calculateLoveDays = () => {
  const anniversary = dayjs(LOVE_ANNIVERSARY).startOf('day')
  const today = dayjs().startOf('day')
  return today.diff(anniversary, 'day') + 1  // +1 因为当天算第1天
}

// 计算下一个整百天
const calculateNextMilestone = (currentDays: number) => {
  const nextHundred = Math.ceil(currentDays / 100) * 100
  return {
    target: nextHundred,
    remaining: nextHundred - currentDays
  }
}

const diaryCount = totalCount  // 使用后端返回的真实总数

const loadDashboardData = async () => {
  try {
    await loadDiaries({ page_size: 6 })

    // 计算恋爱天数
    const days = calculateLoveDays()
    loveDays.value = days

    // 计算下一个整百天
    nextMilestone.value = calculateNextMilestone(days)
  } catch (error) {
    console.error('Failed to load dashboard data:', error)
  }
}

const getCoverMediaUrl = (media?: Photo | null) =>
  resolveMediaUrl(media?.preview_url || media?.thumbnail_url || media?.url || '')

const getMoodEmoji = (mood: string) => {
  const moodEmojis: Record<string, string> = {
    happy: '😊',
    sad: '😩',
    excited: '🤩',
    calm: '😌',
    angry: '😧',
    tired: '😾',
    loved: '😍',
    grateful: '🙏',
  }
  return moodEmojis[mood] || '😊'
}

const stripMarkdown = (content: string, maxLength = 120) => {
  return content
    .replace(/[#*`_\[\]]/g, '')
    .substring(0, maxLength)
}

onMounted(() => {
  loadDashboardData()
})
</script>

<template>
  <div class="dashboard">
    <div class="welcome-section">
      <h1 class="welcome-title">欢迎回来 💞</h1>
      <p class="welcome-date">
        今天是 {{ dayjs().format('YYYY年M月D日') }}，记录美好时光
      </p>
    </div>

    <div class="stats-grid">
      <div class="stat-card stat-card-pink">
        <div class="stat-content">
          <div class="stat-info">
            <p class="stat-label">日记总数</p>
            <p class="stat-value">{{ diaryCount }}</p>
          </div>
          <BookOpen :size="40" class="stat-icon" />
        </div>
      </div>

      <div class="stat-card stat-card-purple">
        <div class="stat-content">
          <div class="stat-info">
            <p class="stat-label">恋爱天数</p>
            <p class="stat-value">{{ loveDays }}</p>
          </div>
          <Heart :size="40" class="stat-icon" />
        </div>
      </div>

      <div class="stat-card stat-card-amber">
        <div class="stat-content">
          <div class="stat-info">
            <p class="stat-label">下一个整百天</p>
            <p class="stat-value" v-if="nextMilestone">
              {{ nextMilestone.remaining }}天
            </p>
            <p class="stat-subtitle" v-if="nextMilestone">
              距离 {{ nextMilestone.target }} 天
            </p>
          </div>
          <Calendar :size="40" class="stat-icon" />
        </div>
      </div>
    </div>

    <div class="card quick-actions">
      <h2 class="section-title">快速操作</h2>
      <div class="actions-grid">
        <RouterLink to="/diaries/new" class="action-card action-card-pink">
          <div class="action-icon action-icon-pink">
            <Plus :size="20" />
          </div>
          <div class="action-text">
            <p class="action-title">写日记</p>
            <p class="action-subtitle">记录今天</p>
          </div>
        </RouterLink>

        <RouterLink to="/diaries" class="action-card action-card-purple">
          <div class="action-icon action-icon-purple">
            <BookOpen :size="20" />
          </div>
          <div class="action-text">
            <p class="action-title">看日记</p>
            <p class="action-subtitle">浏览记录</p>
          </div>
        </RouterLink>

        <RouterLink to="/countdowns" class="action-card action-card-amber">
          <div class="action-icon action-icon-amber">
            <Calendar :size="20" />
          </div>
          <div class="action-text">
            <p class="action-title">重要日</p>
            <p class="action-subtitle">重要日子</p>
          </div>
        </RouterLink>
      </div>
    </div>

    <div class="card recent-diaries">
      <div class="section-header">
        <h2 class="section-title">最近日记</h2>
        <RouterLink to="/diaries" class="view-all-link">
          查看全部 →
        </RouterLink>
      </div>

      <div v-if="isLoading" class="loading-container">
        <div class="spinner"></div>
      </div>

      <div v-else-if="diaries.length > 0" class="diary-grid">
        <RouterLink
          v-for="diary in diaries"
          :key="diary.id"
          :to="`/diaries/${diary.id}`"
          class="diary-card"
        >
          <!-- 封面图 -->
          <div v-if="diary.cover_media" class="card-cover">
            <template v-if="isVideo(diary.cover_media)">
              <div class="cover-image cover-video-placeholder" />
              <span class="video-badge">▶</span>
            </template>
            <template v-else>
              <img
                :src="getCoverMediaUrl(diary.cover_media)"
                :alt="diary.cover_media.original_name"
                class="cover-image"
                loading="lazy"
                decoding="async"
              />
            </template>
          </div>
          <!-- 文字区 -->
          <div class="card-body">
            <div class="card-title-row">
              <span class="diary-mood">{{ getMoodEmoji(diary.mood) }}</span>
              <h3 class="diary-title">
                <span v-if="!diary.is_public" class="private-badge">🔒</span>
                {{ diary.title }}
              </h3>
            </div>
            <p class="diary-preview">{{ stripMarkdown(diary.content) }}...</p>
            <div class="card-footer">
              <span class="category-badge">{{ diary.category }}</span>
              <span class="diary-date">
                {{ dayjs(diary.date).format('M月D日') }}
                <template v-if="diary.created_by_details"> · {{ diary.created_by_details.username }}</template>
              </span>
            </div>
          </div>
        </RouterLink>
      </div>

      <div v-else class="empty-state">
        <div class="empty-icon">📝</div>
        <h3 class="empty-title">还没有日记</h3>
        <p class="empty-text">开始记录美好时光吧</p>
        <RouterLink to="/diaries/new" class="btn-primary">
          <Plus :size="16" class="mr-1" />
          写第一篇日记
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard {
  width: 100%;
}

.welcome-section {
  margin-bottom: 1.5rem;
  padding: 1.5rem;
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-lg);
  background: linear-gradient(130deg, #fff3f8 0%, #ffeaf3 50%, #fff7fb 100%);
  box-shadow: var(--shadow-soft);
}

.welcome-title {
  margin: 0;
  font-size: 1.75rem;
  font-weight: 700;
  line-height: 1.25;
  color: var(--text-primary);
}

.welcome-date {
  margin: 0.5rem 0 0;
  color: var(--text-secondary);
}

.stats-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  border-radius: var(--radius-lg);
  padding: 1.25rem;
  color: #fff;
  box-shadow: var(--shadow-soft);
  transition: transform var(--dur-fast), box-shadow var(--dur-base);
}

.stat-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-hover);
}

.stat-card-pink {
  background: linear-gradient(135deg, #f58fb2 0%, #f47194 100%);
}

.stat-card-purple {
  background: linear-gradient(135deg, #9b8cff 0%, #7c6ef6 100%);
}

.stat-card-amber {
  background: linear-gradient(135deg, #f6b85c 0%, #f19f3e 100%);
}

.stat-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stat-label {
  margin: 0;
  opacity: 0.92;
  font-size: 0.875rem;
}

.stat-value {
  margin: 0.2rem 0 0;
  font-size: 2rem;
  font-weight: 700;
  line-height: 1;
}

.stat-subtitle {
  margin: 0.2rem 0 0;
  opacity: 0.82;
  font-size: 0.875rem;
}

.stat-icon {
  opacity: 0.82;
}

.card {
  background: var(--bg-elevated);
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-soft);
  padding: 1rem;
  margin-bottom: 1.5rem;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.section-title {
  margin: 0;
  font-size: 1.05rem;
  color: var(--text-primary);
}

.view-all-link {
  color: var(--pink-500);
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 600;
}

.actions-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.75rem;
}

.action-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.8rem;
  border-radius: var(--radius-md);
  border: 1px solid var(--border-soft);
  background: #fff;
  text-decoration: none;
  color: inherit;
  transition: transform var(--dur-fast), box-shadow var(--dur-base), border-color var(--dur-base);
}

.action-card:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-soft);
  border-color: var(--border-strong);
}

.action-icon {
  width: 2.2rem;
  height: 2.2rem;
  border-radius: 0.75rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.action-icon-pink {
  background: #ffe8f1;
  color: #d65a88;
}

.action-icon-purple {
  background: #ece9ff;
  color: #786be8;
}

.action-icon-amber {
  background: #fff1dd;
  color: #c88228;
}

.action-title {
  margin: 0;
  font-size: 0.95rem;
  color: var(--text-primary);
}

.action-subtitle {
  margin: 0.15rem 0 0;
  font-size: 0.8rem;
  color: var(--text-secondary);
}

.loading-container {
  min-height: 160px;
  display: grid;
  place-items: center;
}

.spinner {
  width: 2rem;
  height: 2rem;
  border: 2px solid #f4dbe7;
  border-top-color: var(--pink-500);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.diary-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

.diary-card {
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-lg);
  background: #fff;
  text-decoration: none;
  color: inherit;
  overflow: hidden;
  transition: transform var(--dur-fast), box-shadow var(--dur-base), border-color var(--dur-base);
}

.diary-card:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 24px rgba(217, 117, 154, 0.15);
  border-color: var(--border-strong);
}

.card-cover {
  width: 100%;
  overflow: hidden;
  position: relative;
}

.cover-image {
  width: 100%;
  aspect-ratio: 16 / 9;
  object-fit: cover;
  display: block;
}

.cover-video-placeholder {
  background: linear-gradient(135deg, #f7d7df 0%, #dbeafe 100%);
}

.video-badge {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 2.2rem;
  height: 2.2rem;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.card-body {
  padding: 0.85rem;
}

.card-title-row {
  display: flex;
  align-items: center;
  gap: 0.45rem;
}

.diary-mood {
  font-size: 1.15rem;
  flex-shrink: 0;
}

.diary-title {
  margin: 0;
  font-size: 0.95rem;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.private-badge {
  margin-right: 0.25rem;
  font-size: 0.85rem;
}

.diary-preview {
  margin: 0.4rem 0 0;
  color: var(--text-secondary);
  font-size: 0.84rem;
  line-height: 1.55;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 0.6rem;
  gap: 0.5rem;
}

.category-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.2rem 0.5rem;
  border-radius: 9999px;
  font-size: 0.72rem;
  font-weight: 600;
  background: #ffeaf3;
  color: #a55674;
  flex-shrink: 0;
}

.diary-date {
  color: #a38998;
  font-size: 0.75rem;
  white-space: nowrap;
}

.empty-state {
  text-align: center;
  padding: 2rem 1rem;
}

.empty-icon {
  font-size: 2.1rem;
}

.empty-title {
  margin: 0.5rem 0 0;
  color: var(--text-primary);
}

.empty-text {
  margin: 0.35rem 0 1rem;
  color: var(--text-secondary);
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.62rem 1.2rem;
  border: none;
  border-radius: var(--radius-sm);
  background: linear-gradient(135deg, var(--pink-500) 0%, var(--rose-500) 100%);
  color: #fff;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  box-shadow: 0 8px 16px rgba(217, 117, 154, 0.26);
  transition: transform var(--dur-fast), box-shadow var(--dur-base), filter var(--dur-base);
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 12px 22px rgba(217, 117, 154, 0.32);
  filter: brightness(1.02);
}

.mr-1 {
  margin-right: 0.35rem;
}

@media (min-width: 768px) {
  .stats-grid {
    grid-template-columns: repeat(3, 1fr);
  }

  .actions-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }

  .diary-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
