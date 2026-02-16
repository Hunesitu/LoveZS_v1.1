/**
 * 照片 API 服务
 */

import { api } from './client'
import type { Photo } from '../types'

interface DjangoPaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T
}

interface PhotosResult {
  photos: Photo[]
}

export const getPhotos = async (): Promise<{ photos: Photo[] }> => {
  const response = await api.get<DjangoPaginatedResponse<PhotosResult>>('/photos/')
  return response.data.results || { photos: [] }
}

export const getPhoto = async (id: number): Promise<{ photo: Photo }> => {
  const response = await api.get<{ photo: Photo }>(`/photos/${id}/`)
  return response.data
}

export const deletePhoto = async (id: number): Promise<void> => {
  await api.delete(`/photos/${id}/`)
}

export const uploadPhotos = async (
  formData: FormData
): Promise<{ photos: Photo[] }> => {
  const response = await api.post<{ photos: Photo[] }>(
    '/photos/upload/',
    formData,
    {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 300000, // 5分钟，视频文件较大
    }
  )
  return response.data
}

const photoService = {
  getPhotos,
  getPhoto,
  deletePhoto,
  uploadPhotos,
}

export default photoService

