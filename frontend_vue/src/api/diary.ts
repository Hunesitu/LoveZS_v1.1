/**
 * 日记 API 服务
 * 对应原: frontend/src/services/diary.ts
 */

import { api } from './client'
import type {
  Diary,
  CreateDiaryRequest,
  UpdateDiaryRequest,
  DiaryQueryParams,
} from '../types'

/**
 * Django REST Framework 分页响应
 */
interface DjangoPaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T
}

/**
 * 日记列表结果
 */
interface DiariesResult {
  diaries: Diary[]
}

/**
 * 获取日记列表
 */
export const getDiaries = async (params?: DiaryQueryParams): Promise<{ diaries: Diary[] }> => {
  const response = await api.get<DjangoPaginatedResponse<DiariesResult>>('/diaries/', { params })
  const result = response.data.results
  return { diaries: result?.diaries ?? [] }
}

/**
 * 获取单篇日记
 */
export const getDiary = async (id: number): Promise<{ diary: Diary }> => {
  const response = await api.get<{ diary: Diary }>(`/diaries/${id}/`)
  return response.data
}

/**
 * 创建日记
 */
export const createDiary = async (data: CreateDiaryRequest): Promise<{ diary: Diary }> => {
  const response = await api.post<{ diary: Diary }>('/diaries/', data)
  return response.data
}

/**
 * 更新日记
 */
export const updateDiary = async (
  id: number,
  data: UpdateDiaryRequest
): Promise<{ diary: Diary }> => {
  const response = await api.put<{ diary: Diary }>(`/diaries/${id}/`, data)
  return response.data
}

/**
 * 删除日记
 */
export const deleteDiary = async (id: number): Promise<void> => {
  await api.delete(`/diaries/${id}/`)
}

/**
 * 关联照片到日记
 */
export const attachPhotos = async (id: number, photoIds: number[]): Promise<void> => {
  await api.post(`/diaries/${id}/photos/`, { photoIds })
}

/**
 * 从日记移除照片
 */
export const removePhoto = async (diaryId: number, photoId: number): Promise<void> => {
  await api.delete(`/diaries/${diaryId}/photos/${photoId}/`)
}

/**
 * 获取所有分类
 */
export const getCategories = async (): Promise<{ categories: string[] }> => {
  const response = await api.get<{ categories: string[] }>('/diaries/meta/categories/')
  return response.data
}

// 默认导出
const diaryService = {
  getDiaries,
  getDiary,
  createDiary,
  updateDiary,
  deleteDiary,
  attachPhotos,
  removePhoto,
  getCategories,
}

export default diaryService
