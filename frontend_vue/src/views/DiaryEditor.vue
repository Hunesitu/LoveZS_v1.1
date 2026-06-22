<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Save, Upload, X } from 'lucide-vue-next'
import dayjs from 'dayjs'
import { useDiaries } from '@/composables/useDiaries'
import { useUiStore } from '@/stores/ui'
import diaryService from '@/api/diary'
import photoService from '@/api/photo'
import { getMediaUrl, isVideo } from '@/utils/media'
import { MOOD_EMOJIS, MOOD_LABELS, type CreateDiaryRequest, type Diary, type Mood, type Photo } from '@/types'

const router = useRouter()
const route = useRoute()
const uiStore = useUiStore()
const { createDiary, updateDiary } = useDiaries()

const isEditMode = computed(() => Boolean(route.params.id))
const diaryId = computed(() => Number(route.params.id))
const formData = ref<CreateDiaryRequest>({
  title: '',
  content: '',
  mood: 'happy',
  category: '生活',
  date: dayjs().format('YYYY-MM-DD'),
  is_public: true,
  photo_ids: [],
})

const isSubmitting = ref(false)
const isPageLoading = ref(false)
const uploadedPhotos = ref<Photo[]>([])
const isUploading = ref(false)
const isSelectMode = ref(false)
const selectedPhotoIds = ref<Set<number>>(new Set())
const showMoveDialog = ref(false)
const targetDiaryId = ref<number | null>(null)
const availableDiaries = ref<Diary[]>([])
const isMoving = ref(false)

const moodOptions = Object.entries(MOOD_LABELS).map(([value, label]) => ({
  value: value as Mood,
  label,
  emoji: MOOD_EMOJIS[value as Mood],
}))
const categoryOptions = ['生活', '工作', '学习', '旅行', '美食', '运动', '娱乐', '其他']
const selectedCount = computed(() => selectedPhotoIds.value.size)
const uploadProgressText = ref('')

const MAX_IMAGE_SIZE = 10 * 1024 * 1024
const MAX_VIDEO_SIZE = 100 * 1024 * 1024
const MAX_BATCH_FILES = 8
const MAX_BATCH_SIZE = 80 * 1024 * 1024

const validateMediaFiles = (files: File[]) => {
  const validFiles: File[] = []
  const rejectedFiles: string[] = []

  files.forEach((file) => {
    const isImage = file.type.startsWith('image/')
    const isVideoFile = file.type.startsWith('video/')

    if (!isImage && !isVideoFile) {
      rejectedFiles.push(`${file.name} 不是图片或视频`)
      return
    }

    const maxSize = isImage ? MAX_IMAGE_SIZE : MAX_VIDEO_SIZE
    if (file.size > maxSize) {
      rejectedFiles.push(`${file.name} 超过 ${isImage ? '10MB' : '100MB'}`)
      return
    }

    validFiles.push(file)
  })

  return { validFiles, rejectedFiles }
}

const chunkFiles = (files: File[]) => {
  const batches: File[][] = []
  let currentBatch: File[] = []
  let currentSize = 0

  files.forEach((file) => {
    const wouldExceedFiles = currentBatch.length >= MAX_BATCH_FILES
    const wouldExceedSize = currentSize > 0 && currentSize + file.size > MAX_BATCH_SIZE

    if (wouldExceedFiles || wouldExceedSize) {
      batches.push(currentBatch)
      currentBatch = []
      currentSize = 0
    }

    currentBatch.push(file)
    currentSize += file.size
  })

  if (currentBatch.length) {
    batches.push(currentBatch)
  }

  return batches
}

const loadDiaryForEdit = async () => {
  if (!isEditMode.value) return
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

const uploadMediaFiles = async (files: File[]) => {
  if (!files.length) return

  const { validFiles, rejectedFiles } = validateMediaFiles(files)
  if (rejectedFiles.length) {
    uiStore.showToast(`已跳过 ${rejectedFiles.length} 个文件：${rejectedFiles[0]}`, 'warning')
  }
  if (!validFiles.length) return

  const batches = chunkFiles(validFiles)
  let uploadedCount = 0

  isUploading.value = true
  try {
    for (const [index, batch] of batches.entries()) {
      uploadProgressText.value = batches.length > 1
        ? `正在上传第 ${index + 1}/${batches.length} 批`
        : '上传中...'

      const uploadFormData = new FormData()
      batch.forEach(file => uploadFormData.append('photos', file))
      const response = await photoService.uploadPhotos(uploadFormData)
      const newPhotos = response.photos || []
      uploadedPhotos.value = [...uploadedPhotos.value, ...newPhotos]
      const ids = new Set(formData.value.photo_ids || [])
      newPhotos.forEach(photo => ids.add(photo.id))
      formData.value.photo_ids = Array.from(ids)
      uploadedCount += newPhotos.length
    }

    uiStore.showToast(`已上传 ${uploadedCount} 个文件`, 'success')
  } catch (error) {
    console.error('Upload media error:', error)
    uiStore.showToast('文件上传失败，请稍后重试', 'error')
  } finally {
    isUploading.value = false
    uploadProgressText.value = ''
  }
}

const handleSelectPhotos = async (event: Event) => {
  const input = event.target as HTMLInputElement
  await uploadMediaFiles(input.files ? Array.from(input.files) : [])
  input.value = ''
}

const handlePaste = async (event: ClipboardEvent) => {
  const items = event.clipboardData?.items
  if (!items) return
  const files: File[] = []
  for (const item of Array.from(items)) {
    if (item.type.startsWith('image/') || item.type.startsWith('video/')) {
      const file = item.getAsFile()
      if (file) files.push(file)
    }
  }
  if (files.length) {
    event.preventDefault()
    await uploadMediaFiles(files)
  }
}

const removeAttachedPhoto = (photoId: number) => {
  uploadedPhotos.value = uploadedPhotos.value.filter(photo => photo.id !== photoId)
  formData.value.photo_ids = (formData.value.photo_ids || []).filter(id => id !== photoId)
}

const toggleSelectMode = () => {
  isSelectMode.value = !isSelectMode.value
  if (!isSelectMode.value) selectedPhotoIds.value = new Set()
}

const togglePhotoSelect = (id: number) => {
  const selected = new Set(selectedPhotoIds.value)
  selected.has(id) ? selected.delete(id) : selected.add(id)
  selectedPhotoIds.value = selected
}

const deleteSelected = () => {
  const ids = selectedPhotoIds.value
  uploadedPhotos.value = uploadedPhotos.value.filter(photo => !ids.has(photo.id))
  formData.value.photo_ids = (formData.value.photo_ids || []).filter(id => !ids.has(id))
  selectedPhotoIds.value = new Set()
  isSelectMode.value = false
}

const openMoveDialog = async () => {
  try {
    const response = await diaryService.getDiaries({ page_size: 100 })
    availableDiaries.value = response.diaries.filter(diary => diary.id !== diaryId.value)
  } catch {
    availableDiaries.value = []
  }
  targetDiaryId.value = null
  showMoveDialog.value = true
}

const confirmMove = async () => {
  if (!targetDiaryId.value) return
  isMoving.value = true
  try {
    const ids = [...selectedPhotoIds.value]
    await diaryService.attachPhotos(targetDiaryId.value, ids)
    uploadedPhotos.value = uploadedPhotos.value.filter(photo => !selectedPhotoIds.value.has(photo.id))
    formData.value.photo_ids = (formData.value.photo_ids || []).filter(id => !selectedPhotoIds.value.has(id))
    selectedPhotoIds.value = new Set()
    isSelectMode.value = false
    showMoveDialog.value = false
    uiStore.showToast(`已移动 ${ids.length} 个文件`, 'success')
  } catch {
    uiStore.showToast('移动失败，请重试', 'error')
  } finally {
    isMoving.value = false
  }
}

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

const goBack = () => {
  if (isEditMode.value && Number.isFinite(diaryId.value)) {
    router.push(`/diaries/${diaryId.value}`)
    return
  }
  router.push('/diaries')
}

onMounted(loadDiaryForEdit)
</script>

<template>
  <div class="diary-editor-page page-narrow">
    <div class="page-header">
      <div>
        <p class="romance-kicker">Write The Next Scene</p>
        <h1 class="page-title">{{ isEditMode ? '编辑日记' : '写日记' }}</h1>
        <p class="page-subtitle">把今天的光、声音和心跳，慢慢写进这一幕。</p>
      </div>
      <div class="header-actions">
        <button type="button" class="btn-secondary" @click="goBack">
          <X :size="16" />
          取消
        </button>
        <button type="button" class="btn-primary" :disabled="isSubmitting" @click="saveDiary">
          <Save :size="16" />
          {{ isSubmitting ? '保存中...' : '保存' }}
        </button>
      </div>
    </div>

    <div v-if="isPageLoading" class="loading-container glass-card">
      <div class="spinner"></div>
    </div>

    <form v-else class="editor-form cinematic-frame" @submit.prevent="saveDiary">
      <div class="form-group">
        <label class="form-label" for="diary-title">标题</label>
        <input id="diary-title" v-model="formData.title" type="text" class="input-field" placeholder="比如：今晚的风也很温柔" />
      </div>

      <div class="form-row">
        <div class="form-group">
          <label class="form-label" for="diary-date">日期</label>
          <input id="diary-date" v-model="formData.date" type="date" class="input-field" />
        </div>
        <div class="form-group">
          <label class="form-label" for="diary-mood">心情</label>
          <select id="diary-mood" v-model="formData.mood" class="input-field">
            <option v-for="mood in moodOptions" :key="mood.value" :value="mood.value">
              {{ mood.emoji }} {{ mood.label }}
            </option>
          </select>
        </div>
      </div>

      <div class="form-row">
        <div class="form-group">
          <label class="form-label" for="diary-category">分类</label>
          <select id="diary-category" v-model="formData.category" class="input-field">
            <option v-for="category in categoryOptions" :key="category" :value="category">{{ category }}</option>
          </select>
        </div>
        <div class="form-group">
          <label class="form-label">可见性</label>
          <div class="visibility-toggle">
            <label class="radio-option" :class="{ active: formData.is_public !== false }">
              <input v-model="formData.is_public" type="radio" :value="true" />
              <span>公开</span>
            </label>
            <label class="radio-option" :class="{ active: formData.is_public === false }">
              <input v-model="formData.is_public" type="radio" :value="false" />
              <span>私密</span>
            </label>
          </div>
        </div>
      </div>

      <div class="form-group">
        <label class="form-label" for="diary-content">内容</label>
        <textarea
          id="diary-content"
          v-model="formData.content"
          class="content-textarea"
          placeholder="写下这一幕发生了什么，也写下你想留住的心情..."
          rows="12"
          @paste="handlePaste"
        />
        <p class="help-text">支持 Markdown，可直接粘贴图片或视频上传；素材会成为这篇日记的电影胶片。</p>
      </div>

      <div class="form-group">
        <div class="photo-toolbar">
          <label class="form-label">添加图片或视频胶片</label>
          <div v-if="isEditMode && uploadedPhotos.length > 0" class="photo-actions">
            <button v-if="!isSelectMode" type="button" class="btn-secondary btn-compact" @click="toggleSelectMode">选择</button>
            <template v-else>
              <button type="button" class="btn-secondary btn-compact danger-text" :disabled="selectedCount === 0" @click="deleteSelected">
                删除 {{ selectedCount }}
              </button>
              <button type="button" class="btn-secondary btn-compact" :disabled="selectedCount === 0" @click="openMoveDialog">
                移动 {{ selectedCount }}
              </button>
              <button type="button" class="btn-secondary btn-compact" @click="toggleSelectMode">取消</button>
            </template>
          </div>
        </div>

        <div class="upload-card">
          <input id="diary-photo-input" type="file" accept="image/*,video/*" multiple class="photo-input" @change="handleSelectPhotos" />
          <label for="diary-photo-input" class="btn-upload" :class="{ disabled: isUploading }">
            <Upload :size="16" />
            {{ isUploading ? uploadProgressText || '上传中...' : '选择图片或视频，让画面入镜' }}
          </label>
        </div>

        <div v-if="uploadedPhotos.length > 0" class="attached-list">
          <div
            v-for="photo in uploadedPhotos"
            :key="photo.id"
            class="attached-item"
            :class="{ selected: selectedPhotoIds.has(photo.id), 'select-mode': isSelectMode }"
            @click="isSelectMode ? togglePhotoSelect(photo.id) : undefined"
          >
            <video v-if="isVideo(photo)" :src="getMediaUrl(photo, 'thumbnail')" class="attached-image" muted preload="metadata" />
            <img v-else :src="getMediaUrl(photo, 'thumbnail')" :alt="photo.original_name" class="attached-image" loading="lazy" decoding="async" />
            <div v-if="isSelectMode" class="select-overlay">
              <span class="select-check">{{ selectedPhotoIds.has(photo.id) ? '✓' : '' }}</span>
            </div>
            <button v-if="!isSelectMode" type="button" class="attached-remove" @click="removeAttachedPhoto(photo.id)">移除</button>
          </div>
        </div>
      </div>
    </form>

    <div v-if="showMoveDialog" class="move-dialog-overlay" @click.self="showMoveDialog = false">
      <div class="move-dialog">
        <h2 class="section-title">选择目标日记</h2>
        <div class="diary-select-list">
          <button
            v-for="diary in availableDiaries"
            :key="diary.id"
            type="button"
            class="diary-select-item"
            :class="{ active: targetDiaryId === diary.id }"
            @click="targetDiaryId = diary.id"
          >
            <span>{{ diary.title }}</span>
            <small>{{ diary.date }}</small>
          </button>
          <p v-if="availableDiaries.length === 0" class="no-diaries">暂无其他日记</p>
        </div>
        <div class="move-dialog-actions">
          <button type="button" class="btn-secondary" @click="showMoveDialog = false">取消</button>
          <button type="button" class="btn-primary" :disabled="!targetDiaryId || isMoving" @click="confirmMove">
            {{ isMoving ? '移动中...' : '确认移动' }}
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.header-actions {
  display: flex;
  gap: 0.75rem;
}

.editor-form {
  padding: 1.25rem;
}

.editor-form::before {
  opacity: 0.34;
}

.content-textarea {
  min-height: 220px;
  resize: vertical;
  line-height: 1.7;
}

.help-text {
  margin: 0.5rem 0 0;
  color: var(--ink-soft);
  font-size: 0.78rem;
}

.visibility-toggle,
.photo-actions,
.move-dialog-actions {
  display: flex;
  gap: 0.6rem;
}

.radio-option {
  display: inline-flex;
  flex: 1;
  align-items: center;
  justify-content: center;
  min-height: 42px;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  color: var(--ink-soft);
  background: rgba(255, 255, 255, 0.05);
}

.radio-option input {
  display: none;
}

.radio-option.active {
  color: var(--rose-bright);
  border-color: var(--line-strong);
  background: rgba(240, 120, 182, 0.14);
  font-weight: 700;
}

.photo-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 0.55rem;
}

.btn-compact {
  min-height: 34px;
  padding: 0.35rem 0.75rem;
  font-size: 0.8rem;
}

.danger-text {
  color: var(--danger);
}

.photo-input {
  display: none;
}

.upload-card {
  display: flex;
  padding: 0.85rem;
  border: 1px dashed rgba(245, 200, 143, 0.24);
  border-radius: var(--radius-md);
  background: rgba(245, 200, 143, 0.05);
}

.btn-upload.disabled {
  opacity: 0.6;
  cursor: not-allowed;
  pointer-events: none;
}

.attached-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(112px, 1fr));
  gap: 0.65rem;
  margin-top: 0.85rem;
}

.attached-item {
  position: relative;
  overflow: hidden;
  border: 1px solid rgba(245, 200, 143, 0.14);
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.06);
  transition: transform var(--dur-base) ease, border-color var(--dur-base) ease;
}

.attached-item:hover {
  border-color: var(--line-strong);
  transform: translateY(-2px);
}

.attached-item.select-mode {
  cursor: pointer;
}

.attached-item.selected {
  border-color: var(--rose-bright);
  box-shadow: 0 0 0 2px rgba(240, 120, 182, 0.3);
}

.attached-image {
  width: 100%;
  aspect-ratio: 1 / 1;
  object-fit: cover;
}

.attached-remove {
  width: 100%;
  min-height: 34px;
  border: 0;
  border-top: 1px solid var(--line);
  color: var(--ink-soft);
  background: rgba(255, 255, 255, 0.05);
}

.attached-remove:hover {
  color: var(--danger);
}

.select-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: flex-start;
  justify-content: flex-end;
  padding: 0.35rem;
  background: rgba(0, 0, 0, 0.22);
}

.select-check {
  display: grid;
  place-items: center;
  width: 1.45rem;
  height: 1.45rem;
  border: 2px solid #fff;
  border-radius: 50%;
  color: #fff;
  background: rgba(240, 120, 182, 0.85);
  font-size: 0.8rem;
}

.move-dialog-overlay {
  position: fixed;
  inset: 0;
  z-index: 200;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.62);
  backdrop-filter: blur(5px);
}

.move-dialog {
  display: flex;
  flex-direction: column;
  width: min(100%, 420px);
  max-height: 80vh;
  padding: 1.25rem;
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  background: rgba(18, 16, 36, 0.98);
  box-shadow: var(--shadow-lg);
}

.diary-select-list {
  display: grid;
  gap: 0.5rem;
  max-height: 48vh;
  margin: 1rem 0;
  overflow-y: auto;
}

.diary-select-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.7rem;
  padding: 0.7rem 0.85rem;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  color: var(--ink);
  background: rgba(255, 255, 255, 0.05);
}

.diary-select-item.active,
.diary-select-item:hover {
  border-color: var(--line-strong);
  background: rgba(240, 120, 182, 0.14);
}

.diary-select-item span {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.diary-select-item small,
.no-diaries {
  color: var(--ink-soft);
}

@media (max-width: 640px) {
  .header-actions,
  .visibility-toggle,
  .photo-toolbar,
  .move-dialog-actions {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>
