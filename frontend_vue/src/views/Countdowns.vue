<!--
Countdowns 页面
对应原: frontend/src/pages/Countdowns.tsx
重要日管理，支持每年重复和固定日期
-->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useCountdowns } from '@/composables/useCountdowns'
import { useUiStore } from '@/stores/ui'
import { useUserStore } from '@/stores/user'
import { Plus, Trash2, Calendar as CalendarIcon, Heart, Clock, Edit } from 'lucide-vue-next'
import dayjs from 'dayjs'
import type { Countdown, CreateCountdownRequest } from '@/types'

const { countdowns, isLoading, loadCountdowns, createCountdown, updateCountdown, deleteCountdown } = useCountdowns()
const uiStore = useUiStore()
const userStore = useUserStore()

// 表单状态
const title = ref('')
const targetDate = ref('')
const isRecurring = ref(false)
const recurringMonth = ref<number | null>(null)
const recurringDay = ref<number | null>(null)
const isSubmitting = ref(false)

// 编辑状态
const editingId = ref<number | null>(null)

// 里程碑天数
const milestones = [100, 200, 300, 400, 500, 600, 700, 800, 900, 1000, 1500, 2000, 3000, 5000, 10000]

// 计算下一个里程碑
const getNextMilestone = (currentDays: number) => {
  return milestones.find(m => m > currentDays) || milestones[milestones.length - 1]
}

// 动态计算可选天数（根据月份）
const daysInMonth = computed(() => {
  if (!recurringMonth.value) return 31
  const month = recurringMonth.value
  if ([4, 6, 9, 11].includes(month)) return 30
  if (month === 2) return 29  // 简化处理
  return 31
})

// 统一排序：即将到来的在前，已过去的在后
const sortedCountdowns = computed(() => {
  return [...countdowns.value].sort((a, b) => {
    // 优先按是否即将到来排序
    const aIsUpcoming = (a.days || 0) >= 0
    const bIsUpcoming = (b.days || 0) >= 0

    if (aIsUpcoming && !bIsUpcoming) return -1
    if (!aIsUpcoming && bIsUpcoming) return 1

    // 同类型按天数排序
    return Math.abs(a.days || 0) - Math.abs(b.days || 0)
  })
})

// 分离已过去和即将到来的（用于里程碑计算）
const pastCountdowns = computed(() =>
  sortedCountdowns.value.filter(c => (c.days || 0) < 0)
)

const upcomingCountdowns = computed(() =>
  sortedCountdowns.value.filter(c => (c.days || 0) >= 0)
)

// 最长的纪念日（用于里程碑计算）
const longestCountdown = computed(() => {
  if (pastCountdowns.value.length === 0) return null
  return pastCountdowns.value.reduce((prev, curr) =>
    (curr.absolute_days || 0) > (prev.absolute_days || 0) ? curr : prev
  )
})

// 下一个里程碑
const nextMilestone = computed(() => {
  if (!longestCountdown.value) return null
  const currentDays = longestCountdown.value.absolute_days || 0
  const milestone = getNextMilestone(currentDays) ?? currentDays
  return {
    days: milestone,
    currentDays,
    daysToMilestone: milestone - currentDays,
    progress: milestone > 0 ? Math.min((currentDays / milestone) * 100, 100) : 0
  }
})

// 格式化日期显示
const formatDateDisplay = (c: Countdown) => {
  if (c.is_recurring && c.recurring_month && c.recurring_day) {
    return `每年${c.recurring_month}月${c.recurring_day}日`
  }
  return dayjs(c.target_date).format('YYYY年MM月DD日')
}

// 获取图标
const getDaysIcon = (c: Countdown) => {
  const days = c.days || 0
  if (days === 0) return '🎉'
  if (days > 0) return '⏰'
  return '💕'
}

// 获取天数文本
const getDaysText = (c: Countdown) => {
  const days = c.days || 0
  if (days === 0) return '今天就是！'
  if (days > 0) return `还有 ${days} 天`
  return `已 ${c.absolute_days} 天`
}

// 加载数据
const loadData = async () => {
  try {
    await loadCountdowns()
  } catch (err) {
    console.error('加载重要日失败', err)
  }
}

// 创建重要日
const handleCreate = async () => {
  if (!title.value) return

  // 验证每年重复模式的必填项
  if (isRecurring.value && (!recurringMonth.value || !recurringDay.value)) {
    uiStore.showToast('请选择月份和日期', 'error')
    return
  }

  // 验证固定日期模式的必填项
  if (!isRecurring.value && !targetDate.value) {
    uiStore.showToast('请选择日期', 'error')
    return
  }

  isSubmitting.value = true
  try {
    const data: CreateCountdownRequest = {
      title: title.value,
      is_recurring: isRecurring.value,
      recurring_type: isRecurring.value ? 'yearly' : undefined,
    }

    if (isRecurring.value) {
      // 每年重复
      data.recurring_month = recurringMonth.value!
      data.recurring_day = recurringDay.value!
      // 设置一个占位日期，后端会忽略
      data.target_date = `${new Date().getFullYear()}-${String(recurringMonth.value!).padStart(2, '0')}-${String(recurringDay.value!).padStart(2, '0')}`
    } else {
      // 固定日期
      data.target_date = targetDate.value
      // 自动判断方向
      const date = dayjs(targetDate.value)
      data.direction = date.isBefore(dayjs(), 'day') ? 'countup' : 'countdown'
    }

    await createCountdown(data)
    // 重置表单
    title.value = ''
    targetDate.value = ''
    isRecurring.value = false
    recurringMonth.value = null
    recurringDay.value = null
    uiStore.showToast('重要日添加成功', 'success')
  } catch (err: any) {
    console.error('创建重要日失败', err)
    const errorMsg = err.response?.data?.message || err.message || '创建失败'
    uiStore.showToast(`创建失败: ${errorMsg}`, 'error')
  } finally {
    isSubmitting.value = false
  }
}

// 删除重要日
const handleDelete = async (id: number) => {
  if (!window.confirm('确定删除吗？')) return
  try {
    await deleteCountdown(id)
    uiStore.showToast('删除成功', 'success')
  } catch (err) {
    console.error('删除失败', err)
    uiStore.showToast('删除失败', 'error')
  }
}

// 开始编辑
const handleEdit = (countdown: Countdown) => {
  editingId.value = countdown.id
  title.value = countdown.title
  isRecurring.value = countdown.is_recurring
  recurringMonth.value = countdown.recurring_month ?? null
  recurringDay.value = countdown.recurring_day ?? null

  if (countdown.is_recurring && countdown.recurring_month && countdown.recurring_day) {
    // 每年重复：从 target_date 提取年
    const currentYear = new Date().getFullYear()
    targetDate.value = `${currentYear}-${String(countdown.recurring_month).padStart(2, '0')}-${String(countdown.recurring_day).padStart(2, '0')}`
  } else {
    targetDate.value = countdown.target_date
  }
}

// 取消编辑
const cancelEdit = () => {
  editingId.value = null
  title.value = ''
  targetDate.value = ''
  isRecurring.value = false
  recurringMonth.value = null
  recurringDay.value = null
}

// 更新重要日
const handleUpdate = async () => {
  if (!title.value || !editingId.value) return

  // 验证每年重复模式的必填项
  if (isRecurring.value && (!recurringMonth.value || !recurringDay.value)) {
    uiStore.showToast('请选择月份和日期', 'error')
    return
  }

  // 验证固定日期模式的必填项
  if (!isRecurring.value && !targetDate.value) {
    uiStore.showToast('请选择日期', 'error')
    return
  }

  isSubmitting.value = true
  try {
    const data: CreateCountdownRequest = {
      title: title.value,
      is_recurring: isRecurring.value,
      recurring_type: isRecurring.value ? 'yearly' : undefined,
      type: 'other',  // 默认类型
    }

    if (isRecurring.value) {
      data.recurring_month = recurringMonth.value!
      data.recurring_day = recurringDay.value!
      data.direction = 'countup'
      // 占位日期（后端根据 recurring_month/day 计算实际日期）
      data.target_date = `${new Date().getFullYear()}-${String(recurringMonth.value!).padStart(2, '0')}-${String(recurringDay.value!).padStart(2, '0')}`
    } else {
      data.target_date = targetDate.value
      const date = dayjs(targetDate.value)
      data.direction = date.isBefore(dayjs(), 'day') ? 'countup' : 'countdown'
    }

    await updateCountdown(editingId.value, data)
    cancelEdit()
    uiStore.showToast('更新成功', 'success')
  } catch (err: any) {
    console.error('更新重要日失败', err)
    // 打印详细的错误信息
    const errorData = err.response?.data
    if (errorData) {
      console.log('错误详情:', JSON.stringify(errorData, null, 2))
    }
    const errorMsg = err.response?.data?.message || err.message || '更新失败'
    uiStore.showToast(`更新失败: ${errorMsg}`, 'error')
  } finally {
    isSubmitting.value = false
  }
}

// 组件挂载时加载数据
onMounted(() => {
  loadData()
})
</script>

<template>
  <div class="countdowns-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">
        <CalendarIcon :size="24" class="title-icon" />
        重要日
      </h1>
      <p class="page-subtitle">记录那些重要的日子</p>
    </div>

    <!-- 创建/编辑表单（仅管理员可见） -->
    <div v-if="userStore.isAdmin" class="card form-card">
      <h2 class="section-title">{{ editingId ? '编辑重要日' : '添加新重要日' }}</h2>
      <form @submit.prevent="editingId ? handleUpdate() : handleCreate()" class="create-form">
        <div class="form-group">
          <label class="form-label">标题</label>
          <input
            v-model="title"
            type="text"
            class="input-field"
            placeholder="如：她的生日、相识纪念日"
            required
          />
        </div>

        <!-- 重复类型选择 -->
        <div class="form-group">
          <label class="form-label">重复类型</label>
          <div class="radio-group">
            <label class="radio-option" :class="{ active: !isRecurring }">
              <input
                type="radio"
                v-model="isRecurring"
                :value="false"
              />
              <span>固定日期</span>
            </label>
            <label class="radio-option" :class="{ active: isRecurring }">
              <input
                type="radio"
                v-model="isRecurring"
                :value="true"
              />
              <span>每年重复</span>
            </label>
          </div>
        </div>

        <!-- 固定日期选择器 -->
        <div v-if="!isRecurring" class="form-group">
          <label class="form-label">选择日期</label>
          <input
            v-model="targetDate"
            type="date"
            class="input-field"
            required
          />
        </div>

        <!-- 每年重复选择器 -->
        <div v-else class="form-group-inline">
          <div class="form-group">
            <label class="form-label">月份</label>
            <select v-model="recurringMonth" class="input-field" required>
              <option value="">选择月份</option>
              <option v-for="m in 12" :key="m" :value="m">{{ m }}月</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">日期</label>
            <select v-model="recurringDay" class="input-field" required :disabled="!recurringMonth">
              <option value="">选择日期</option>
              <option v-for="d in daysInMonth" :key="d" :value="d">{{ d }}日</option>
            </select>
          </div>
        </div>

        <div class="form-group form-submit">
          <button v-if="editingId" type="button" class="btn-secondary" @click="cancelEdit" :disabled="isSubmitting">
            取消
          </button>
          <button type="submit" class="btn-primary" :disabled="isSubmitting">
            <Plus v-if="!isSubmitting && !editingId" :size="16" class="mr-2" />
            <span v-if="isSubmitting">{{ editingId ? '更新中...' : '创建中...' }}</span>
            <span v-else-if="editingId">更新</span>
            <span v-else>添加</span>
          </button>
        </div>
      </form>
    </div>

    <!-- 里程碑卡片 -->
    <div v-if="nextMilestone" class="milestone-card">
      <div class="milestone-content">
        <h3 class="milestone-title">
          <span class="milestone-icon">🏆</span>
          下一个里程碑
        </h3>
        <p class="milestone-subtitle">
          {{ longestCountdown?.title }} 已有
          <span class="milestone-days">{{ nextMilestone.currentDays }}</span> 天
        </p>
        <div class="milestone-target">
          <span class="target-icon">🎯</span>
          <span class="target-text">
            距离 {{ nextMilestone.days }} 天还有 {{ nextMilestone.daysToMilestone }} 天
          </span>
        </div>
        <!-- 进度条 -->
        <div class="progress-container">
          <div class="progress-bar">
            <div
              class="progress-fill"
              :style="{ width: `${nextMilestone.progress}%` }"
            ></div>
          </div>
          <p class="progress-text">{{ Math.round(nextMilestone.progress) }}% 完成</p>
        </div>
      </div>
    </div>

    <!-- 统一列表 -->
    <div class="countdowns-section">
      <h2 class="section-title">
        <Heart :size="20" class="section-icon" />
        所有重要日
      </h2>

      <div v-if="sortedCountdowns.length > 0" class="countdowns-list">
        <div v-for="c in sortedCountdowns" :key="c.id" class="countdown-item">
          <div class="item-content">
            <h3 class="item-title">{{ c.title }}</h3>
            <p class="item-date">
              {{ formatDateDisplay(c) }}
            </p>
            <div class="item-days">
              <span class="days-icon">{{ getDaysIcon(c) }}</span>
              <span class="days-text">{{ getDaysText(c) }}</span>
            </div>
          </div>
          <div class="item-actions">
            <button
              v-if="userStore.isAdmin"
              @click="handleEdit(c)"
              class="edit-btn"
              title="编辑"
            >
              <Edit :size="16" />
            </button>
            <button
              v-if="userStore.isAdmin"
              @click="handleDelete(c.id)"
              class="delete-btn"
              title="删除"
            >
              <Trash2 :size="16" />
            </button>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div v-else class="empty-state">
        <Heart :size="48" class="empty-icon" />
        <p class="empty-text">还没有添加重要日</p>
        <p class="empty-hint">添加一个纪念日或生日开始记录吧</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.countdowns-page {
  width: 100%;
}

.page-header {
  margin-bottom: 1.25rem;
}

.page-title {
  margin: 0;
  font-size: 1.55rem;
  font-weight: 700;
  color: var(--text-primary);
  display: flex;
  align-items: center;
}

.title-icon {
  color: var(--pink-500);
  margin-right: 0.5rem;
}

.page-subtitle {
  margin: 0.3rem 0 0;
  color: var(--text-secondary);
}

.card {
  background: var(--bg-elevated);
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-lg);
  padding: 1rem;
  box-shadow: var(--shadow-soft);
}

.section-title {
  margin: 0 0 0.9rem;
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text-primary);
  display: flex;
  align-items: center;
}

.section-icon {
  color: var(--pink-500);
  margin-right: 0.5rem;
}

.form-card {
  margin-bottom: 1.25rem;
}

.create-form {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.85rem;
}

.form-group {
  display: flex;
  flex-direction: column;
}

.form-group-inline {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.85rem;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.3rem;
}

.input-field {
  padding: 0.625rem 0.875rem;
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  color: var(--text-primary);
  background-color: #fff;
  transition: border-color var(--dur-base), box-shadow var(--dur-base), background-color var(--dur-base);
}

.input-field:focus {
  outline: none;
  border-color: var(--pink-300);
  box-shadow: var(--shadow-focus);
  background-color: #fff9fc;
}

.input-field:disabled {
  background-color: var(--bg-soft);
  cursor: not-allowed;
}

.radio-group {
  display: flex;
  gap: 0.5rem;
}

.radio-option {
  flex: 1;
  padding: 0.625rem 0.875rem;
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-sm);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: border-color var(--dur-base), background-color var(--dur-base);
}

.radio-option input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.radio-option span {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.radio-option.active {
  border-color: var(--pink-300);
  background-color: #fff9fc;
}

.radio-option.active span {
  color: var(--pink-500);
  font-weight: 600;
}

.form-submit {
  justify-content: flex-end;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.625rem 1.2rem;
  background: linear-gradient(135deg, var(--pink-500) 0%, var(--rose-500) 100%);
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 8px 16px rgba(217, 117, 154, 0.26);
  transition: transform var(--dur-fast), box-shadow var(--dur-base), filter var(--dur-base);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 12px 22px rgba(217, 117, 154, 0.32);
  filter: brightness(1.02);
}

.btn-primary:disabled {
  opacity: 0.62;
  cursor: not-allowed;
}

.milestone-card {
  background: linear-gradient(130deg, #fff3f8 0%, #fef0f6 56%, #fff8fb 100%);
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-lg);
  padding: 1rem;
  box-shadow: var(--shadow-soft);
  margin-bottom: 1.25rem;
}

.milestone-content {
  display: flex;
  flex-direction: column;
}

.milestone-title {
  margin: 0;
  font-weight: 700;
  color: var(--text-primary);
  display: flex;
  align-items: center;
}

.milestone-icon {
  font-size: 1.25rem;
  margin-right: 0.5rem;
}

.milestone-subtitle {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin: 0.3rem 0 0;
}

.milestone-days {
  font-weight: 700;
  color: var(--pink-500);
}

.milestone-target {
  margin-top: 0.7rem;
  display: flex;
  align-items: center;
}

.target-icon {
  font-size: 1.35rem;
  margin-right: 0.4rem;
}

.target-text {
  font-size: 1rem;
  font-weight: 700;
  color: #9e6380;
}

.progress-container {
  margin-top: 0.75rem;
}

.progress-bar {
  width: 100%;
  height: 0.6rem;
  background-color: #f1dfe8;
  border-radius: 9999px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(135deg, var(--pink-500) 0%, #b989c2 100%);
  border-radius: 9999px;
  transition: width 0.5s ease;
}

.progress-text {
  font-size: 0.75rem;
  color: var(--text-secondary);
  margin: 0.25rem 0 0;
  text-align: right;
}

.countdowns-section {
  margin-bottom: 1.25rem;
}

.countdowns-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.countdown-item {
  background: var(--bg-elevated);
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-lg);
  padding: 0.95rem;
  box-shadow: var(--shadow-soft);
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  transition: transform var(--dur-fast), border-color var(--dur-base), box-shadow var(--dur-base);
}

.countdown-item:hover {
  transform: translateY(-2px);
  border-color: var(--border-strong);
  box-shadow: var(--shadow-hover);
}

.item-content {
  flex: 1;
}

.item-title {
  margin: 0;
  font-weight: 600;
  color: var(--text-primary);
}

.item-date {
  margin: 0.2rem 0 0;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.item-days {
  margin-top: 0.45rem;
  display: flex;
  align-items: center;
}

.days-icon {
  font-size: 1.4rem;
  margin-right: 0.45rem;
}

.days-text {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--pink-500);
}

.delete-btn {
  padding: 0.28rem;
  color: #af94a2;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 0.45rem;
  cursor: pointer;
  transition: color var(--dur-base), background-color var(--dur-base), border-color var(--dur-base);
  display: inline-flex;
  align-items: center;
}

.delete-btn:hover {
  color: #c45c7c;
  background: #fff2f6;
  border-color: #f2bfd1;
}

.edit-btn {
  padding: 0.28rem;
  color: #af94a2;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 0.45rem;
  cursor: pointer;
  transition: color var(--dur-base), background-color var(--dur-base), border-color var(--dur-base);
  display: inline-flex;
  align-items: center;
}

.edit-btn:hover {
  color: var(--pink-500);
  background: var(--pink-50);
  border-color: var(--border-soft);
}

.item-actions {
  display: flex;
  gap: 0.25rem;
}

.empty-state {
  background: var(--bg-elevated);
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-lg);
  padding: 3rem 1rem;
  box-shadow: var(--shadow-soft);
  text-align: center;
}

.empty-icon {
  color: #b198a6;
  margin: 0 auto 0.75rem;
}

.empty-text {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}

.empty-hint {
  margin: 0.3rem 0 0;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.mr-2 {
  margin-right: 0.5rem;
}

@media (min-width: 768px) {
  .form-group-inline {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .page-title {
    font-size: 1.3rem;
  }

  .form-group-inline {
    grid-template-columns: 1fr;
  }
}
</style>
