export interface User {
  id: number
  username: string
  email: string
  first_name?: string
  last_name?: string
  is_staff?: boolean
  date_joined: string
}

export interface RegisterRequest {
  username: string
  password: string
}

export interface LoginRequest {
  username: string
  password: string
}

export interface TokenResponse {
  access: string
  refresh: string
}

export interface AuthResponse {
  user: User
  token: TokenResponse
}

export type Mood = 'happy' | 'sad' | 'excited' | 'calm' | 'angry' | 'tired' | 'loved' | 'grateful'

export const MOOD_LABELS: Record<Mood, string> = {
  happy: '开心',
  sad: '伤心',
  excited: '兴奋',
  calm: '平静',
  angry: '生气',
  tired: '疲惫',
  loved: '相爱',
  grateful: '感恩',
}

export const MOOD_EMOJIS: Record<Mood, string> = {
  happy: '😊',
  sad: '😢',
  excited: '🤩',
  calm: '😌',
  angry: '😤',
  tired: '😴',
  loved: '😍',
  grateful: '🙏',
}

export type CountdownType = 'anniversary' | 'birthday' | 'event' | 'other'
export type CountdownDirection = 'countup' | 'countdown'
export type RecurringType = 'yearly' | 'monthly' | 'daily'

export interface UserBasic {
  id: number
  username: string
  email: string
}

export interface Album {
  id: number
  name: string
  description: string
  cover_photo: string
  is_default: boolean
  photo_count?: number
  created_by?: number | null
  created_by_details?: UserBasic
  created_at: string
  updated_at: string
}

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
  created_by?: number | null
  created_by_details?: UserBasic
  created_at: string
  updated_at: string
}

export interface DiaryComment {
  id: number
  content: string
  parent: number | null
  created_by: number
  created_by_details?: UserBasic
  created_at: string
  replies?: DiaryComment[]
}

export interface Diary {
  id: number
  title: string
  content: string
  mood: Mood
  category: string
  date: string
  formatted_date?: string
  is_public?: boolean
  is_pinned?: boolean
  attached_photos?: Photo[]
  cover_media?: Photo | null
  word_count?: number
  comments?: DiaryComment[]
  created_by?: number | null
  created_by_details?: UserBasic
  created_at: string
  updated_at: string
}

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
  created_by?: number | null
  created_by_details?: UserBasic
  created_at: string
  updated_at: string
}

export interface ApiResponse<T = any> {
  success: boolean
  message?: string
  data?: T
  errors?: Record<string, string[]>
}

export interface PaginatedResponse<T> {
  count?: number
  next?: string | null
  previous?: string | null
  results?: T
}

export interface DiariesListResponse {
  diaries: Diary[]
  pagination?: {
    page: number
    limit: number
    total: number
    pages: number
  }
}

export interface PhotosListResponse {
  photos: Photo[]
  pagination?: {
    page: number
    limit: number
    total: number
    pages: number
  }
}

export interface CountdownsListResponse {
  countdowns: Countdown[]
  pagination?: {
    page: number
    limit: number
    total: number
    pages: number
  }
}

export interface AlbumsListResponse {
  albums: Album[]
}

export interface MetadataResponse {
  categories?: string[]
  tags?: string[]
}

export interface CreateDiaryRequest {
  title: string
  content: string
  mood: Mood
  category: string
  date?: string
  is_public?: boolean
  photo_ids?: number[]
}

export interface UpdateDiaryRequest extends Partial<CreateDiaryRequest> {}

export interface CreateAlbumRequest {
  name: string
  description?: string
  cover_photo?: string
}

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

export interface DiaryFormData {
  title: string
  content: string
  mood: Mood
  category: string
  date: string
}

export interface CountdownFormData {
  title: string
  description: string
  target_date: string
  type: CountdownType
  is_recurring: boolean
  recurring_type: RecurringType | ''
}

export interface LoadingState {
  isLoading: boolean
  error: string | null
}

export interface PaginationParams {
  page?: number
  page_size?: number
  limit?: number
}

export interface FilterParams {
  category?: string
  mood?: Mood
  start_date?: string
  end_date?: string
  search?: string
}

export interface DiaryQueryParams extends PaginationParams, FilterParams {}

export type NotificationType = 'diary_comment' | 'diary_created' | 'diary_like'

export interface Notification {
  id: number
  type: NotificationType
  title: string
  content: string
  from_user: number
  from_user_details?: UserBasic
  diary?: number
  comment?: number
  is_read: boolean
  created_at: string
}

export interface NotificationsListResponse {
  notifications: Notification[]
  unread_count: number
  pagination?: {
    page: number
    limit: number
    total: number
    pages: number
  }
}
