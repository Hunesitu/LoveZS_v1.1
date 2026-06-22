<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  ArrowLeft,
  ChevronLeft,
  ChevronRight,
  Edit2,
  Pin,
  Reply,
  RotateCcw,
  Send,
  Trash2,
  X,
  ZoomIn,
  ZoomOut,
} from 'lucide-vue-next'
import dayjs from 'dayjs'
import { useUiStore } from '@/stores/ui'
import { useUserStore } from '@/stores/user'
import { getMediaUrl, isVideo } from '@/utils/media'
import diaryService, { pinDiary, unpinDiary } from '@/api/diary'
import { api } from '@/api/client'
import { MOOD_EMOJIS, type Diary, type DiaryComment, type Photo } from '@/types'

const route = useRoute()
const router = useRouter()
const uiStore = useUiStore()
const userStore = useUserStore()

const diary = ref<Diary | null>(null)
const isLoading = ref(false)
const previewIndex = ref(-1)
const scale = ref(1)
const minScale = 0.5
const maxScale = 3
const commentContent = ref('')
const isSubmittingComment = ref(false)
const comments = ref<DiaryComment[]>([])
const replyingTo = ref<DiaryComment | null>(null)
const replyContent = ref('')
const isSubmittingReply = ref(false)

const diaryId = computed(() => Number(route.params.id))
const photoCount = computed(() => diary.value?.attached_photos?.length ?? 0)
const previewPhoto = computed(() =>
  previewIndex.value >= 0 ? diary.value?.attached_photos?.[previewIndex.value] ?? null : null
)
const totalCommentCount = computed(() =>
  comments.value.reduce((sum, comment) => sum + 1 + (comment.replies?.length ?? 0), 0)
)

const resetZoom = () => {
  scale.value = 1
}

const zoomIn = () => {
  scale.value = Math.min(scale.value + 0.25, maxScale)
}

const zoomOut = () => {
  scale.value = Math.max(scale.value - 0.25, minScale)
}

const loadDiary = async () => {
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
  const index = diary.value?.attached_photos?.findIndex(p => p.id === photo.id) ?? -1
  previewIndex.value = index
  resetZoom()
}

const closePreview = () => {
  previewIndex.value = -1
  resetZoom()
}

const prevPhoto = () => {
  if (previewIndex.value > 0) {
    previewIndex.value--
    resetZoom()
  }
}

const nextPhoto = () => {
  if (previewIndex.value < photoCount.value - 1) {
    previewIndex.value++
    resetZoom()
  }
}

const submitComment = async () => {
  if (!commentContent.value.trim()) return

  isSubmittingComment.value = true
  try {
    const response = await api.post(`/diaries/${diaryId.value}/comments/`, {
      content: commentContent.value.trim(),
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
  if (!window.confirm('确定要删除这条评论吗？')) return

  try {
    await api.delete(`/diaries/${diaryId.value}/comments/${commentId}/`)
    if (parentId) {
      const parent = comments.value.find(c => c.id === parentId)
      if (parent?.replies) parent.replies = parent.replies.filter(r => r.id !== commentId)
    } else {
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
      parent: replyingTo.value.id,
    })
    const newReply = response.data.comment
    const parent = comments.value.find(c => c.id === newReply.parent)
    if (parent) {
      if (!parent.replies) parent.replies = []
      parent.replies.push(newReply)
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

const onKeydown = (event: KeyboardEvent) => {
  if (!previewPhoto.value) return
  if (event.key === 'ArrowLeft') prevPhoto()
  if (event.key === 'ArrowRight') nextPhoto()
  if (event.key === 'Escape') closePreview()
}

onMounted(() => {
  loadDiary()
  window.addEventListener('keydown', onKeydown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', onKeydown)
})
</script>

<template>
  <div class="diary-detail-page page-narrow">
    <div class="detail-header">
      <button class="btn-secondary" type="button" @click="router.push('/diaries')">
        <ArrowLeft :size="16" />
        返回列表
      </button>
      <div class="header-actions">
        <button
          v-if="diary && (diary.created_by === userStore.user?.id || userStore.isAdmin)"
          class="btn-secondary"
          type="button"
          @click="handleTogglePin"
        >
          <Pin :size="16" :class="{ pinned: diary.is_pinned }" />
          {{ diary.is_pinned ? '取消置顶' : '置顶' }}
        </button>
        <button
          v-if="diary && diary.created_by === userStore.user?.id"
          class="btn-primary"
          type="button"
          @click="router.push(`/diaries/${diary.id}/edit`)"
        >
          <Edit2 :size="16" />
          编辑
        </button>
      </div>
    </div>

    <div v-if="isLoading" class="loading-container glass-card">
      <div class="spinner"></div>
    </div>

    <article v-else-if="diary" class="detail-card cinematic-frame">
      <header class="card-header">
        <p class="romance-kicker">Scene Detail</p>
        <div class="title-wrap">
          <span class="mood-emoji">{{ MOOD_EMOJIS[diary.mood] }}</span>
          <h1 class="title">
            <span v-if="diary.is_public === false" class="inline-badge">私密</span>
            <span v-if="diary.is_pinned" class="inline-badge">置顶</span>
            {{ diary.title }}
          </h1>
        </div>
        <div class="meta-line">
          <span>{{ dayjs(diary.created_at).format('YYYY-MM-DD HH:mm') }}</span>
          <span>·</span>
          <span>{{ diary.category }}</span>
          <span v-if="diary.created_by_details">· {{ diary.created_by_details.username }}</span>
          <span v-if="diary.word_count">· {{ diary.word_count }} 字</span>
        </div>
        <p class="cinematic-quote">“有些时刻不必盛大，只要被认真记得，就会一直发光。”</p>
      </header>

      <section class="content-section">
        <pre class="content-text">{{ diary.content }}</pre>
      </section>

      <section v-if="diary.attached_photos?.length" class="photos-section">
        <h2 class="section-title">关联胶片（{{ diary.attached_photos.length }}）</h2>
        <div class="photos-grid">
          <button
            v-for="photo in diary.attached_photos"
            :key="photo.id"
            type="button"
            class="photo-item"
            @click="openPreview(photo)"
          >
            <video
              v-if="isVideo(photo)"
              :src="getMediaUrl(photo, 'thumbnail')"
              class="photo-image"
              muted
              preload="metadata"
            />
            <img
              v-else
              :src="getMediaUrl(photo, 'thumbnail')"
              :alt="photo.original_name"
              class="photo-image"
              loading="lazy"
              decoding="async"
            />
            <span v-if="isVideo(photo)" class="video-badge">▶</span>
          </button>
        </div>
      </section>

      <section class="comments-section">
        <h2 class="section-title">片尾留言（{{ totalCommentCount }}）</h2>

        <div v-if="userStore.isAuthenticated" class="comment-form">
          <textarea
            v-model="commentContent"
            class="comment-input"
            placeholder="写下一句片尾留言..."
            rows="3"
            maxlength="1000"
          />
          <div class="comment-form-actions">
            <span class="char-count">{{ commentContent.length }}/1000</span>
            <button class="btn-primary btn-sm" type="button" :disabled="!commentContent.trim() || isSubmittingComment" @click="submitComment">
              <Send :size="14" />
              {{ isSubmittingComment ? '发送中...' : '发表' }}
            </button>
          </div>
        </div>

        <div v-if="comments.length > 0" class="comments-list">
          <article v-for="comment in comments" :key="comment.id" class="comment-item">
            <div class="comment-header">
              <strong>{{ comment.created_by_details?.username || '匿名' }}</strong>
              <span>{{ dayjs(comment.created_at).format('YYYY-MM-DD HH:mm') }}</span>
            </div>
            <p class="comment-content">{{ comment.content }}</p>
            <div class="comment-actions">
              <button v-if="userStore.isAuthenticated" type="button" class="comment-reply-btn" @click="startReply(comment)">
                <Reply :size="13" />
                回复
              </button>
              <button v-if="comment.created_by === userStore.user?.id" type="button" class="comment-delete-btn" @click="deleteComment(comment.id)">
                <Trash2 :size="13" />
                删除
              </button>
            </div>

            <div v-if="replyingTo?.id === comment.id" class="reply-form">
              <textarea
                v-model="replyContent"
                class="comment-input"
                :placeholder="`回复 ${comment.created_by_details?.username || '匿名'}...`"
                rows="2"
                maxlength="1000"
              />
              <div class="comment-form-actions">
                <span class="char-count">{{ replyContent.length }}/1000</span>
                <div class="reply-form-btns">
                  <button class="btn-secondary btn-sm" type="button" @click="cancelReply">取消</button>
                  <button class="btn-primary btn-sm" type="button" :disabled="!replyContent.trim() || isSubmittingReply" @click="submitReply">
                    <Send :size="14" />
                    {{ isSubmittingReply ? '发送中...' : '回复' }}
                  </button>
                </div>
              </div>
            </div>

            <div v-if="comment.replies?.length" class="replies-list">
              <article v-for="reply in comment.replies" :key="reply.id" class="reply-item">
                <div class="comment-header">
                  <strong>{{ reply.created_by_details?.username || '匿名' }}</strong>
                  <span>{{ dayjs(reply.created_at).format('YYYY-MM-DD HH:mm') }}</span>
                </div>
                <p class="comment-content">{{ reply.content }}</p>
                <div class="comment-actions">
                  <button v-if="userStore.isAuthenticated" type="button" class="comment-reply-btn" @click="startReply(comment)">
                    <Reply :size="13" />
                    回复
                  </button>
                  <button v-if="reply.created_by === userStore.user?.id" type="button" class="comment-delete-btn" @click="deleteComment(reply.id, comment.id)">
                    <Trash2 :size="13" />
                    删除
                  </button>
                </div>
              </article>
            </div>
          </article>
        </div>
        <p v-else class="no-comments">暂无留言，第一句可以很轻，也可以很甜。</p>
      </section>
    </article>

    <div v-else class="empty-state-card">
      <div class="empty-state">未找到该日记</div>
    </div>

    <div v-if="previewPhoto" class="preview-overlay" role="dialog" aria-modal="true" @click="closePreview">
      <div class="preview-content" @click.stop>
        <button class="preview-close" type="button" aria-label="关闭预览" @click="closePreview">
          <X :size="18" />
        </button>

        <div class="zoom-controls">
          <button class="zoom-btn" type="button" :disabled="scale <= minScale" aria-label="缩小" @click="zoomOut">
            <ZoomOut :size="18" />
          </button>
          <span class="zoom-level">{{ Math.round(scale * 100) }}%</span>
          <button class="zoom-btn" type="button" :disabled="scale >= maxScale" aria-label="放大" @click="zoomIn">
            <ZoomIn :size="18" />
          </button>
          <button class="zoom-btn" type="button" aria-label="重置" @click="resetZoom">
            <RotateCcw :size="18" />
          </button>
        </div>

        <button v-if="previewIndex > 0" class="preview-nav preview-nav--prev" type="button" aria-label="上一张" @click.stop="prevPhoto">
          <ChevronLeft :size="28" />
        </button>

        <div class="preview-image-wrapper" :style="{ transform: `scale(${scale})` }">
          <video v-if="isVideo(previewPhoto)" :src="getMediaUrl(previewPhoto, 'original')" class="preview-image" controls autoplay />
          <img v-else :src="getMediaUrl(previewPhoto, 'original')" :alt="previewPhoto.original_name" class="preview-image" />
        </div>

        <button v-if="previewIndex < photoCount - 1" class="preview-nav preview-nav--next" type="button" aria-label="下一张" @click.stop="nextPhoto">
          <ChevronRight :size="28" />
        </button>

        <span v-if="photoCount > 1" class="preview-counter">{{ previewIndex + 1 }} / {{ photoCount }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.detail-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.detail-card {
  padding: 1.25rem;
}

.card-header {
  margin-bottom: 1rem;
  position: relative;
}

.title-wrap {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}

.mood-emoji {
  font-size: 1.4rem;
}

.title {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  margin: 0;
  color: var(--ink);
  font-family: var(--font-serif);
  font-size: clamp(1.5rem, 3vw, 2rem);
}

.inline-badge {
  padding: 0.12rem 0.4rem;
  border-radius: 999px;
  color: var(--rose-bright);
  background: rgba(240, 120, 182, 0.14);
  font-family: var(--font-sans);
  font-size: 0.72rem;
}

.meta-line {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  margin-top: 0.45rem;
  color: var(--ink-soft);
  font-size: 0.875rem;
}

.cinematic-quote {
  max-width: 720px;
  margin: 0.95rem 0 0;
}

.pinned {
  color: var(--rose-bright);
  transform: rotate(45deg);
}

.content-section {
  margin: 1.25rem 0;
}

.content-text {
  margin: 0;
  color: var(--ink);
  font: inherit;
  font-size: 0.98rem;
  line-height: 1.85;
  white-space: pre-wrap;
  word-break: break-word;
}

.photos-section,
.comments-section {
  padding-top: 1.25rem;
  margin-top: 1.25rem;
  border-top: 1px solid var(--line);
}

.photos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(220px, 100%), 1fr));
  gap: 0.75rem;
  margin-top: 0.8rem;
}

.photo-item {
  position: relative;
  overflow: hidden;
  padding: 0;
  border: 1px solid rgba(245, 200, 143, 0.14);
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.06);
  transition: transform var(--dur-slow) ease, border-color var(--dur-slow) ease;
}

.photo-item:hover {
  border-color: var(--line-strong);
  transform: translateY(-3px);
}

.photo-image {
  width: 100%;
  aspect-ratio: 4 / 3;
  object-fit: cover;
}

.video-badge {
  position: absolute;
  top: 50%;
  left: 50%;
  display: grid;
  place-items: center;
  width: 2.2rem;
  height: 2.2rem;
  border-radius: 50%;
  color: #fff;
  background: rgba(0, 0, 0, 0.55);
  transform: translate(-50%, -50%);
}

.comment-form {
  margin: 0.85rem 0 1rem;
}

.comment-form-actions {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  margin-top: 0.55rem;
}

.char-count,
.no-comments {
  color: var(--ink-soft);
  font-size: 0.8rem;
}

.btn-sm {
  min-height: 34px;
  padding: 0.4rem 0.85rem;
  font-size: 0.8rem;
}

.comments-list {
  display: grid;
  gap: 0.75rem;
}

.comment-item,
.reply-item,
.reply-form {
  padding: 0.75rem;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.05);
}

.comment-header {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.35rem;
  color: var(--ink-soft);
  font-size: 0.8rem;
}

.comment-header strong {
  color: var(--rose-bright);
}

.comment-content {
  margin: 0;
  color: var(--ink);
  line-height: 1.65;
  white-space: pre-wrap;
}

.comment-actions,
.reply-form-btns {
  display: flex;
  gap: 0.5rem;
  margin-top: 0.45rem;
}

.comment-reply-btn,
.comment-delete-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.18rem 0.4rem;
  border: 1px solid transparent;
  color: var(--ink-muted);
  background: transparent;
  font-size: 0.75rem;
}

.comment-reply-btn:hover {
  color: var(--rose-bright);
}

.comment-delete-btn:hover {
  color: var(--danger);
}

.replies-list {
  display: grid;
  gap: 0.5rem;
  margin-top: 0.65rem;
  margin-left: 1.25rem;
  padding-left: 0.85rem;
  border-left: 2px solid var(--line);
}

.preview-overlay {
  position: fixed;
  inset: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: clamp(0.5rem, 2vw, 1.25rem);
  background: rgba(0, 0, 0, 0.78);
  backdrop-filter: blur(6px);
}

.preview-content {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: center;
  width: min(96vw, 1400px);
  max-height: calc(100vh - 1rem);
}

.preview-image-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  max-width: 100%;
  max-height: calc(100vh - 1rem);
  transition: transform var(--dur-slow) ease;
}

.preview-image {
  max-width: 100%;
  max-height: calc(100vh - 1rem);
  border-radius: var(--radius-md);
  object-fit: contain;
}

.preview-close,
.zoom-btn,
.preview-nav {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid var(--line);
  color: #fff;
  background: rgba(0, 0, 0, 0.5);
}

.preview-close {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  z-index: 3;
  width: 2rem;
  height: 2rem;
  border-radius: 999px;
}

.zoom-controls {
  position: absolute;
  top: 0.5rem;
  left: 50%;
  z-index: 3;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  border-radius: var(--radius-md);
  background: rgba(0, 0, 0, 0.58);
  transform: translateX(-50%);
}

.zoom-btn {
  width: 1.75rem;
  height: 1.75rem;
  border-radius: var(--radius-sm);
}

.zoom-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.zoom-level {
  min-width: 2.5rem;
  color: #fff;
  font-size: 0.75rem;
  text-align: center;
}

.preview-nav {
  position: absolute;
  top: 50%;
  z-index: 2;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 999px;
  transform: translateY(-50%);
}

.preview-nav--prev {
  left: 0.75rem;
}

.preview-nav--next {
  right: 0.75rem;
}

.preview-counter {
  position: absolute;
  bottom: 0.75rem;
  left: 50%;
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  color: #fff;
  background: rgba(0, 0, 0, 0.55);
  font-size: 0.8rem;
  transform: translateX(-50%);
}

@media (max-width: 640px) {
  .detail-header,
  .header-actions,
  .comment-form-actions {
    flex-direction: column;
    align-items: stretch;
  }

  .title-wrap {
    align-items: flex-start;
  }

  .photos-grid {
    grid-template-columns: repeat(auto-fit, minmax(min(150px, 100%), 1fr));
  }
}
</style>
