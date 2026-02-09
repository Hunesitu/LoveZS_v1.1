<!--
Dashboard 页面
显示最近日记、恋爱天数与快速入口
-->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useDiaries } from '@/composables/useDiaries'
import { BookOpen, Heart, Calendar, Plus } from 'lucide-vue-next'
import dayjs from 'dayjs'
import 'dayjs/locale/zh-cn'

dayjs.locale('zh-cn')

const { diaries, isLoading, loadDiaries } = useDiaries()

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

const diaryCount = computed(() => diaries.value.length)

const loadDashboardData = async () => {
  try {
    await loadDiaries({ limit: 3 })

    // 计算恋爱天数
    const days = calculateLoveDays()
    loveDays.value = days

    // 计算下一个整百天
    nextMilestone.value = calculateNextMilestone(days)
  } catch (error) {
    console.error('Failed to load dashboard data:', error)
  }
}

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

const stripMarkdown = (content: string, maxLength = 80) => {
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

      <div v-else-if="diaries.length > 0" class="diary-list">
        <RouterLink
          v-for="diary in diaries"
          :key="diary.id"
          :to="`/diaries/${diary.id}`"
          class="diary-item"
        >
          <div class="diary-content">
            <span class="diary-mood">{{ getMoodEmoji(diary.mood) }}</span>
            <div class="diary-info">
              <h3 class="diary-title">{{ diary.title }}</h3>
              <p class="diary-preview">{{ stripMarkdown(diary.content) }}...</p>
              <p class="diary-date">{{ dayjs(diary.date).format('YYYY-MM-DD') }}</p>
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

.diary-list {
  display: flex;
  flex-direction: column;
  gap: 0.55rem;
}

.diary-item {
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-md);
  background: #fff;
  text-decoration: none;
  color: inherit;
  transition: transform var(--dur-fast), box-shadow var(--dur-base), border-color var(--dur-base);
}

.diary-item:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-soft);
  border-color: var(--border-strong);
}

.diary-content {
  display: flex;
  gap: 0.65rem;
  align-items: flex-start;
  padding: 0.75rem;
}

.diary-mood {
  font-size: 1.15rem;
}

.diary-info {
  min-width: 0;
}

.diary-title {
  margin: 0;
  font-size: 0.95rem;
  color: var(--text-primary);
}

.diary-preview {
  margin: 0.25rem 0 0;
  color: var(--text-secondary);
  font-size: 0.84rem;
  line-height: 1.5;
}

.diary-date {
  margin: 0.35rem 0 0;
  color: #a38998;
  font-size: 0.75rem;
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
}
</style>

