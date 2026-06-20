import { computed, ref } from 'vue'
import diaryService from '@/api/diary'
import type { CreateDiaryRequest, Diary, DiaryQueryParams } from '@/types'

export function useDiaries() {
  const diaries = ref<Diary[]>([])
  const totalCount = ref(0)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const totalDiaries = computed(() => diaries.value.length)
  const recentDiaries = computed(() => diaries.value.slice(0, 3))

  const loadDiaries = async (params?: DiaryQueryParams) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await diaryService.getDiaries(params)
      diaries.value = response.diaries || []
      totalCount.value = response.total ?? 0
    } catch (err) {
      error.value = '加载日记失败'
      console.error('Error loading diaries:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const createDiary = async (data: CreateDiaryRequest) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await diaryService.createDiary(data)
      diaries.value.unshift(response.diary)
      totalCount.value += 1
      return response.diary
    } catch (err) {
      error.value = '创建日记失败'
      console.error('Error creating diary:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const updateDiary = async (id: number, data: Partial<CreateDiaryRequest>) => {
    isLoading.value = true
    error.value = null

    try {
      const response = await diaryService.updateDiary(id, data)
      const index = diaries.value.findIndex(diary => diary.id === id)
      if (index !== -1) diaries.value[index] = response.diary
      return response.diary
    } catch (err) {
      error.value = '更新日记失败'
      console.error('Error updating diary:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const deleteDiary = async (id: number) => {
    isLoading.value = true
    error.value = null

    try {
      await diaryService.deleteDiary(id)
      diaries.value = diaries.value.filter(diary => diary.id !== id)
      totalCount.value = Math.max(0, totalCount.value - 1)
    } catch (err) {
      error.value = '删除日记失败'
      console.error('Error deleting diary:', err)
      throw err
    } finally {
      isLoading.value = false
    }
  }

  const refresh = () => loadDiaries()

  const clear = () => {
    diaries.value = []
  }

  return {
    diaries,
    totalCount,
    isLoading,
    error,
    totalDiaries,
    recentDiaries,
    loadDiaries,
    createDiary,
    updateDiary,
    deleteDiary,
    refresh,
    clear,
  }
}
