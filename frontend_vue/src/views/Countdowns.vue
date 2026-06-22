<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { Calendar as CalendarIcon, Edit, Heart, Plus, Trash2, Trophy } from 'lucide-vue-next'
import dayjs from 'dayjs'
import { useCountdowns } from '@/composables/useCountdowns'
import { useUiStore } from '@/stores/ui'
import { useUserStore } from '@/stores/user'
import { findNextMilestone } from '@/utils/milestones'
import type { Countdown, CreateCountdownRequest } from '@/types'

const { countdowns, loadCountdowns, createCountdown, updateCountdown, deleteCountdown } = useCountdowns()
const uiStore = useUiStore()
const userStore = useUserStore()

const title = ref('')
const targetDate = ref('')
const isRecurring = ref(false)
const recurringMonth = ref<number | null>(null)
const recurringDay = ref<number | null>(null)
const isSubmitting = ref(false)
const editingId = ref<number | null>(null)

const daysInMonth = computed(() => {
  if (!recurringMonth.value) return 31
  if ([4, 6, 9, 11].includes(recurringMonth.value)) return 30
  if (recurringMonth.value === 2) return 29
  return 31
})

const sortedCountdowns = computed(() =>
  [...countdowns.value].sort((a, b) => {
    const aUpcoming = (a.days || 0) >= 0
    const bUpcoming = (b.days || 0) >= 0
    if (aUpcoming && !bUpcoming) return -1
    if (!aUpcoming && bUpcoming) return 1
    return Math.abs(a.days || 0) - Math.abs(b.days || 0)
  })
)

const nextMilestone = computed(() => findNextMilestone(countdowns.value))

const formatDateDisplay = (countdown: Countdown) => {
  if (countdown.is_recurring && countdown.recurring_month && countdown.recurring_day) {
    return `每年 ${countdown.recurring_month}月${countdown.recurring_day}日`
  }
  return dayjs(countdown.target_date).format('YYYY年M月D日')
}

const getDaysText = (countdown: Countdown) => {
  const days = countdown.days || 0
  if (days === 0) return '今天就是'
  if (days > 0) return `还有 ${days} 天`
  return `已 ${countdown.absolute_days} 天`
}

const resetForm = () => {
  editingId.value = null
  title.value = ''
  targetDate.value = ''
  isRecurring.value = false
  recurringMonth.value = null
  recurringDay.value = null
}

const buildPayload = (): CreateCountdownRequest | null => {
  if (!title.value.trim()) {
    uiStore.showToast('请输入标题', 'warning')
    return null
  }

  if (isRecurring.value && (!recurringMonth.value || !recurringDay.value)) {
    uiStore.showToast('请选择月份和日期', 'warning')
    return null
  }

  if (!isRecurring.value && !targetDate.value) {
    uiStore.showToast('请选择日期', 'warning')
    return null
  }

  const payload: CreateCountdownRequest = {
    title: title.value.trim(),
    type: 'other',
    is_recurring: isRecurring.value,
    recurring_type: isRecurring.value ? 'yearly' : undefined,
  }

  if (isRecurring.value) {
    payload.recurring_month = recurringMonth.value!
    payload.recurring_day = recurringDay.value!
    payload.direction = 'countup'
    payload.target_date = `${new Date().getFullYear()}-${String(recurringMonth.value!).padStart(2, '0')}-${String(recurringDay.value!).padStart(2, '0')}`
  } else {
    payload.target_date = targetDate.value
    payload.direction = dayjs(targetDate.value).isBefore(dayjs(), 'day') ? 'countup' : 'countdown'
  }

  return payload
}

const handleSubmit = async () => {
  const payload = buildPayload()
  if (!payload) return

  isSubmitting.value = true
  try {
    if (editingId.value) {
      await updateCountdown(editingId.value, payload)
      uiStore.showToast('重要日已更新', 'success')
    } else {
      await createCountdown(payload)
      uiStore.showToast('重要日已添加', 'success')
    }
    resetForm()
  } catch (error: any) {
    console.error('Save countdown failed:', error)
    uiStore.showToast(error.response?.data?.message || '保存失败，请稍后重试', 'error')
  } finally {
    isSubmitting.value = false
  }
}

const handleEdit = (countdown: Countdown) => {
  editingId.value = countdown.id
  title.value = countdown.title
  isRecurring.value = countdown.is_recurring
  recurringMonth.value = countdown.recurring_month ?? null
  recurringDay.value = countdown.recurring_day ?? null
  targetDate.value = countdown.is_recurring && countdown.recurring_month && countdown.recurring_day
    ? `${new Date().getFullYear()}-${String(countdown.recurring_month).padStart(2, '0')}-${String(countdown.recurring_day).padStart(2, '0')}`
    : countdown.target_date
}

const handleDelete = async (id: number) => {
  if (!window.confirm('确定要删除这个重要日吗？')) return

  try {
    await deleteCountdown(id)
    uiStore.showToast('删除成功', 'success')
  } catch (error) {
    console.error('Delete countdown failed:', error)
    uiStore.showToast('删除失败，请稍后重试', 'error')
  }
}

onMounted(() => {
  loadCountdowns()
})
</script>

<template>
  <div class="countdowns-page page-narrow">
    <div class="page-header">
      <div>
        <p class="romance-kicker">Milestone Timeline</p>
        <h1 class="page-title">
          <CalendarIcon :size="24" class="title-icon" />
          重要日
        </h1>
        <p class="page-subtitle">把相遇、生日和每个约定，都放进不会褪色的时间轴。</p>
      </div>
    </div>

    <section v-if="userStore.isAdmin" class="card form-card cinematic-card">
      <h2 class="section-title">{{ editingId ? '编辑重要日' : '添加重要日' }}</h2>
      <form class="create-form" @submit.prevent="handleSubmit">
        <div class="form-group">
          <label class="form-label" for="countdown-title">标题</label>
          <input id="countdown-title" v-model="title" type="text" class="input-field" placeholder="例如：她的生日、相识纪念日" />
        </div>

        <div class="form-group">
          <label class="form-label">重复类型</label>
          <div class="radio-group">
            <label class="radio-option" :class="{ active: !isRecurring }">
              <input v-model="isRecurring" type="radio" :value="false" />
              <span>固定日期</span>
            </label>
            <label class="radio-option" :class="{ active: isRecurring }">
              <input v-model="isRecurring" type="radio" :value="true" />
              <span>每年重复</span>
            </label>
          </div>
        </div>

        <div v-if="!isRecurring" class="form-group">
          <label class="form-label" for="target-date">选择日期</label>
          <input id="target-date" v-model="targetDate" type="date" class="input-field" />
        </div>

        <div v-else class="form-row">
          <div class="form-group">
            <label class="form-label" for="recurring-month">月份</label>
            <select id="recurring-month" v-model="recurringMonth" class="input-field">
              <option :value="null">选择月份</option>
              <option v-for="m in 12" :key="m" :value="m">{{ m }}月</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label" for="recurring-day">日期</label>
            <select id="recurring-day" v-model="recurringDay" class="input-field" :disabled="!recurringMonth">
              <option :value="null">选择日期</option>
              <option v-for="d in daysInMonth" :key="d" :value="d">{{ d }}日</option>
            </select>
          </div>
        </div>

        <div class="form-actions">
          <button v-if="editingId" type="button" class="btn-secondary" @click="resetForm">取消</button>
          <button type="submit" class="btn-primary" :disabled="isSubmitting">
            <Plus v-if="!editingId" :size="16" />
            {{ isSubmitting ? '保存中...' : editingId ? '更新' : '添加' }}
          </button>
        </div>
      </form>
    </section>

    <section v-if="nextMilestone" class="milestone-card cinematic-card">
      <div>
        <h2 class="section-title">
          <Trophy :size="20" class="section-icon" />
          下一个里程碑
        </h2>
        <p class="milestone-copy">
          {{ nextMilestone.title }} 在
          <strong>{{ nextMilestone.remaining }}</strong> 天后抵达，
          就是 {{ dayjs(nextMilestone.targetDate).format('YYYY年M月D日') }}，下一束追光已经在路上。
        </p>
        <div class="progress-bar">
          <span :style="{ width: `${nextMilestone.progress}%` }"></span>
        </div>
      </div>
    </section>

    <section class="countdowns-section">
      <h2 class="section-title">
        <Heart :size="20" class="section-icon" />
        所有重要日
      </h2>

      <div v-if="sortedCountdowns.length > 0" class="countdowns-list">
        <article v-for="countdown in sortedCountdowns" :key="countdown.id" class="countdown-item cinematic-card">
          <div class="item-content">
            <h3 class="item-title">{{ countdown.title }}</h3>
            <p class="item-date">{{ formatDateDisplay(countdown) }}</p>
            <p class="item-days">{{ getDaysText(countdown) }}</p>
          </div>
          <div v-if="userStore.isAdmin" class="item-actions">
            <button class="action-btn" type="button" title="编辑" @click="handleEdit(countdown)">
              <Edit :size="16" />
            </button>
            <button class="action-btn danger" type="button" title="删除" @click="handleDelete(countdown.id)">
              <Trash2 :size="16" />
            </button>
          </div>
        </article>
      </div>

      <div v-else class="empty-state-card">
        <div class="empty-state">
          <Heart :size="44" fill="currentColor" />
          <p>还没有添加重要日</p>
          <p>添加一个纪念日或生日，让时间开始替你们倒数。</p>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.form-card,
.milestone-card {
  padding: 1rem;
  margin-bottom: 1.25rem;
}

.create-form {
  display: grid;
  gap: 0.85rem;
}

.radio-group {
  display: flex;
  gap: 0.6rem;
}

.radio-option {
  display: inline-flex;
  flex: 1;
  align-items: center;
  justify-content: center;
  min-height: 42px;
  padding: 0.6rem 0.85rem;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  color: var(--ink-soft);
  background: rgba(255, 255, 255, 0.05);
  cursor: pointer;
}

.radio-option input {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.radio-option.active {
  color: var(--rose-bright);
  border-color: var(--line-strong);
  background: rgba(240, 120, 182, 0.14);
  font-weight: 700;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.7rem;
}

.milestone-copy {
  margin: 0.7rem 0 0.8rem;
  color: var(--ink-soft);
  line-height: 1.7;
}

.milestone-copy strong {
  color: var(--rose-bright);
}

.progress-bar {
  overflow: hidden;
  height: 0.62rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.1);
}

.progress-bar span {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: linear-gradient(90deg, var(--violet), var(--rose-bright));
  transition: width var(--dur-slow) ease;
}

.countdowns-section {
  display: grid;
  gap: 0.9rem;
}

.countdowns-list {
  display: grid;
  gap: 0.75rem;
}

.countdown-item {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem;
  transition: transform var(--dur-base) ease;
}

.countdown-item:hover {
  transform: translateY(-3px);
}

.item-title {
  margin: 0;
  color: var(--ink);
  font-size: 1rem;
}

.item-date {
  margin: 0.25rem 0 0;
  color: var(--ink-soft);
}

.item-days {
  margin: 0.45rem 0 0;
  color: var(--rose-bright);
  font-size: 1.05rem;
  font-weight: 800;
}

.item-actions {
  display: flex;
  gap: 0.3rem;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border: 1px solid transparent;
  color: var(--ink-muted);
  background: transparent;
}

.action-btn:hover {
  color: var(--rose-bright);
  border-color: var(--line);
  background: rgba(255, 255, 255, 0.06);
}

.action-btn.danger:hover {
  color: var(--danger);
}

.empty-state-card {
  padding: 1rem;
}

.empty-state {
  gap: 0.5rem;
}

.empty-state svg {
  color: var(--rose-bright);
}

.empty-state p {
  margin: 0;
}

@media (max-width: 640px) {
  .radio-group,
  .form-actions {
    flex-direction: column;
  }

  .countdown-item {
    flex-direction: column;
  }
}
</style>
