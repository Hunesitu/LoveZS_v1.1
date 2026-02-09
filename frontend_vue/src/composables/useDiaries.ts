/**
 * 日记 Composable
 * 对应原: frontend/src/hooks/useDiaries.ts
 */

import { ref, computed } from 'vue'
import diaryService from '@/api/diary'
import type { Diary, DiaryQueryParams, CreateDiaryRequest } from '@/types'

export function useDiaries() {
  // 状态
  const diaries = ref<Diary[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  // 计算属性
  const totalDiaries = computed(() => diaries.value.length)
  const recentDiaries = computed(() => diaries.value.slice(0, 3))

  /**
   * 加载日记列表
   */
  const loadDiaries = async (params?: DiaryQueryParams) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await diaryService.getDiaries(params)
      diaries.value = response.diaries || []
    } catch (err) {
      error.value = '加载日记失败'
      console.error('Error loading diaries:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 创建日记
   */
  const createDiary = async (data: CreateDiaryRequest) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await diaryService.createDiary(data)
      // 将新日记添加到列表开头
      diaries.value.unshift(response.diary)
      return response.diary
    } catch (err) {
      error.value = '创建日记失败'
      console.error('Error creating diary:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 更新日记
   */
  const updateDiary = async (id: number, data: Partial<CreateDiaryRequest>) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await diaryService.updateDiary(id, data)
      // 更新列表中的日记
      const index = diaries.value.findIndex(d => d.id === id)
      if (index !== -1) {
        diaries.value[index] = response.diary
      }
      return response.diary
    } catch (err) {
      error.value = '更新日记失败'
      console.error('Error updating diary:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 删除日记
   */
  const deleteDiary = async (id: number) => {
    isLoading.value = true
    error.value = null

    try {
      await diaryService.deleteDiary(id)
      // 从列表中移除
      diaries.value = diaries.value.filter(d => d.id !== id)
    } catch (err) {
      error.value = '删除日记失败'
      console.error('Error deleting diary:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  /**
   * 刷新日记列表
   */
  const refresh = () => loadDiaries()

  /**
   * 清空日记列表
   */
  const clear = () => {
    diaries.value = []
  }

  return {
    // 状态
    diaries,
    isLoading,
    error,

    // 计算属性
    totalDiaries,
    recentDiaries,

    // 方法
    loadDiaries,
    createDiary,
    updateDiary,
    deleteDiary,
    refresh,
    clear,
  }
}
