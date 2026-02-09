/**
 * 重要日 Composable
 */

import { ref, computed } from 'vue'
import countdownService from '@/api/countdown'
import type { Countdown, CreateCountdownRequest } from '@/types'

export function useCountdowns() {
  const countdowns = ref<Countdown[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const totalCountdowns = computed(() => countdowns.value.length)

  // 获取已过去的重要日（countup）
  const pastCountdowns = computed(() =>
    countdowns.value.filter(c => c.direction === 'countup')
  )

  // 获取即将到来的重要日（countdown）
  const upcomingCountdowns = computed(() =>
    countdowns.value.filter(c => c.direction === 'countdown' && c.days > 0)
  )

  // 获取恋爱天数（最早的 countup）
  const loveDays = computed(() => {
    if (pastCountdowns.value.length === 0) return 0
    // 返回绝对值最大的天数
    return Math.min(...pastCountdowns.value.map(c => Math.abs(c.days)))
  })

  // 获取下一个倒计时
  const nextCountdown = computed(() => {
    if (upcomingCountdowns.value.length === 0) return null
    return upcomingCountdowns.value.sort((a, b) => a.days - b.days)[0]
  })

  /**
   * 加载重要日列表
   */
  const loadCountdowns = async (params?: { type?: string; direction?: string }) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await countdownService.getCountdowns(params)
      countdowns.value = response.countdowns || []
    } catch (err) {
      error.value = '加载重要日失败'
      console.error('Error loading countdowns:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 创建重要日
   */
  const createCountdown = async (data: CreateCountdownRequest) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await countdownService.createCountdown(data)
      countdowns.value.push(response.countdown)
      return response.countdown
    } catch (err) {
      error.value = '创建重要日失败'
      console.error('Error creating countdown:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 更新重要日
   */
  const updateCountdown = async (id: number, data: Partial<CreateCountdownRequest>) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await countdownService.updateCountdown(id, data)
      const index = countdowns.value.findIndex(c => c.id === id)
      if (index !== -1) {
        countdowns.value[index] = response.countdown
      }
      return response.countdown
    } catch (err) {
      error.value = '更新重要日失败'
      console.error('Error updating countdown:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 删除重要日
   */
  const deleteCountdown = async (id: number) => {
    isLoading.value = true
    error.value = null

    try {
      await countdownService.deleteCountdown(id)
      countdowns.value = countdowns.value.filter(c => c.id !== id)
    } catch (err) {
      error.value = '删除重要日失败'
      console.error('Error deleting countdown:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 刷新
   */
  const refresh = () => loadCountdowns()

  return {
    // 状态
    countdowns,
    isLoading,
    error,

    // 计算属性
    totalCountdowns,
    pastCountdowns,
    upcomingCountdowns,
    loveDays,
    nextCountdown,

    // 方法
    loadCountdowns,
    createCountdown,
    updateCountdown,
    deleteCountdown,
    refresh,
  }
}
