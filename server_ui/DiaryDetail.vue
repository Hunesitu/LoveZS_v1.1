<!--
DiaryDetail 页面
日记详情查看，支持图片放大预览
-->
<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ArrowLeft, Edit2, X, Trash2, Send, ChevronLeft, ChevronRight, Reply, Pin, ZoomIn, ZoomOut, RotateCcw } from 'lucide-vue-next'
import dayjs from 'dayjs'
import { useUiStore } from '@/stores/ui'
import { useUserStore } from '@/stores/user'
import { resolveMediaUrl, isVideo } from '@/utils/media'
import diaryService, { pinDiary, unpinDiary } from '@/api/diary'
import { api } from '@/api/client'
import type { Diary, Photo, DiaryComment } from '@/types'

const route = useRoute()
const router = useRouter()
const uiStore = useUiStore()
const userStore = useUserStore()

const diary = ref<Diary | null>(null)
const isLoading = ref(false)
const previewIndex = ref(-1)
const previewPhoto = computed(() =>
  previewIndex.value >= 0
    ? diary.value?.attached_photos?.[previewIndex.value] ?? null
    : null
)

// 缩放相关
const scale = ref(1)
const minScale = 0.5
const maxScale = 3

const zoomIn = () => {
  scale.value = Math.min(scale.value + 0.25, maxScale)
}

const zoomOut = () => {
  scale.value = Math.max(scale.value - 0.25, minScale)
}

const resetZoom = () => {
  scale.value = 1
}

const handleWheel = (e: WheelEvent) => {
  e.preventDefault()
  if (e.deltaY < 0) {
    zoomIn()
  } else {
    zoomOut()
  }
}

// 拖动切换相关
const isDragging = ref(false)
const dragStartX = ref(0)
const dragStartY = ref(0)
const dragDeltaX = ref(0)
const dragDeltaY = ref(0)

const onDragStart = (e: MouseEvent | TouchEvent) => {
  isDragging.value = true
  if ('touches' in e) {
    const touch = e.touches[0]
    if (touch) {
      dragStartX.value = touch.clientX
      dragStartY.value = touch.clientY
    }
  } else {
    dragStartX.value = e.clientX
    dragStartY.value = e.clientY
  }
  dragDeltaX.value = 0
  dragDeltaY.value = 0
}

const onDragMove = (e: MouseEvent | TouchEvent) => {
  if (!isDragging.value) return

  let clientX: number, clientY: number
  if ('touches' in e) {
    const touch = e.touches[0]
    if (!touch) return
    clientX = touch.clientX
    clientY = touch.clientY
  } else {
    clientX = e.clientX
    clientY = e.clientY
  }

  dragDeltaX.value = clientX - dragStartX.value
  dragDeltaY.value = clientY - dragStartY.value
}

const onDragEnd = () => {
  if (!isDragging.value) return
  isDragging.value = false

  const threshold = 50 // 拖动阈值

  if (dragDeltaX.value < -threshold && previewIndex.value < photoCount.value - 1) {
    // 向左滑动，切换下一张
    previewIndex.value++
    resetZoom()
  } else if (dragDeltaX.value > threshold && previewIndex.value > 0) {
    // 向右滑动，切换上一张
    previewIndex.value--
    resetZoom()
  }

  dragDeltaX.value = 0
  dragDeltaY.value = 0
}

// 评论相关
const commentContent = ref('')
const isSubmittingComment = ref(false)
const comments = ref<DiaryComment[]>([])

// 回复相关
const replyingTo = ref<DiaryComment | null>(null)
const replyContent = ref('')
const isSubmittingReply = ref(false)

const totalCommentCount = computed(() => {
  return comments.value.reduce((sum, c) => sum + 1 + (c.replies?.length ?? 0), 0)
})

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
    comments.value = response.diary.comments || []
  } catch (error) {
    console.error('Load diary detail error:', error)
    uiStore.showToast('加载日记失败', 'error')
    router.push('/diaries')
  } finally {
    isLoading.value = false
  }
}

const handleTogglePin = async () => {
  if (!diary.value) return

  try {
    if (diary.value.is_pinned) {
      await unpinDiary(diary.value.id)
      diary.value.is_pinned = false
      uiStore.showToast('已取消置顶', 'success')
    } else {
      await pinDiary(diary.value.id)
      diary.value.is_pinned = true
      uiStore.showToast('日记已置顶', 'success')
    }
  } catch (error) {
    console.error('Failed to toggle pin:', error)
    uiStore.showToast('操作失败，请稍后重试', 'error')
  }
}

const openPreview = (photo: Photo) => {
  const idx = diary.value?.attached_photos?.findIndex(p => p.id === photo.id) ?? -1
  previewIndex.value = idx
}

const closePreview = () => {
  previewIndex.value = -1
}

const stopBubbling = (event: MouseEvent) => {
  event.stopPropagation()
}

const photoCount = computed(() => diary.value?.attached_photos?.length ?? 0)

const getInlineMediaUrl = (photo: Photo) =>
  resolveMediaUrl(photo.thumbnail_url || photo.preview_url || photo.url || '')

const getFullMediaUrl = (photo: Photo) =>
  resolveMediaUrl(photo.url || photo.preview_url || photo.thumbnail_url || '')

const prevPhoto = () => {
  if (previewIndex.value > 0) previewIndex.value--
}
const nextPhoto = () => {
  if (previewIndex.value < photoCount.value - 1) previewIndex.value++
}


const submitComment = async () => {
  if (!commentContent.value.trim()) return
  isSubmittingComment.value = true
  try {
    const response = await api.post(`/diaries/${diaryId.value}/comments/`, {
      content: commentContent.value.trim()
    })
    comments.value.unshift(response.data.comment)
    commentContent.value = ''
    uiStore.showToast('评论发表成功', 'success')
  } catch (error) {
    console.error('Submit comment error:', error)
    uiStore.showToast('评论发表失败', 'error')
  } finally {
    isSubmittingComment.value = false
  }
}

const deleteComment = async (commentId: number, parentId?: number | null) => {
  if (!window.confirm('确定删除这条评论吗？')) return
  try {
    await api.delete(`/diaries/${diaryId.value}/comments/${commentId}/`)
    if (parentId) {
      // 删除子回复：从父评论的 replies 中移除
      const parent = comments.value.find(c => c.id === parentId)
      if (parent?.replies) {
        parent.replies = parent.replies.filter(r => r.id !== commentId)
      }
    } else {
      // 删除顶级评论（级联删除由后端处理）
      comments.value = comments.value.filter(c => c.id !== commentId)
    }
    uiStore.showToast('评论已删除', 'success')
  } catch (error) {
    console.error('Delete comment error:', error)
    uiStore.showToast('删除评论失败', 'error')
  }
}

const startReply = (comment: DiaryComment) => {
  replyingTo.value = comment
  replyContent.value = ''
}

const cancelReply = () => {
  replyingTo.value = null
  replyContent.value = ''
}

const submitReply = async () => {
  if (!replyContent.value.trim() || !replyingTo.value) return
  isSubmittingReply.value = true
  try {
    const response = await api.post(`/diaries/${diaryId.value}/comments/`, {
      content: replyContent.value.trim(),
      parent: replyingTo.value.id
    })
    const newReply = response.data.comment
    // 后端强制一级嵌套，找到实际的顶级父评论
    const topParentId = newReply.parent
    const topParent = comments.value.find(c => c.id === topParentId)
    if (topParent) {
      if (!topParent.replies) topParent.replies = []
      topParent.replies.push(newReply)
    }
    cancelReply()
    uiStore.showToast('回复发表成功', 'success')
  } catch (error) {
    console.error('Submit reply error:', error)
    uiStore.showToast('回复发表失败', 'error')
  } finally {
    isSubmittingReply.value = false
  }
}

// 键盘导航
const onKeydown = (e: KeyboardEvent) => {
  if (previewIndex.value < 0) return
  if (e.key === 'ArrowLeft') prevPhoto()
  else if (e.key === 'ArrowRight') nextPhoto()
  else if (e.key === 'Escape') closePreview()
}

onMounted(() => {
  getDiaryDetail()
  window.addEventListener('keydown', onKeydown)
})
onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
})
</script>

<template>
  <div class="diary-detail-page">
    <div class="detail-header">
      <button class="btn-secondary" @click="router.push('/diaries')">
        <ArrowLeft :size="16" />
        <span class="ml-2">返回列表</span>
      </button>
      <div class="header-actions">
        <button
          v-if="diary && (diary.created_by === userStore.user?.id || userStore.isAdmin)"
          class="btn-secondary"
          @click="handleTogglePin"
        >
          <Pin :size="16" :class="{ 'pinned-icon': diary?.is_pinned }" />
          <span class="ml-2">{{ diary?.is_pinned ? '取消置顶' : '置顶' }}</span>
        </button>
        <button
          v-if="diary && diary.created_by === userStore.user?.id"
          class="btn-primary"
          @click="router.push(`/diaries/${diary.id}/edit`)"
        >
          <Edit2 :size="16" />
          <span class="ml-2">编辑</span>
        </button>
      </div>
    </div>

    <div v-if="isLoading" class="loading-container">
      <div class="spinner"></div>
    </div>

    <article v-else-if="diary" class="detail-card">
      <header class="card-header">
        <div class="title-wrap">
          <span class="mood-emoji">{{ getMoodEmoji(diary.mood) }}</span>
          <h1 class="title">
            <span v-if="diary.is_public === false" class="private-badge">🔒</span>
            <span v-if="diary.is_pinned" class="pinned-badge" title="已置顶">📌</span>
            {{ diary.title }}
          </h1>
        </div>
        <div class="meta-line">
          <span>{{ dayjs(diary.created_at).format('YYYY-MM-DD HH:mm:ss') }}</span>
          <span>·</span>
          <span>{{ diary.category }}</span>
          <span v-if="diary.created_by_details">· {{ diary.created_by_details.username }}</span>
          <span v-if="diary.word_count">· {{ diary.word_count }} 词</span>
        </div>
      </header>

      <section class="content-section">
        <pre class="content-text">{{ diary.content }}</pre>
      </section>

      <section
        v-if="diary.attached_photos && diary.attached_photos.length > 0"
        class="photos-section"
      >
        <h3 class="photos-title">关联媒体（{{ diary.attached_photos.length }}）</h3>
        <div class="photos-grid">
          <button
            v-for="photo in diary.attached_photos"
            :key="photo.id"
            class="photo-item"
            @click="openPreview(photo)"
          >
            <div
              v-if="isVideo(photo)"
              class="photo-image photo-video-placeholder"
            />
            <img
              v-else
              :src="getInlineMediaUrl(photo)"
              :alt="photo.original_name"
              class="photo-image"
              loading="lazy"
              decoding="async"
            />
            <span v-if="isVideo(photo)" class="video-badge">▶</span>
          </button>
        </div>
      </section>

      <!-- 评论区 -->
      <section class="comments-section">
        <h3 class="comments-title">评论（{{ totalCommentCount }}）</h3>

        <!-- 发表评论 -->
        <div v-if="userStore.isAuthenticated" class="comment-form">
          <textarea
            v-model="commentContent"
            class="comment-input"
            placeholder="写下你的评论..."
            rows="3"
            maxlength="1000"
          ></textarea>
          <div class="comment-form-actions">
            <span class="char-count">{{ commentContent.length }}/1000</span>
            <button
              class="btn-primary btn-sm"
              :disabled="!commentContent.trim() || isSubmittingComment"
              @click="submitComment"
            >
              <Send :size="14" />
              <span class="ml-2">{{ isSubmittingComment ? '发送中...' : '发表' }}</span>
            </button>
          </div>
        </div>

        <!-- 评论列表 -->
        <div v-if="comments.length > 0" class="comments-list">
          <div v-for="comment in comments" :key="comment.id" class="comment-item">
            <div class="comment-header">
              <span class="comment-author">{{ comment.created_by_details?.username || '匿名' }}</span>
              <span class="comment-time">{{ dayjs(comment.created_at).format('YYYY-MM-DD HH:mm:ss') }}</span>
            </div>
            <p class="comment-content">{{ comment.content }}</p>
            <div class="comment-actions">
              <button
                v-if="userStore.isAuthenticated"
                class="comment-reply-btn"
                @click="startReply(comment)"
              >
                <Reply :size="13" />
                <span>回复</span>
              </button>
              <button
                v-if="comment.created_by === userStore.user?.id"
                class="comment-delete-btn"
                @click="deleteComment(comment.id)"
              >
                <Trash2 :size="13" />
                <span>删除</span>
              </button>
            </div>

            <!-- 内联回复表单 -->
            <div v-if="replyingTo?.id === comment.id" class="reply-form">
              <textarea
                v-model="replyContent"
                class="comment-input"
                :placeholder="`回复 ${comment.created_by_details?.username || '匿名'}...`"
                rows="2"
                maxlength="1000"
              ></textarea>
              <div class="comment-form-actions">
                <span class="char-count">{{ replyContent.length }}/1000</span>
                <div class="reply-form-btns">
                  <button class="btn-secondary btn-sm" @click="cancelReply">取消</button>
                  <button
                    class="btn-primary btn-sm"
                    :disabled="!replyContent.trim() || isSubmittingReply"
                    @click="submitReply"
                  >
                    <Send :size="14" />
                    <span class="ml-2">{{ isSubmittingReply ? '发送中...' : '回复' }}</span>
                  </button>
                </div>
              </div>
            </div>

            <!-- 子回复列表 -->
            <div v-if="comment.replies && comment.replies.length > 0" class="replies-list">
              <div v-for="reply in comment.replies" :key="reply.id" class="reply-item">
                <div class="comment-header">
                  <span class="comment-author">{{ reply.created_by_details?.username || '匿名' }}</span>
                  <span class="comment-time">{{ dayjs(reply.created_at).format('YYYY-MM-DD HH:mm:ss') }}</span>
                </div>
                <p class="comment-content">{{ reply.content }}</p>
                <div class="comment-actions">
                  <button
                    v-if="userStore.isAuthenticated"
                    class="comment-reply-btn"
                    @click="startReply(comment)"
                  >
                    <Reply :size="13" />
                    <span>回复</span>
                  </button>
                  <button
                    v-if="reply.created_by === userStore.user?.id"
                    class="comment-delete-btn"
                    @click="deleteComment(reply.id, comment.id)"
                  >
                    <Trash2 :size="13" />
                    <span>删除</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
        <p v-else class="no-comments">暂无评论</p>
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
      @wheel="handleWheel"
    >
      <div
        class="preview-content"
        @click="stopBubbling"
        @mousedown="onDragStart"
        @mousemove="onDragMove"
        @mouseup="onDragEnd"
        @mouseleave="onDragEnd"
        @touchstart.passive="onDragStart"
        @touchmove.passive="onDragMove"
        @touchend="onDragEnd"
      >
        <button class="preview-close" @click="closePreview" aria-label="关闭预览">
          <X :size="18" />
        </button>

        <!-- 缩放按钮 -->
        <div class="zoom-controls">
          <button class="zoom-btn" @click.stop="zoomOut" :disabled="scale <= minScale" aria-label="缩小">
            <ZoomOut :size="18" />
          </button>
          <span class="zoom-level">{{ Math.round(scale * 100) }}%</span>
          <button class="zoom-btn" @click.stop="zoomIn" :disabled="scale >= maxScale" aria-label="放大">
            <ZoomIn :size="18" />
          </button>
          <button class="zoom-btn" @click.stop="resetZoom" aria-label="重置">
            <RotateCcw :size="18" />
          </button>
        </div>

        <!-- 左箭头 -->
        <button
          v-if="previewIndex > 0"
          class="preview-nav preview-nav--prev"
          @click.stop="prevPhoto(); resetZoom()"
          aria-label="上一张"
        >
          <ChevronLeft :size="28" />
        </button>

        <div
          class="preview-image-wrapper"
          :style="{
            transform: `translateX(${dragDeltaX}px) scale(${scale})`,
            transition: isDragging ? 'none' : 'transform 0.3s ease'
          }"
        >
          <video
            v-if="isVideo(previewPhoto)"
            :src="getFullMediaUrl(previewPhoto)"
            class="preview-image"
            controls
            autoplay
          />
          <img
            v-else
            :src="getFullMediaUrl(previewPhoto)"
            :alt="previewPhoto.original_name"
            class="preview-image"
          />
        </div>

        <!-- 右箭头 -->
        <button
          v-if="previewIndex < photoCount - 1"
          class="preview-nav preview-nav--next"
          @click.stop="nextPhoto(); resetZoom()"
          aria-label="下一张"
        >
          <ChevronRight :size="28" />
        </button>

        <!-- 计数器 -->
        <span v-if="photoCount > 1" class="preview-counter">
          {{ previewIndex + 1 }} / {{ photoCount }}
        </span>
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
  display: flex;
  align-items: center;
  gap: 0.35rem;
}

.private-badge {
  font-size: 0.85em;
  flex-shrink: 0;
}

.pinned-badge {
  font-size: 0.85em;
  flex-shrink: 0;
  margin-right: 4px;
}

.pinned-icon {
  color: var(--pink-500);
  transform: rotate(45deg);
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
  position: relative;
}

.video-badge {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 2.2rem;
  height: 2.2rem;
  border-radius: 50%;
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: none;
}

.photo-image {
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
  display: block;
}

.photo-video-placeholder {
  background: linear-gradient(135deg, #f7d7df 0%, #dbeafe 100%);
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

.preview-image-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  max-width: 100%;
  max-height: calc(100vh - 1rem);
}

.preview-image-wrapper .preview-image {
  max-height: calc(100vh - 1rem);
}

.zoom-controls {
  position: absolute;
  top: 0.5rem;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 0.25rem;
  background: rgba(0, 0, 0, 0.6);
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-md);
  z-index: 10;
}

.zoom-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.75rem;
  height: 1.75rem;
  background: transparent;
  border: none;
  color: #fff;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background-color 0.2s;
}

.zoom-btn:hover:not(:disabled) {
  background: rgba(255, 255, 255, 0.2);
}

.zoom-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.zoom-level {
  color: #fff;
  font-size: 0.75rem;
  min-width: 2.5rem;
  text-align: center;
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
  z-index: 2;
}

.preview-nav {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  border: none;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 999px;
  background: rgba(0, 0, 0, 0.45);
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  z-index: 2;
  transition: background 0.15s;
}
.preview-nav:hover {
  background: rgba(0, 0, 0, 0.7);
}
.preview-nav--prev { left: 0.75rem; }
.preview-nav--next { right: 0.75rem; }

.preview-counter {
  position: absolute;
  bottom: 0.75rem;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(0, 0, 0, 0.5);
  color: #fff;
  font-size: 0.8rem;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  pointer-events: none;
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

/* 评论区样式 */
.comments-section {
  margin-top: 1.25rem;
  padding-top: 1.25rem;
  border-top: 1px solid var(--border-soft);
}

.comments-title {
  margin: 0 0 0.85rem;
  font-size: 0.95rem;
  color: var(--text-primary);
}

.comment-form {
  margin-bottom: 1rem;
}

.comment-input {
  width: 100%;
  padding: 0.625rem 0.875rem;
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  color: var(--text-primary);
  background-color: #fff;
  resize: vertical;
  font-family: inherit;
  transition: border-color var(--dur-base), box-shadow var(--dur-base);
}

.comment-input:focus {
  outline: none;
  border-color: var(--pink-300);
  box-shadow: var(--shadow-focus);
  background-color: #fff9fc;
}

.comment-form-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.5rem;
}

.char-count {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.btn-sm {
  padding: 0.4rem 0.9rem;
  font-size: 0.8125rem;
}

.comments-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.comment-item {
  padding: 0.75rem;
  background: var(--bg-soft, #fafafa);
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-sm);
}

.comment-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.35rem;
}

.comment-author {
  font-size: 0.8125rem;
  font-weight: 600;
  color: var(--pink-500);
}

.comment-time {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.comment-content {
  margin: 0;
  font-size: 0.875rem;
  line-height: 1.6;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-break: break-word;
}

.comment-delete-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  margin-top: 0.35rem;
  padding: 0.15rem 0.4rem;
  font-size: 0.75rem;
  color: #af94a2;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 0.35rem;
  cursor: pointer;
  transition: color var(--dur-base), background-color var(--dur-base);
}

.comment-delete-btn:hover {
  color: #c45c7c;
  background: #fff2f6;
  border-color: #f2bfd1;
}

.comment-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.35rem;
}

.comment-reply-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.15rem 0.4rem;
  font-size: 0.75rem;
  color: #af94a2;
  background: transparent;
  border: 1px solid transparent;
  border-radius: 0.35rem;
  cursor: pointer;
  transition: color var(--dur-base), background-color var(--dur-base);
}

.comment-reply-btn:hover {
  color: var(--pink-500);
  background: #fff2f6;
  border-color: #f2bfd1;
}

.replies-list {
  margin-top: 0.65rem;
  margin-left: 1.25rem;
  padding-left: 0.85rem;
  border-left: 2px solid var(--border-soft);
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.reply-item {
  padding: 0.6rem 0.75rem;
  background: var(--bg-elevated);
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-sm);
}

.reply-form {
  margin-top: 0.5rem;
  padding: 0.65rem;
  background: var(--bg-elevated);
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-sm);
}

.reply-form-btns {
  display: flex;
  gap: 0.5rem;
}

.no-comments {
  margin: 0;
  font-size: 0.875rem;
  color: var(--text-secondary);
  text-align: center;
  padding: 1rem 0;
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
