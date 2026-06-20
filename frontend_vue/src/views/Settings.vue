<script setup lang="ts">
import { ref } from 'vue'
import { Download, Settings as SettingsIcon, Trash2 } from 'lucide-vue-next'
import api from '@/api/client'
import { useUiStore } from '@/stores/ui'
import { useUserStore } from '@/stores/user'

const uiStore = useUiStore()
const userStore = useUserStore()

const isExporting = ref(false)
const isClearing = ref(false)

const handleExportBackup = async () => {
  isExporting.value = true
  try {
    const response = await api.get('/backup/export/', { responseType: 'blob' })
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `lovezs-media-backup-${new Date().toISOString().split('T')[0]}.zip`)
    document.body.appendChild(link)
    link.click()
    link.remove()
    window.URL.revokeObjectURL(url)
    uiStore.showToast('备份导出成功', 'success')
  } catch (error) {
    console.error('Export backup error:', error)
    uiStore.showToast('备份导出失败', 'error')
  } finally {
    isExporting.value = false
  }
}

const handleClearAllData = async () => {
  if (!window.confirm('危险操作！确定要清除所有数据吗？此操作不可恢复。')) return
  const confirmation = window.prompt('请输入 "DELETE ALL" 以确认：')
  if (confirmation !== 'DELETE ALL') {
    window.alert('操作已取消')
    return
  }
  if (!window.confirm('最后确认：所有数据将被永久删除。')) return

  isClearing.value = true
  try {
    await api.post('/admin/clear/')
    uiStore.showToast('数据清除成功', 'success')
  } catch (error) {
    console.error('Clear data error:', error)
    uiStore.showToast('数据清除失败', 'error')
  } finally {
    isClearing.value = false
  }
}
</script>

<template>
  <div class="settings-page page-narrow">
    <div class="page-header">
      <div>
        <p class="romance-kicker">Projection Room</p>
        <h1 class="page-title">
          <SettingsIcon :size="24" class="title-icon" />
          设置
        </h1>
        <p class="page-subtitle">整理放映室、备份胶片，也给回忆留一份安心。</p>
      </div>
    </div>

    <section class="card cinematic-card">
      <h2 class="section-title">数据备份</h2>
      <p class="section-description">导出媒体文件备份（照片、视频等）到本地 zip 文件，把重要画面多留一份。</p>
      <button type="button" class="btn-primary" :disabled="isExporting" @click="handleExportBackup">
        <Download :size="16" />
        {{ isExporting ? '导出中...' : '导出备份' }}
      </button>
    </section>

    <section class="card cinematic-card">
      <h2 class="section-title">关于</h2>
      <div class="info-list">
        <div class="info-item">
          <span>应用名称</span>
          <strong>LoveZs</strong>
        </div>
        <div class="info-item">
          <span>版本</span>
          <strong>1.0.0</strong>
        </div>
        <div class="info-item">
          <span>用途</span>
          <strong>记录美好时光与浪漫片段</strong>
        </div>
        <div class="info-item">
          <span>技术栈</span>
          <strong>Django + Vue 3</strong>
        </div>
      </div>
    </section>

    <section v-if="userStore.isAdmin" class="card danger-card cinematic-card">
      <h2 class="section-title danger-title">危险区域</h2>
      <p class="section-description">这些操作不可撤销，请谨慎操作。</p>
      <button type="button" class="btn-danger" :disabled="isClearing" @click="handleClearAllData">
        <Trash2 :size="16" />
        {{ isClearing ? '清除中...' : '清除所有数据' }}
      </button>
      <p class="danger-note">注意：该操作将删除数据库记录与媒体文件。</p>
    </section>
  </div>
</template>

<style scoped>
.card {
  padding: 1rem;
  margin-bottom: 1rem;
}

.section-description {
  margin: 0.45rem 0 0.95rem;
  color: var(--ink-soft);
  font-size: 0.9rem;
  line-height: 1.6;
}

.info-list {
  display: grid;
  gap: 0.6rem;
  margin-top: 0.9rem;
}

.info-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.65rem 0.75rem;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  background: rgba(255, 255, 255, 0.05);
}

.info-item span {
  color: var(--ink-soft);
}

.info-item strong {
  color: var(--ink);
}

.danger-card {
  border-color: rgba(255, 127, 154, 0.35);
}

.danger-title {
  color: var(--danger);
}

.danger-note {
  margin: 0.7rem 0 0;
  color: rgba(255, 127, 154, 0.82);
  font-size: 0.78rem;
}

@media (max-width: 640px) {
  .info-item {
    align-items: flex-start;
    flex-direction: column;
    gap: 0.25rem;
  }
}
</style>
