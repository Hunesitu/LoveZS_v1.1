<!--
DiaryDetail 页面
日记详情查看，支持图片放大预览
-->
<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Edit2, X } from 'lucide-vue-next'
import dayjs from 'dayjs'
import { useUiStore } from '@/stores/ui'
import { resolveMediaUrl } from '@/utils/media'
import diaryService from '@/api/diary'
import type { Diary, Photo } from '@/types'

const route = useRoute()
const router = useRouter()
const uiStore = useUiStore()

const diary = ref<Diary | null>(null)
const isLoading = ref(false)
const previewPhoto = ref<Photo | null>(null)

const diaryId = computed(() => Number(route.params.id))

const getMoodEmoji = (mood: string) => {
  const moodEmojis: Record<string, string> = {
    happy: '😊',
    sad: '😩',
    excited: '🤩',
    calm: '😌',
    angry: '😧',
    tired: '😾',
    loved: '😍',
    grateful: '🙏',
  }
  return moodEmojis[mood] || '😊'
}

const getDiaryDetail = async () => {
  if (!Number.isFinite(diaryId.value)) {
    uiStore.showToast('日记参数错误', 'error')
    router.push('/diaries')
    return
  }

  isLoading.value = true
  try {
    const response = await diaryService.getDiary(diaryId.value)
    diary.value = response.diary
  } catch (error) {
    console.error('Load diary detail error:', error)
    uiStore.showToast('加载日记失败', 'error')
    router.push('/diaries')
  } finally {
    isLoading.value = false
  }
}

const openPreview = (photo: Photo) => {
  previewPhoto.value = photo
}

const closePreview = () => {
  previewPhoto.value = null
}

const stopBubbling = (event: MouseEvent) => {
  event.stopPropagation()
}

onMounted(() => {
  getDiaryDetail()
})
</script>

<template>
  <div class="diary-detail-page">
    <div class="detail-header">
      <button class="btn-secondary" @click="router.push('/diaries')">
        <ArrowLeft :size="16" />
        <span class="ml-2">返回列表</span>
      </button>
      <button
        v-if="diary"
        class="btn-primary"
        @click="router.push(`/diaries/${diary.id}/edit`)"
      >
        <Edit2 :size="16" />
        <span class="ml-2">编辑</span>
      </button>
    </div>

    <div v-if="isLoading" class="loading-container">
      <div class="spinner"></div>
    </div>

    <article v-else-if="diary" class="detail-card">
      <header class="card-header">
        <div class="title-wrap">
          <span class="mood-emoji">{{ getMoodEmoji(diary.mood) }}</span>
          <h1 class="title">{{ diary.title }}</h1>
        </div>
        <div class="meta-line">
          <span>{{ dayjs(diary.date).format('YYYY-MM-DD') }}</span>
          <span>·</span>
          <span>{{ diary.category }}</span>
          <span v-if="diary.word_count">· {{ diary.word_count }} 词</span>
        </div>
      </header>

      <section v-if="diary.tags?.length" class="tags-line">
        <span v-for="tag in diary.tags" :key="tag" class="tag-item">#{{ tag }}</span>
      </section>

      <section class="content-section">
        <pre class="content-text">{{ diary.content }}</pre>
      </section>

      <section
        v-if="diary.attached_photos && diary.attached_photos.length > 0"
        class="photos-section"
      >
        <h3 class="photos-title">关联图片（{{ diary.attached_photos.length }}）</h3>
        <div class="photos-grid">
          <button
            v-for="photo in diary.attached_photos"
            :key="photo.id"
            class="photo-item"
            @click="openPreview(photo)"
          >
            <img
              :src="resolveMediaUrl(photo.url || photo.thumbnail_url || '')"
              :alt="photo.original_name"
              class="photo-image"
              loading="lazy"
            />
          </button>
        </div>
      </section>
    </article>

    <div v-else class="empty-state-card">
      <p>未找到该日记</p>
    </div>

    <div
      v-if="previewPhoto"
      class="preview-overlay"
      role="dialog"
      aria-modal="true"
      @click="closePreview"
    >
      <div class="preview-content" @click="stopBubbling">
        <button class="preview-close" @click="closePreview" aria-label="关闭预览">
          <X :size="18" />
        </button>
        <img
          :src="resolveMediaUrl(previewPhoto.url || previewPhoto.thumbnail_url || '')"
          :alt="previewPhoto.original_name"
          class="preview-image"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.diary-detail-page {
  width: 100%;
  max-width: 56rem;
  margin: 0 auto;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
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

.btn-secondary {
  background: #fff;
  color: var(--text-secondary);
  border: 1px solid var(--border-soft);
}

.detail-card {
  background: var(--bg-elevated);
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-lg);
  padding: 1.25rem;
  box-shadow: var(--shadow-soft);
}

.card-header {
  margin-bottom: 1rem;
}

.title-wrap {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.title {
  margin: 0;
  font-size: 1.55rem;
  color: var(--text-primary);
}

.meta-line {
  margin-top: 0.45rem;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  color: var(--text-secondary);
  font-size: 0.875rem;
}

.mood-emoji {
  font-size: 1.3rem;
}

.tags-line {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  margin-bottom: 1rem;
}

.tag-item {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.55rem;
  background: #ffeaf3;
  color: #a55674;
  border-radius: 999px;
  font-size: 0.8125rem;
  font-weight: 500;
}

.content-section {
  margin-bottom: 1.25rem;
}

.content-text {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 0.95rem;
  line-height: 1.8;
  color: var(--text-primary);
  font-family: inherit;
}

.photos-title {
  margin: 0 0 0.65rem;
  color: var(--text-primary);
  font-size: 0.95rem;
}

.photos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(220px, 100%), 1fr));
  gap: 0.75rem;
}

.photo-item {
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-sm);
  padding: 0;
  cursor: zoom-in;
  overflow: hidden;
  background: #fff;
}

.photo-image {
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
  display: block;
}

.preview-overlay {
  position: fixed;
  inset: 0;
  z-index: 100;
  background: rgba(0, 0, 0, 0.72);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: clamp(0.5rem, 2vw, 1.25rem);
}

.preview-content {
  position: relative;
  width: min(96vw, 1400px);
  max-height: calc(100vh - 1rem);
  display: flex;
  align-items: center;
  justify-content: center;
}

.preview-image {
  display: block;
  max-width: 100%;
  max-height: calc(100vh - 1rem);
  width: auto;
  height: auto;
  object-fit: contain;
  border-radius: var(--radius-md);
}

.preview-close {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  border: none;
  width: 2rem;
  height: 2rem;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.45);
  color: #fff;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.loading-container,
.empty-state-card {
  background: var(--bg-elevated);
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-lg);
  min-height: 160px;
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

.ml-2 {
  margin-left: 0.5rem;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

@media (max-width: 640px) {
  .detail-header {
    flex-direction: column;
    align-items: stretch;
  }

  .btn-primary,
  .btn-secondary {
    justify-content: center;
  }

  .photos-grid {
    grid-template-columns: repeat(auto-fit, minmax(min(160px, 100%), 1fr));
  }
}
</style>
