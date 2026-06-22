<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { Edit, Heart, Pin, Plus, Search, Trash2 } from 'lucide-vue-next'
import dayjs from 'dayjs'
import { useDiaries } from '@/composables/useDiaries'
import { useUiStore } from '@/stores/ui'
import { useUserStore } from '@/stores/user'
import { pinDiary, unpinDiary } from '@/api/diary'
import { getMediaUrl, isVideo } from '@/utils/media'
import { MOOD_EMOJIS, MOOD_LABELS, type Diary, type Mood, type Photo } from '@/types'

const uiStore = useUiStore()
const userStore = useUserStore()
const { diaries, isLoading, loadDiaries, deleteDiary } = useDiaries()

const searchTerm = ref('')
const selectedCategory = ref('')
const selectedMood = ref('')
const categories = ref<string[]>([])

const moodOptions = Object.entries(MOOD_LABELS).map(([value, label]) => ({
  value: value as Mood,
  label,
  emoji: MOOD_EMOJIS[value as Mood],
}))

const getFirstMedia = (diary: Diary) =>
  diary.cover_media || diary.attached_photos?.find(p => !isVideo(p)) || diary.attached_photos?.[0] || null

const filteredDiaries = computed(() => {
  return diaries.value.filter(diary => {
    const keyword = searchTerm.value.trim().toLowerCase()
    const matchesKeyword =
      !keyword ||
      diary.title.toLowerCase().includes(keyword) ||
      diary.content.toLowerCase().includes(keyword)
    const matchesCategory = !selectedCategory.value || diary.category === selectedCategory.value
    const matchesMood = !selectedMood.value || diary.mood === selectedMood.value
    return matchesKeyword && matchesCategory && matchesMood
  })
})

const loadCategories = () => {
  categories.value = Array.from(new Set(diaries.value.map(d => d.category).filter(Boolean)))
}

const refreshData = async () => {
  await loadDiaries()
  loadCategories()
}

const handleDeleteDiary = async (id: number) => {
  if (!window.confirm('确定要删除这篇日记吗？此操作不可撤销。')) return

  try {
    await deleteDiary(id)
    uiStore.showToast('日记删除成功', 'success')
    loadCategories()
  } catch (error) {
    console.error('Failed to delete diary:', error)
    uiStore.showToast('删除失败，请稍后重试', 'error')
  }
}

const handleTogglePin = async (diary: Diary, event: Event) => {
  event.preventDefault()
  event.stopPropagation()

  try {
    if (diary.is_pinned) {
      await unpinDiary(diary.id)
      diary.is_pinned = false
      uiStore.showToast('已取消置顶', 'success')
    } else {
      await pinDiary(diary.id)
      diary.is_pinned = true
      uiStore.showToast('日记已置顶', 'success')
    }
  } catch (error) {
    console.error('Failed to toggle pin:', error)
    uiStore.showToast('操作失败，请稍后重试', 'error')
  }
}

const stopCardNavigation = (event: Event) => {
  event.preventDefault()
  event.stopPropagation()
}

const stripMarkdown = (content: string, maxLength = 110) =>
  content.replace(/[#*`_[\]]/g, '').substring(0, maxLength)

onMounted(refreshData)
</script>

<template>
  <div class="diaries-page page-shell">
    <div class="page-header">
      <div>
        <p class="romance-kicker">Memory Library</p>
        <h1 class="page-title">我的日记</h1>
        <p class="page-subtitle">把每一次心动、旅行和日常，都剪进只属于我们的长片。</p>
      </div>
      <RouterLink to="/diaries/new" class="btn-primary">
        <Plus :size="16" />
        写日记
      </RouterLink>
    </div>

    <section class="filter-card cinematic-card">
      <div class="filter-grid">
        <label class="search-input">
          <Search :size="18" class="search-icon" />
        <input v-model="searchTerm" type="text" placeholder="搜索某一幕回忆..." class="input-field with-icon" />
        </label>
        <select v-model="selectedCategory" class="input-field" aria-label="分类筛选">
          <option value="">所有分类</option>
          <option v-for="category in categories" :key="category" :value="category">{{ category }}</option>
        </select>
        <select v-model="selectedMood" class="input-field" aria-label="心情筛选">
          <option value="">所有心情</option>
          <option v-for="mood in moodOptions" :key="mood.value" :value="mood.value">
            {{ mood.emoji }} {{ mood.label }}
          </option>
        </select>
        <div class="filter-count">共 {{ filteredDiaries.length }} 篇日记</div>
      </div>
    </section>

    <div v-if="isLoading" class="loading-container glass-card">
      <div class="spinner"></div>
    </div>

    <div v-else-if="filteredDiaries.length > 0" class="diaries-grid">
      <RouterLink
        v-for="diary in filteredDiaries"
        :key="diary.id"
        :to="`/diaries/${diary.id}`"
        class="diary-card cinematic-card"
      >
        <div class="card-cover">
          <template v-if="getFirstMedia(diary)">
            <video
              v-if="isVideo(getFirstMedia(diary)!)"
              :src="getMediaUrl(getFirstMedia(diary), 'thumbnail')"
              class="cover-image"
              muted
              preload="metadata"
            />
            <img
              v-else
              :src="getMediaUrl(getFirstMedia(diary), 'thumbnail')"
              :alt="getFirstMedia(diary)!.original_name"
              class="cover-image"
              loading="lazy"
              decoding="async"
            />
          </template>
          <div v-else class="cover-fallback">
            <Heart :size="30" fill="currentColor" />
          </div>
        </div>

        <div class="card-content">
          <div class="card-header">
            <div class="header-left">
              <span class="mood-emoji">{{ MOOD_EMOJIS[diary.mood] }}</span>
              <div class="diary-meta">
                <h3 class="diary-title">
                  <span v-if="diary.is_public === false" class="inline-badge">私密</span>
                  <span v-if="diary.is_pinned" class="inline-badge">置顶</span>
                  {{ diary.title }}
                </h3>
                <p class="diary-date">
                  {{ dayjs(diary.created_at).format('YYYY-MM-DD HH:mm') }}
                  <span v-if="diary.created_by_details">· {{ diary.created_by_details.username }}</span>
                </p>
              </div>
            </div>
            <div v-if="diary.created_by === userStore.user?.id || userStore.isAdmin" class="header-actions">
              <button
                type="button"
                class="action-btn"
                :title="diary.is_pinned ? '取消置顶' : '置顶'"
                @click="event => handleTogglePin(diary, event)"
              >
                <Pin :size="16" :class="{ pinned: diary.is_pinned }" />
              </button>
              <RouterLink
                :to="`/diaries/${diary.id}/edit`"
                class="action-btn"
                title="编辑"
                @click="stopCardNavigation"
              >
                <Edit :size="16" />
              </RouterLink>
              <button
                type="button"
                class="action-btn danger"
                title="删除"
                @click="event => { stopCardNavigation(event); handleDeleteDiary(diary.id) }"
              >
                <Trash2 :size="16" />
              </button>
            </div>
          </div>

          <p class="content-preview">{{ stripMarkdown(diary.content) || '这一幕还没写完，但光已经很好。' }}</p>

          <div class="card-footer">
            <span class="tag">{{ diary.category || '生活' }}</span>
            <span>{{ MOOD_LABELS[diary.mood] }}</span>
          </div>
        </div>
      </RouterLink>
    </div>

    <div v-else class="empty-state-card">
      <div class="empty-state">
        <Heart :size="44" fill="currentColor" />
        <h3>{{ searchTerm || selectedCategory || selectedMood ? '没有找到匹配的日记' : '还没有日记' }}</h3>
        <p>{{ searchTerm || selectedCategory || selectedMood ? '换个关键词，也许那一幕藏在别的光里。' : '开始写下你们的第一篇日记，让银幕亮起来。' }}</p>
        <RouterLink to="/diaries/new" class="btn-primary">
          <Plus :size="16" />
          写第一篇日记
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
.filter-card {
  padding: 1rem;
  margin-bottom: 1.25rem;
}

.search-input {
  position: relative;
}

.search-icon {
  position: absolute;
  top: 50%;
  left: 0.8rem;
  color: var(--ink-muted);
  transform: translateY(-50%);
  pointer-events: none;
}

.input-field.with-icon {
  padding-left: 2.5rem;
}

.filter-count {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  color: var(--ink-soft);
  font-size: 0.875rem;
  white-space: nowrap;
}

.diaries-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
}

.diary-card {
  overflow: hidden;
  transition: transform var(--dur-base) ease, border-color var(--dur-base) ease, box-shadow var(--dur-base) ease;
  animation: revealIn 420ms ease both;
}

.diary-card:hover {
  transform: translateY(-5px);
}

.diary-card:focus-visible {
  outline: 2px solid var(--rose-bright);
  outline-offset: 2px;
}

.card-cover {
  position: relative;
  width: 100%;
  aspect-ratio: 16 / 9;
  overflow: hidden;
  background: rgba(32, 27, 50, 0.9);
}

.cover-image,
.cover-fallback {
  width: 100%;
  height: 100%;
}

.cover-image {
  object-fit: cover;
  transition: transform var(--dur-slow) ease;
}

.diary-card:hover .cover-image {
  transform: scale(1.04);
}

.cover-fallback {
  display: grid;
  place-items: center;
  color: rgba(255, 143, 200, 0.7);
  background:
    radial-gradient(circle at center, rgba(245, 200, 143, 0.18), transparent 48%),
    radial-gradient(circle at 72% 20%, rgba(240, 120, 182, 0.22), transparent 36%),
    linear-gradient(135deg, rgba(46, 28, 55, 0.95), rgba(8, 8, 14, 0.98));
}

.card-content {
  padding: 1rem;
}

.card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
}

.header-left {
  display: flex;
  min-width: 0;
  gap: 0.6rem;
}

.mood-emoji {
  font-size: 1.35rem;
  line-height: 1.2;
}

.diary-meta {
  min-width: 0;
}

.diary-title {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  margin: 0;
  overflow: hidden;
  color: var(--ink);
  font-size: 1rem;
  font-weight: 800;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.inline-badge {
  flex: 0 0 auto;
  padding: 0.1rem 0.35rem;
  border-radius: 999px;
  color: var(--rose-bright);
  background: rgba(240, 120, 182, 0.14);
  font-size: 0.68rem;
}

.diary-date,
.content-preview,
.card-footer {
  color: var(--ink-soft);
}

.diary-date {
  margin: 0.2rem 0 0;
  font-size: 0.78rem;
}

.header-actions {
  display: flex;
  flex-shrink: 0;
  gap: 0.3rem;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: 1px solid transparent;
  color: var(--ink-muted);
  background: transparent;
}

.action-btn:hover {
  color: var(--rose-bright);
  border-color: var(--line);
  background: rgba(255, 255, 255, 0.06);
}

.action-btn.danger:hover {
  color: var(--danger);
}

.pinned {
  color: var(--rose-bright);
  transform: rotate(45deg);
}

.content-preview {
  display: -webkit-box;
  min-height: 2.8em;
  margin: 0.85rem 0;
  overflow: hidden;
  font-size: 0.875rem;
  line-height: 1.6;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  font-size: 0.78rem;
  font-weight: 700;
}

.empty-state-card {
  padding: 1rem;
}

.empty-state {
  gap: 0.75rem;
}

.empty-state h3,
.empty-state p {
  margin: 0;
}

.empty-state svg {
  color: var(--rose-bright);
}

@media (max-width: 767px) {
  .diaries-grid {
    grid-template-columns: 1fr;
  }

  .filter-count {
    justify-content: flex-start;
  }

  .card-header {
    flex-direction: column;
  }

  .header-actions {
    width: 100%;
    justify-content: flex-end;
  }
}
</style>
