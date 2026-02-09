/**
 * LoveZs 类型定义
 * 从原 Express 后端 API 响应类型转换而来
 */

// ========================================
// 模型类型
// ========================================

/**
 * 心情选项
 */
export type Mood = 'happy' | 'sad' | 'excited' | 'calm' | 'angry' | 'tired' | 'loved' | 'grateful'

/**
 * 心情选项显示文本
 */
export const MOOD_LABELS: Record<Mood, string> = {
  happy: '开心',
  sad: '伤心',
  excited: '兴奋',
  calm: '平静',
  angry: '生气',
  tired: '疲惫',
  loved: '被爱',
  grateful: '感恩'
}

/**
 * 心情选项对应的 Emoji
 */
export const MOOD_EMOJIS: Record<Mood, string> = {
  happy: '😊',
  sad: '😢',
  excited: '🤩',
  calm: '😌',
  angry: '😠',
  tired: '😴',
  loved: '🥰',
  grateful: '🙏'
}

/**
 * 重要日类型
 */
export type CountdownType = 'anniversary' | 'birthday' | 'event' | 'other'

/**
 * 重要日方向
 */
export type CountdownDirection = 'countup' | 'countdown'

/**
 * 重复类型
 */
export type RecurringType = 'yearly' | 'monthly' | 'daily'

/**
 * 相册模型
 */
export interface Album {
  id: number
  name: string
  description: string
  cover_photo: string
  is_default: boolean
  photo_count?: number
  created_at: string
  updated_at: string
}

/**
 * 照片模型
 */
export interface Photo {
  id: number
  filename: string
  original_name: string
  path: string
  url: string
  size: number
  size_formatted?: string
  mimetype: string
  album: number
  album_details?: Album
  description: string
  location?: {
    latitude: number
    longitude: number
    address?: string
  }
  exif?: {
    camera?: string
    lens?: string
    aperture?: string
    shutter_speed?: string
    iso?: number
    focal_length?: string
    date_time?: string
  }
  compressed_url?: string
  thumbnail_url?: string
  created_at: string
  updated_at: string
}

/**
 * 日记模型
 */
export interface Diary {
  id: number
  title: string
  content: string
  mood: Mood
  category: string
  date: string
  formatted_date?: string
  tags: string[]
  attached_photos?: Photo[]
  word_count?: number
  created_at: string
  updated_at: string
}

/**
 * 重要日模型
 */
export interface Countdown {
  id: number
  title: string
  description: string
  target_date: string
  formatted_target_date?: string
  type: CountdownType
  direction: CountdownDirection
  is_recurring: boolean
  recurring_type?: RecurringType
  recurring_month?: number | null
  recurring_day?: number | null
  days: number
  absolute_days?: number
  status: string
  created_at: string
  updated_at: string
}

// ========================================
// API 请求/响应类型
// ========================================

/**
 * API 响应基础格式
 */
export interface ApiResponse<T = any> {
  success: boolean
  message?: string
  data?: T
}

/**
 * 分页数据格式
 */
export interface PaginatedResponse<T> {
  count?: number
  next?: string | null
  previous?: string | null
  results?: T
}

/**
 * 日记列表响应
 */
export interface DiariesListResponse {
  diaries: Diary[]
  pagination?: {
    page: number
    limit: number
    total: number
    pages: number
  }
}

/**
 * 照片列表响应
 */
export interface PhotosListResponse {
  photos: Photo[]
  pagination?: {
    page: number
    limit: number
    total: number
    pages: number
  }
}

/**
 * 重要日列表响应
 */
export interface CountdownsListResponse {
  countdowns: Countdown[]
  pagination?: {
    page: number
    limit: number
    total: number
    pages: number
  }
}

/**
 * 相册列表响应
 */
export interface AlbumsListResponse {
  albums: Album[]
}

/**
 * 元数据响应
 */
export interface MetadataResponse {
  categories?: string[]
  tags?: string[]
}

// ========================================
// 创建/更新请求类型
// ========================================

/**
 * 创建日记请求
 */
export interface CreateDiaryRequest {
  title: string
  content: string
  mood: Mood
  category: string
  date?: string
  tags?: string[]
  photo_ids?: number[]
}

/**
 * 更新日记请求
 */
export interface UpdateDiaryRequest extends Partial<CreateDiaryRequest> {
}

/**
 * 创建相册请求
 */
export interface CreateAlbumRequest {
  name: string
  description?: string
  cover_photo?: string
}

/**
 * 创建重要日请求
 */
export interface CreateCountdownRequest {
  title: string
  description?: string
  target_date?: string
  type?: CountdownType
  direction?: CountdownDirection
  is_recurring?: boolean
  recurring_type?: RecurringType
  recurring_month?: number
  recurring_day?: number
}

// ========================================
// 表单类型
// ========================================

/**
 * 日记表单数据
 */
export interface DiaryFormData {
  title: string
  content: string
  mood: Mood
  category: string
  date: string
  tags: string[]
}

/**
 * 重要日表单数据
 */
export interface CountdownFormData {
  title: string
  description: string
  target_date: string
  type: CountdownType
  is_recurring: boolean
  recurring_type: RecurringType | ''
}

// ========================================
// UI状态类型
// ========================================

/**
 * 加载状态
 */
export interface LoadingState {
  isLoading: boolean
  error: string | null
}

/**
 * 分页参数
 */
export interface PaginationParams {
  page?: number
  page_size?: number
  limit?: number
}

/**
 * 过滤参数
 */
export interface FilterParams {
  category?: string
  mood?: Mood
  start_date?: string
  end_date?: string
  search?: string
}

/**
 * 日记查询参数
 */
export interface DiaryQueryParams extends PaginationParams, FilterParams {
}
