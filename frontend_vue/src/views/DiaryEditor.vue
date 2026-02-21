<!--
DiaryEditor 页面
日记编辑器，Markdown 编辑，照片关联
-->
<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useDiaries } from '@/composables/useDiaries'
import { useUiStore } from '@/stores/ui'
import { Save, X } from 'lucide-vue-next'
import dayjs from 'dayjs'
import type { Mood, CreateDiaryRequest, Photo, Diary } from '@/types'
import photoService from '@/api/photo'
import diaryService from '@/api/diary'
import { resolveMediaUrl, isVideo } from '@/utils/media'

const router = useRouter()
const route = useRoute()
const uiStore = useUiStore()
const { createDiary, updateDiary } = useDiaries()

const isEditMode = computed(() => Boolean(route.params.id))
const diaryId = computed(() => Number(route.params.id))

// 表单数据
const formData = ref<CreateDiaryRequest>({
  title: '',
  content: '',
  mood: 'happy',
  category: '生活',
  date: dayjs().format('YYYY-MM-DD'),
  is_public: true,
  photo_ids: []
})

const isSubmitting = ref(false)
const isPageLoading = ref(false)
const uploadedPhotos = ref<Photo[]>([])
const isUploading = ref(false)

// 多选模式状态
const isSelectMode = ref(false)
const selectedPhotoIds = ref<Set<number>>(new Set())
const showMoveDialog = ref(false)
const targetDiaryId = ref<number | null>(null)
const availableDiaries = ref<Diary[]>([])
const isMoving = ref(false)

const selectedCount = computed(() => selectedPhotoIds.value.size)

// 心情选项
const moodOptions: { value: Mood; label: string; emoji: string }[] = [
  { value: 'happy', label: '开心', emoji: '😊' },
  { value: 'sad', label: '伤心', emoji: '😩' },
  { value: 'excited', label: '兴奋', emoji: '🤩' },
  { value: 'calm', label: '平静', emoji: '😌' },
  { value: 'angry', label: '生气', emoji: '😧' },
  { value: 'tired', label: '疲惫', emoji: '😾' },
  { value: 'loved', label: '被爱', emoji: '😍' },
  { value: 'grateful', label: '感恩', emoji: '🙏' },
]

// 分类选项
const categoryOptions = ['生活', '工作', '学习', '旅行', '美食', '运动', '娱乐', '其他']

const loadDiaryForEdit = async () => {
  if (!isEditMode.value) {
    return
  }

  if (!Number.isFinite(diaryId.value)) {
    uiStore.showToast('日记参数错误', 'error')
    router.push('/diaries')
    return
  }

  isPageLoading.value = true
  try {
    const response = await diaryService.getDiary(diaryId.value)
    const diary = response.diary

    formData.value = {
      title: diary.title,
      content: diary.content,
      mood: diary.mood,
      category: diary.category,
      date: diary.date,
      is_public: diary.is_public !== false,
      photo_ids: (diary.attached_photos || []).map(photo => photo.id),
    }
    uploadedPhotos.value = [...(diary.attached_photos || [])]
  } catch (error) {
    console.error('Load diary detail error:', error)
    uiStore.showToast('加载日记失败', 'error')
    router.push('/diaries')
  } finally {
    isPageLoading.value = false
  }
}

// 通用图片上传函数
const uploadImageFiles = async (files: File[]) => {
  if (files.length === 0) return

  isUploading.value = true
  try {
    const uploadFormData = new FormData()
    files.forEach((file) => {
      uploadFormData.append('photos', file)
    })

    const response = await photoService.uploadPhotos(uploadFormData)
    const newPhotos = response.photos || []

    uploadedPhotos.value = [...uploadedPhotos.value, ...newPhotos]

    const ids = new Set<number>(formData.value.photo_ids || [])
    newPhotos.forEach((photo) => ids.add(photo.id))
    formData.value.photo_ids = Array.from(ids)

    uiStore.showToast(`已上传 ${newPhotos.length} 个文件`, 'success')
  } catch (error) {
    console.error('Upload image error:', error)
    uiStore.showToast('文件上传失败，请稍后重试', 'error')
  } finally {
    isUploading.value = false
  }
}

// 处理文件选择上传
const handleSelectPhotos = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files ? Array.from(target.files) : []

  await uploadImageFiles(files)
  target.value = ''
}

// 处理剪贴板粘贴图片/视频
const handlePaste = async (event: ClipboardEvent) => {
  const items = event.clipboardData?.items
  if (!items) return

  const mediaFiles: File[] = []

  for (let i = 0; i < items.length; i++) {
    const item = items[i]
    if (item?.type.startsWith('image/') || item?.type.startsWith('video/')) {
      const file = item?.getAsFile()
      if (file) {
        mediaFiles.push(file)
      }
    }
  }

  if (mediaFiles.length > 0) {
    event.preventDefault()
    await uploadImageFiles(mediaFiles)
  }
}

const removeAttachedPhoto = (photoId: number) => {
  uploadedPhotos.value = uploadedPhotos.value.filter((photo) => photo.id !== photoId)
  formData.value.photo_ids = (formData.value.photo_ids || []).filter((id) => id !== photoId)
}

// ========================================
// 多选管理
// ========================================

// 进入/退出选择模式
const toggleSelectMode = () => {
  isSelectMode.value = !isSelectMode.value
  if (!isSelectMode.value) {
    selectedPhotoIds.value = new Set()
  }
}

// 切换单张照片选中状态
const togglePhotoSelect = (id: number) => {
  const s = new Set(selectedPhotoIds.value)
  s.has(id) ? s.delete(id) : s.add(id)
  selectedPhotoIds.value = s
}

// 批量删除（从当前日记移除，不删除照片文件）
const deleteSelected = () => {
  const ids = selectedPhotoIds.value
  uploadedPhotos.value = uploadedPhotos.value.filter(p => !ids.has(p.id))
  formData.value.photo_ids = (formData.value.photo_ids || []).filter(id => !ids.has(id))
  selectedPhotoIds.value = new Set()
  isSelectMode.value = false
}

// 打开移动对话框（加载日记列表）
const openMoveDialog = async () => {
  try {
    const response = await diaryService.getDiaries({ page_size: 100 } as any)
    availableDiaries.value = response.diaries.filter(d => d.id !== diaryId.value)
  } catch {
    availableDiaries.value = []
  }
  targetDiaryId.value = null
  showMoveDialog.value = true
}

// 确认移动照片到目标日记
const confirmMove = async () => {
  if (!targetDiaryId.value) return
  isMoving.value = true
  try {
    const ids = [...selectedPhotoIds.value]
    await diaryService.attachPhotos(targetDiaryId.value, ids)
    // 从本篇表单中移除（保存时最终生效）
    uploadedPhotos.value = uploadedPhotos.value.filter(p => !selectedPhotoIds.value.has(p.id))
    formData.value.photo_ids = (formData.value.photo_ids || []).filter(id => !selectedPhotoIds.value.has(id))
    selectedPhotoIds.value = new Set()
    isSelectMode.value = false
    showMoveDialog.value = false
    uiStore.showToast(`已移动 ${ids.length} 张照片`, 'success')
  } catch {
    uiStore.showToast('移动失败，请重试', 'error')
  } finally {
    isMoving.value = false
  }
}

// 保存日记
const saveDiary = async () => {
  if (!formData.value.title.trim()) {
    uiStore.showToast('请输入日记标题', 'warning')
    return
  }

  isSubmitting.value = true
  try {
    const payload = {
      ...formData.value,
      photo_ids: [...(formData.value.photo_ids || [])],
    }

    const savedDiary = isEditMode.value
      ? await updateDiary(diaryId.value, payload)
      : await createDiary(payload)

    uiStore.showToast(isEditMode.value ? '日记更新成功' : '日记保存成功', 'success')
    router.push(`/diaries/${savedDiary.id}`)
  } catch (error) {
    console.error('Save diary error:', error)
    uiStore.showToast('保存失败，请稍后重试', 'error')
  } finally {
    isSubmitting.value = false
  }
}

// 返回列表
const goBack = () => {
  if (isEditMode.value && Number.isFinite(diaryId.value)) {
    router.push(`/diaries/${diaryId.value}`)
    return
  }
  router.push('/diaries')
}

onMounted(() => {
  loadDiaryForEdit()
})
</script>

<template>
  <div class="diary-editor-page">
    <!-- 头部 -->
    <div class="editor-header">
      <h1 class="page-title">{{ isEditMode ? '编辑日记' : '写日记' }}</h1>
      <div class="header-actions">
        <button @click="goBack" class="btn-secondary">
          <X :size="16" />
          <span class="ml-2">取消</span>
        </button>
        <button @click="saveDiary" class="btn-primary" :disabled="isSubmitting">
          <Save :size="16" />
          <span class="ml-2">{{ isSubmitting ? '保存中...' : '保存' }}</span>
        </button>
      </div>
    </div>

    <div v-if="isPageLoading" class="loading-container">
      <div class="spinner"></div>
    </div>

    <!-- 表单 -->
    <div v-else class="editor-form">
      <!-- 标题 -->
      <div class="form-group">
        <label class="form-label">标题</label>
        <input
          v-model="formData.title"
          type="text"
          class="input-field"
              placeholder="给日记起个标题吧..."
        />
      </div>

      <!-- 日期和心情 -->
      <div class="form-row">
        <div class="form-group flex-1">
          <label class="form-label">日期</label>
          <input
            v-model="formData.date"
            type="date"
            class="input-field"
          />
        </div>
        <div class="form-group flex-1">
          <label class="form-label">心情</label>
          <select v-model="formData.mood" class="input-field">
            <option v-for="mood in moodOptions" :key="mood.value" :value="mood.value">
              {{ mood.emoji }} {{ mood.label }}
            </option>
          </select>
        </div>
      </div>

      <!-- 分类与可见性 -->
      <div class="form-row">
        <div class="form-group flex-1">
          <label class="form-label">分类</label>
          <select v-model="formData.category" class="input-field">
            <option v-for="cat in categoryOptions" :key="cat" :value="cat">
              {{ cat }}
            </option>
          </select>
        </div>
        <div class="form-group flex-1">
          <label class="form-label">可见性</label>
          <div class="visibility-toggle">
            <label class="radio-option" :class="{ active: formData.is_public !== false }">
              <input type="radio" :value="true" v-model="formData.is_public" />
              <span>🌐 公开</span>
            </label>
            <label class="radio-option" :class="{ active: formData.is_public === false }">
              <input type="radio" :value="false" v-model="formData.is_public" />
              <span>🔒 私密</span>
            </label>
          </div>
        </div>
      </div>

      <!-- 内容 -->
      <div class="form-group">
        <label class="form-label">内容</label>
        <textarea
          v-model="formData.content"
          class="content-textarea"
          placeholder="记录今天发生了什么..."
          rows="12"
          @paste="handlePaste"
        ></textarea>
        <p class="help-text">支持 Markdown 语法，可直接粘贴图片上传</p>
      </div>

      <!-- 照片/视频管理区 -->
      <div class="form-group">
        <!-- 工具栏 -->
        <div class="photo-toolbar">
          <label class="form-label">添加图片或视频</label>
          <!-- 编辑模式且有照片时，显示多选操作按钮 -->
          <div v-if="isEditMode && uploadedPhotos.length > 0" class="photo-actions">
            <button v-if="!isSelectMode" type="button" class="btn-select" @click="toggleSelectMode">
              选择
            </button>
            <template v-else>
              <button
                type="button"
                class="btn-delete-selected"
                :disabled="selectedCount === 0"
                @click="deleteSelected"
              >
                删除 ({{ selectedCount }})
              </button>
              <button
                type="button"
                class="btn-move-selected"
                :disabled="selectedCount === 0"
                @click="openMoveDialog"
              >
                移动到其他日记 ({{ selectedCount }})
              </button>
              <button type="button" class="btn-cancel-select" @click="toggleSelectMode">
                取消
              </button>
            </template>
          </div>
        </div>

        <div class="upload-card">
          <input
            id="diary-photo-input"
            type="file"
            accept="image/*,video/*"
            multiple
            class="photo-input"
            @change="handleSelectPhotos"
          />
          <label for="diary-photo-input" class="btn-upload" :class="{ disabled: isUploading }">
            {{ isUploading ? '上传中...' : '选择图片或视频并上传' }}
          </label>
        </div>

        <div v-if="uploadedPhotos.length > 0" class="attached-list">
          <div
            v-for="photo in uploadedPhotos"
            :key="photo.id"
            class="attached-item"
            :class="{ 'is-selected': selectedPhotoIds.has(photo.id), 'select-mode': isSelectMode }"
            @click="isSelectMode ? togglePhotoSelect(photo.id) : undefined"
          >
            <video
              v-if="isVideo(photo)"
              :src="resolveMediaUrl(photo.url || '')"
              class="attached-image"
              muted
              preload="metadata"
            />
            <img
              v-else
              :src="resolveMediaUrl(photo.url || photo.thumbnail_url || '')"
              :alt="photo.original_name"
              class="attached-image"
            />
            <!-- 选中覆盖层 -->
            <div v-if="isSelectMode" class="select-overlay">
              <span class="select-check" :class="{ checked: selectedPhotoIds.has(photo.id) }">✓</span>
            </div>
            <!-- 非选择模式保留移除按钮 -->
            <button v-if="!isSelectMode" class="attached-remove" @click="removeAttachedPhoto(photo.id)">
              移除
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 移动照片对话框 -->
    <div v-if="showMoveDialog" class="move-dialog-overlay" @click.self="showMoveDialog = false">
      <div class="move-dialog">
        <h3 class="move-dialog-title">选择目标日记</h3>
        <div class="diary-select-list">
          <button
            v-for="d in availableDiaries"
            :key="d.id"
            type="button"
            class="diary-select-item"
            :class="{ active: targetDiaryId === d.id }"
            @click="targetDiaryId = d.id"
          >
            <span class="diary-select-title">{{ d.title }}</span>
            <span class="diary-select-date">{{ d.date }}</span>
          </button>
          <p v-if="availableDiaries.length === 0" class="no-diaries">暂无其他日记</p>
        </div>
        <div class="move-dialog-actions">
          <button type="button" class="btn-secondary" @click="showMoveDialog = false">取消</button>
          <button
            type="button"
            class="btn-primary"
            :disabled="!targetDiaryId || isMoving"
            @click="confirmMove"
          >
            {{ isMoving ? '移动中...' : '确认移动' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.diary-editor-page {
  width: 100%;
  max-width: 56rem;
  margin: 0 auto;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.25rem;
  gap: 0.75rem;
}

.page-title {
  margin: 0;
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--text-primary);
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.btn-primary,
.btn-secondary {
  display: inline-flex;
  align-items: center;
  padding: 0.625rem 1.2rem;
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform var(--dur-fast), box-shadow var(--dur-base), background-color var(--dur-base), border-color var(--dur-base), color var(--dur-base);
}

.btn-primary {
  border: none;
  background: linear-gradient(135deg, var(--pink-500) 0%, var(--rose-500) 100%);
  color: #fff;
  box-shadow: 0 8px 16px rgba(217, 117, 154, 0.24);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 12px 22px rgba(217, 117, 154, 0.3);
}

.btn-primary:disabled {
  opacity: 0.62;
  cursor: not-allowed;
}

.btn-secondary {
  background: #fff;
  color: var(--text-secondary);
  border: 1px solid var(--border-soft);
}

.btn-secondary:hover {
  background: var(--pink-50);
  color: var(--text-primary);
  border-color: var(--border-strong);
  transform: translateY(-1px);
}

.editor-form {
  background: var(--bg-elevated);
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-lg);
  padding: 1.25rem;
  box-shadow: var(--shadow-soft);
}

.loading-container {
  background: var(--bg-elevated);
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-lg);
  min-height: 220px;
  display: grid;
  place-items: center;
}

.spinner {
  width: 1.9rem;
  height: 1.9rem;
  border: 3px solid #f3f3f3;
  border-top: 3px solid var(--pink-500);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.form-group {
  margin-bottom: 1.1rem;
}

.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 0.45rem;
}

.input-field {
  width: 100%;
  padding: 0.625rem 0.875rem;
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  color: var(--text-primary);
  background: #fff;
  transition: border-color var(--dur-base), box-shadow var(--dur-base), background-color var(--dur-base);
}

.input-field:focus {
  outline: none;
  border-color: var(--pink-300);
  box-shadow: var(--shadow-focus);
  background-color: #fff9fc;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

.content-textarea {
  width: 100%;
  padding: 0.875rem;
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-md);
  font-size: 0.875rem;
  color: var(--text-primary);
  background: #fff;
  font-family: inherit;
  line-height: 1.6;
  resize: vertical;
  min-height: 220px;
  transition: border-color var(--dur-base), box-shadow var(--dur-base), background-color var(--dur-base);
}

.content-textarea:focus {
  outline: none;
  border-color: var(--pink-300);
  box-shadow: var(--shadow-focus);
  background-color: #fff9fc;
}

.help-text {
  font-size: 0.75rem;
  color: var(--text-secondary);
  margin-top: 0.5rem;
}

.upload-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.photo-input {
  display: none;
}

.btn-upload {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.625rem 1rem;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-soft);
  background: #fff;
  color: var(--text-secondary);
  cursor: pointer;
  transition: transform var(--dur-fast), background-color var(--dur-base), border-color var(--dur-base), color var(--dur-base);
}

.btn-upload:hover {
  background: var(--pink-50);
  color: var(--text-primary);
  border-color: var(--border-strong);
}

.btn-upload.disabled {
  opacity: 0.6;
  cursor: not-allowed;
  pointer-events: none;
}

.attached-list {
  margin-top: 0.75rem;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(112px, 1fr));
  gap: 0.6rem;
}

.attached-item {
  position: relative;
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-sm);
  overflow: hidden;
  background: #fff;
  transition: border-color var(--dur-fast);
}

.attached-item.select-mode {
  cursor: pointer;
}

.attached-item.is-selected {
  border-color: var(--pink-400);
  box-shadow: 0 0 0 2px rgba(217, 117, 154, 0.35);
}

.attached-image {
  width: 100%;
  aspect-ratio: 1 / 1;
  object-fit: cover;
  display: block;
}

.attached-remove {
  width: 100%;
  border: none;
  border-top: 1px solid var(--border-soft);
  background: #fff;
  color: #a55674;
  cursor: pointer;
  padding: 0.4rem 0;
  font-size: 0.78rem;
}

/* 多选相关 */
.photo-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 0.45rem;
}

.photo-toolbar .form-label {
  margin-bottom: 0;
}

.photo-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.btn-select,
.btn-cancel-select {
  padding: 0.3rem 0.75rem;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-soft);
  background: #fff;
  color: var(--text-secondary);
  font-size: 0.8rem;
  cursor: pointer;
  transition: background-color var(--dur-base), color var(--dur-base);
}

.btn-select:hover,
.btn-cancel-select:hover {
  background: var(--pink-50);
  color: var(--text-primary);
}

.btn-delete-selected {
  padding: 0.3rem 0.75rem;
  border-radius: var(--radius-sm);
  border: 1px solid #fca5a5;
  background: #fff1f1;
  color: #b91c1c;
  font-size: 0.8rem;
  cursor: pointer;
  transition: background-color var(--dur-base);
}

.btn-delete-selected:hover:not(:disabled) {
  background: #fee2e2;
}

.btn-delete-selected:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.btn-move-selected {
  padding: 0.3rem 0.75rem;
  border-radius: var(--radius-sm);
  border: none;
  background: linear-gradient(135deg, var(--pink-500) 0%, var(--rose-500) 100%);
  color: #fff;
  font-size: 0.8rem;
  cursor: pointer;
  transition: opacity var(--dur-base);
}

.btn-move-selected:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.select-overlay {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.15);
  display: flex;
  align-items: flex-start;
  justify-content: flex-end;
  padding: 0.3rem;
}

.select-check {
  width: 1.4rem;
  height: 1.4rem;
  border-radius: 50%;
  border: 2px solid #fff;
  background: rgba(0, 0, 0, 0.25);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  color: transparent;
  transition: background-color var(--dur-fast), color var(--dur-fast);
}

.select-check.checked {
  background: var(--pink-500);
  color: #fff;
}

/* 移动对话框 */
.move-dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.45);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  padding: 1rem;
}

.move-dialog {
  background: #fff;
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  width: 100%;
  max-width: 400px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
}

.move-dialog-title {
  font-size: 1rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 1rem;
}

.diary-select-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  margin-bottom: 1rem;
  max-height: 50vh;
}

.diary-select-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.6rem 0.875rem;
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-sm);
  background: #fff;
  cursor: pointer;
  text-align: left;
  transition: border-color var(--dur-fast), background-color var(--dur-fast);
}

.diary-select-item:hover {
  background: var(--pink-50);
  border-color: var(--pink-200);
}

.diary-select-item.active {
  border-color: var(--pink-400);
  background: var(--pink-50);
}

.diary-select-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 70%;
}

.diary-select-date {
  font-size: 0.75rem;
  color: var(--text-secondary);
  flex-shrink: 0;
}

.no-diaries {
  text-align: center;
  color: var(--text-secondary);
  font-size: 0.875rem;
  padding: 1.5rem 0;
}

.move-dialog-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

.ml-2 {
  margin-left: 0.5rem;
}

.visibility-toggle {
  display: flex;
  gap: 0.5rem;
}

.radio-option {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.5rem 0.875rem;
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  color: var(--text-secondary);
  cursor: pointer;
  transition: border-color var(--dur-base), background-color var(--dur-base), color var(--dur-base);
  flex: 1;
  justify-content: center;
}

.radio-option input[type="radio"] {
  display: none;
}

.radio-option.active {
  border-color: var(--pink-300);
  background: var(--pink-50);
  color: var(--text-primary);
  font-weight: 600;
}

@media (min-width: 640px) {
  .form-row {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .editor-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-actions {
    width: 100%;
  }

  .btn-primary,
  .btn-secondary {
    flex: 1;
    justify-content: center;
  }

  .photo-toolbar {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .photo-actions {
    width: 100%;
  }

  .btn-move-selected {
    font-size: 0.75rem;
  }
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
