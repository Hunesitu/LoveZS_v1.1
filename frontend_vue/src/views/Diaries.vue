<!--
Diaries 椤甸潰
瀵瑰簲鍘? frontend/src/pages/Diaries.tsx
鏃ヨ鍒楄〃锛屾敮鎸佹悳绱?绛涢€?鍒犻櫎
-->
<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useDiaries } from '@/composables/useDiaries'
import { useUiStore } from '@/stores/ui'
import { useUserStore } from '@/stores/user'
import { Plus, Search, Trash2, Edit } from 'lucide-vue-next'
import dayjs from 'dayjs'
import type { Diary } from '@/types'
import { resolveMediaUrl } from '@/utils/media'

const uiStore = useUiStore()
const userStore = useUserStore()
const { diaries, isLoading, loadDiaries, deleteDiary } = useDiaries()

const searchTerm = ref('')
const selectedCategory = ref('')
const selectedMood = ref('')
const categories = ref<string[]>([])

const moodOptions = [
  { value: 'happy', label: '开心 😊' },
  { value: 'sad', label: '伤心 😩' },
  { value: 'excited', label: '兴奋 🤩' },
  { value: 'calm', label: '平静 😌' },
  { value: 'angry', label: '生气 😧' },
  { value: 'tired', label: '疲惫 😾' },
  { value: 'loved', label: '相爱 😍' },
  { value: 'grateful', label: '感恩 🙏' },
]

const filteredDiaries = computed(() => {
  let filtered = diaries.value

  if (searchTerm.value) {
    const term = searchTerm.value.toLowerCase()
    filtered = filtered.filter((diary) =>
      diary.title.toLowerCase().includes(term) ||
      diary.content.toLowerCase().includes(term)
    )
  }

  if (selectedCategory.value) {
    filtered = filtered.filter((diary) => diary.category === selectedCategory.value)
  }

  if (selectedMood.value) {
    filtered = filtered.filter((diary) => diary.mood === selectedMood.value)
  }

  return filtered
})

const loadCategoriesAndTags = async () => {
  try {
    const categorySet = new Set<string>()

    diaries.value.forEach((diary) => {
      if (diary.category) categorySet.add(diary.category)
    })

    categories.value = Array.from(categorySet)
  } catch (error) {
    console.error('Failed to load categories:', error)
  }
}

const handleLoadDiaries = async () => {
  await loadDiaries()
  await loadCategoriesAndTags()
}

const handleDeleteDiary = async (id: number) => {
  if (!window.confirm('确定要删除这篇日记吗？此操作不可撤销。')) {
    return
  }

  try {
    await deleteDiary(id)
    uiStore.showToast('日记删除成功', 'success')
    await loadCategoriesAndTags()
  } catch (error) {
    console.error('Failed to delete diary:', error)
    uiStore.showToast('删除失败，请稍后重试', 'error')
  }
}

const stopCardNavigation = (event: Event) => {
  event.preventDefault()
  event.stopPropagation()
}

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

const stripMarkdown = (content: string, maxLength = 100) => {
  return content.replace(/[#*`_\[\]]/g, '').substring(0, maxLength)
}

onMounted(() => {
  handleLoadDiaries()
})
</script>

<template>
  <div class="diaries-page">
    <!-- 头部 -->
    <div class="page-header">
      <div class="header-info">
        <h1 class="page-title">我的日记</h1>
        <p class="page-subtitle">记录生活的点点滴滴</p>
      </div>
      <RouterLink to="/diaries/new" class="btn-primary">
        <Plus :size="16" />
        <span class="ml-2">写日记</span>
      </RouterLink>
    </div>

    <!-- 筛选栏 -->
    <div class="filter-card">
      <div class="filter-grid">
        <!-- 鎼滅储妗?-->
        <div class="search-input">
          <Search :size="20" class="search-icon" />
          <input
            v-model="searchTerm"
            type="text"
            placeholder="搜索日记..."
            class="input-field with-icon"
          />
        </div>

        <!-- 分类筛选 -->
        <select v-model="selectedCategory" class="input-field">
          <option value="">所有分类</option>
          <option v-for="category in categories" :key="category" :value="category">
            {{ category }}
          </option>
        </select>

        <!-- 心情筛选 -->
        <select v-model="selectedMood" class="input-field">
          <option value="">所有心情</option>
          <option v-for="mood in moodOptions" :key="mood.value" :value="mood.value">
            {{ mood.label }}
          </option>
        </select>

        <!-- 计数 -->
        <div class="filter-count">
          <span>共 {{ filteredDiaries.length }} 篇日记</span>
        </div>
      </div>
    </div>

    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading-container">
      <div class="spinner"></div>
    </div>

    <!-- 日记网格 -->
    <div v-else-if="filteredDiaries.length > 0" class="diaries-grid">
      <RouterLink
        v-for="diary in filteredDiaries"
        :key="diary.id"
        :to="`/diaries/${diary.id}`"
        class="diary-card"
      >
        <!-- 封面图 -->
        <div v-if="diary.attached_photos?.length" class="card-cover">
          <img
            :src="resolveMediaUrl(diary.attached_photos?.[0]?.url || diary.attached_photos?.[0]?.thumbnail_url || '')"
            :alt="diary.attached_photos?.[0]?.original_name"
            class="cover-image"
          />
        </div>

        <!-- 卡片头部 -->
        <div class="card-header">
          <div class="header-left">
            <span class="mood-emoji">{{ getMoodEmoji(diary.mood) }}</span>
            <div class="diary-meta">
              <h3 class="diary-title">
                <span v-if="diary.is_public === false" class="private-badge">🔒</span>
                {{ diary.title }}
              </h3>
              <p class="diary-date">
                {{ dayjs(diary.created_at).format('YYYY-MM-DD HH:mm:ss') }}
                <span v-if="diary.created_by_details" class="diary-author">· {{ diary.created_by_details.username }}</span>
              </p>
            </div>
          </div>
          <div class="header-actions" v-if="diary.created_by === userStore.user?.id">
            <RouterLink
              :to="`/diaries/${diary.id}/edit`"
              class="action-btn edit-btn"
              title="编辑"
              @click="stopCardNavigation"
            >
              <Edit :size="16" />
            </RouterLink>
            <button
              @click="(event) => { stopCardNavigation(event); handleDeleteDiary(diary.id) }"
              class="action-btn delete-btn"
              title="删除"
            >
              <Trash2 :size="16" />
            </button>
          </div>
        </div>

        <!-- 鍐呭棰勮 -->
        <div class="card-content">
          <p class="content-preview">{{ stripMarkdown(diary.content) }}</p>
        </div>

        <!-- 分类 -->
        <div class="card-footer">
          <div class="tags-group">
            <span class="category-badge">{{ diary.category }}</span>
          </div>
        </div>
      </RouterLink>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state-card">
      <div class="empty-state">
        <div class="empty-icon">馃摑</div>
        <h3 class="empty-title">
          {{ searchTerm || selectedCategory || selectedMood ? '没有找到匹配的日记' : '还没有日记' }}
        </h3>
        <p class="empty-text">
          {{ searchTerm || selectedCategory || selectedMood
            ? '尝试调整搜索条件或清空筛选'
            : '开始写下你们的第一篇日记'
          }}
        </p>
        <RouterLink to="/diaries/new" class="btn-primary">
          <Plus :size="16" />
          <span class="ml-2">写第一篇日记</span>
        </RouterLink>
      </div>
    </div>
  </div>
</template>

<style scoped>
.diaries-page {
  width: 100%;
}

.page-header {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.header-info {
  flex: 1;
}

.page-title {
  margin: 0;
  font-size: 1.7rem;
  font-weight: 700;
  color: var(--text-primary);
}

.page-subtitle {
  margin: 0.35rem 0 0;
  color: var(--text-secondary);
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.62rem 1.2rem;
  border: none;
  border-radius: var(--radius-sm);
  background: linear-gradient(135deg, var(--pink-500) 0%, var(--rose-500) 100%);
  color: #fff;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  box-shadow: 0 8px 16px rgba(217, 117, 154, 0.26);
  transition: transform var(--dur-fast), box-shadow var(--dur-base), filter var(--dur-base);
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 12px 22px rgba(217, 117, 154, 0.32);
  filter: brightness(1.02);
}

.filter-card {
  background: var(--bg-elevated);
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-lg);
  padding: 1rem;
  box-shadow: var(--shadow-soft);
  margin-bottom: 1.25rem;
}

.filter-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.75rem;
}

.search-input {
  position: relative;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #a8929d;
  pointer-events: none;
}

.input-field {
  width: 100%;
  padding: 0.625rem 0.875rem;
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  color: var(--text-primary);
  background-color: #fff;
  transition: border-color var(--dur-base), box-shadow var(--dur-base), background-color var(--dur-base);
}

.input-field:focus {
  outline: none;
  border-color: var(--pink-300);
  box-shadow: var(--shadow-focus);
  background-color: #fff9fc;
}

.input-field.with-icon {
  padding-left: 2.45rem;
}

.filter-count {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.loading-container {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 3.5rem 0;
}

.spinner {
  width: 2rem;
  height: 2rem;
  border: 2px solid #f4dbe7;
  border-top-color: var(--pink-500);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.diaries-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1rem;
}

.diary-card {
  display: block;
  text-decoration: none;
  background: var(--bg-elevated);
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-lg);
  padding: 0;
  overflow: hidden;
  box-shadow: var(--shadow-soft);
  transition: transform var(--dur-fast), border-color var(--dur-base), box-shadow var(--dur-base);
}

.diary-card:hover {
  transform: translateY(-2px);
  border-color: var(--border-strong);
  box-shadow: var(--shadow-hover);
}

.card-cover {
  width: 100%;
  aspect-ratio: 16 / 9;
  overflow: hidden;
}

.cover-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.card-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  margin-bottom: 0.75rem;
  padding: 1rem 1rem 0;
}

.header-left {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  flex: 1;
  min-width: 0;
}

.mood-emoji {
  font-size: 1.45rem;
  flex-shrink: 0;
}

.diary-meta {
  min-width: 0;
}

.diary-title {
  margin: 0;
  font-weight: 600;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.private-badge {
  font-size: 0.85em;
  flex-shrink: 0;
}

.diary-date {
  margin: 0.15rem 0 0;
  font-size: 0.8125rem;
  color: var(--text-secondary);
}

.diary-author {
  color: var(--pink-500);
  font-weight: 500;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  flex-shrink: 0;
}

.action-btn {
  padding: 0.3rem;
  color: #a8929d;
  transition: color var(--dur-base), background-color var(--dur-base), transform var(--dur-fast);
  background: transparent;
  border: 1px solid transparent;
  border-radius: 0.5rem;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
}

.action-btn:hover {
  transform: translateY(-1px);
}

.edit-btn:hover {
  color: var(--pink-500);
  background: var(--pink-50);
  border-color: var(--border-soft);
}

.delete-btn:hover {
  color: #cf617f;
  background: #fff1f5;
  border-color: #f2bfd1;
}

.card-content {
  margin-bottom: 0.75rem;
  padding: 0 1rem;
}

.content-preview {
  margin: 0;
  font-size: 0.875rem;
  color: #574752;
  line-height: 1.55;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1rem 1rem;
}

.tags-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.category-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.5rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  background: #ffeaf3;
  color: #a55674;
}

.empty-state-card {
  background: var(--bg-elevated);
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-soft);
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
}

.empty-icon {
  font-size: 3.6rem;
  margin-bottom: 0.9rem;
}

.empty-title {
  margin: 0;
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--text-primary);
}

.empty-text {
  margin: 0.4rem 0 1.25rem;
  color: var(--text-secondary);
}

.ml-2 {
  margin-left: 0.5rem;
}

@media (min-width: 640px) {
  .page-header {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
}

@media (min-width: 768px) {
  .filter-grid {
    grid-template-columns: repeat(4, 1fr);
  }

  .diaries-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .page-title {
    font-size: 1.45rem;
  }

  .filter-grid {
    grid-template-columns: 1fr;
  }
}
</style>








