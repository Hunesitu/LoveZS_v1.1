<!--
Settings 页面
对应原 frontend/src/pages/Settings.tsx
设置页面，数据备份导出
-->
<script setup lang="ts">
import { ref } from 'vue'
import { useUiStore } from '@/stores/ui'
import { useUserStore } from '@/stores/user'
import { Download, Trash2, Settings as SettingsIcon } from 'lucide-vue-next'
import api from '@/api/client'

const uiStore = useUiStore()
const userStore = useUserStore()

const isExporting = ref(false)
const isClearing = ref(false)

// 导出备份
const handleExportBackup = async () => {
  isExporting.value = true
  try {
    const response = await api.get('/backup/export/', {
      responseType: 'blob'
    })

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

// 清除所有数据
const handleClearAllData = async () => {
  if (!window.confirm('⚠️ 危险操作！\n\n确定要清除所有数据吗？\n这将删除所有日记、照片、倒计时等数据，且不可恢复。')) {
    return
  }

  const confirmation = window.prompt('请输入 "DELETE ALL" 以确认：')
  if (confirmation !== 'DELETE ALL') {
    alert('操作已取消')
    return
  }

  if (!window.confirm('最后确认！所有数据将被永久删除！')) {
    return
  }

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
  <div class="settings-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <h1 class="page-title">
        <SettingsIcon :size="24" class="title-icon" />
        设置
      </h1>
      <p class="page-subtitle">管理你的应用数据与备份</p>
    </div>

    <!-- 数据备份 -->
    <div class="card">
      <h2 class="section-title">数据备份</h2>
      <p class="section-description">
        导出媒体文件备份（照片等）到本地 zip 文件
      </p>
      <button
        @click="handleExportBackup"
        :disabled="isExporting"
        class="btn-primary"
      >
        <Download :size="16" />
        <span class="ml-2">{{ isExporting ? '导出中...' : '导出备份' }}</span>
      </button>
    </div>

    <!-- 应用信息 -->
    <div class="card">
      <h2 class="section-title">关于</h2>
      <div class="info-list">
        <div class="info-item">
          <span class="info-label">应用名称</span>
          <span class="info-value">LoveZs</span>
        </div>
        <div class="info-item">
          <span class="info-label">版本</span>
          <span class="info-value">1.0.0</span>
        </div>
        <div class="info-item">
          <span class="info-label">用途</span>
          <span class="info-value">记录美好时光</span>
        </div>
        <div class="info-item">
          <span class="info-label">技术栈</span>
          <span class="info-value">Django + Vue 3</span>
        </div>
      </div>
    </div>

    <!-- 危险区域（仅管理员可见） -->
    <div v-if="userStore.isAdmin" class="card danger-card">
      <h2 class="section-title danger-title">危险区域</h2>
      <p class="section-description">
        这些操作不可撤销，请谨慎操作
      </p>
      <button
        @click="handleClearAllData"
        :disabled="isClearing"
        class="btn-danger"
      >
        <Trash2 :size="16" />
        <span class="ml-2">{{ isClearing ? '清除中...' : '清除所有数据' }}</span>
      </button>
      <p class="danger-note">
        注意：该操作将删除数据库记录与媒体文件
      </p>
    </div>
  </div>
</template>

<style scoped>
.settings-page {
  width: 100%;
  max-width: 52rem;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 1.25rem;
}

.page-title {
  margin: 0;
  font-size: 1.55rem;
  font-weight: 700;
  color: var(--text-primary);
  display: flex;
  align-items: center;
}

.title-icon {
  color: var(--pink-500);
  margin-right: 0.5rem;
}

.page-subtitle {
  margin: 0.3rem 0 0;
  color: var(--text-secondary);
}

.card {
  background: var(--bg-elevated);
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-lg);
  padding: 1rem;
  box-shadow: var(--shadow-soft);
  margin-bottom: 1rem;
}

.section-title {
  margin: 0 0 0.4rem;
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--text-primary);
}

.section-description {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin: 0 0 0.9rem;
}

.btn-primary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.625rem 1.2rem;
  background: linear-gradient(135deg, var(--pink-500) 0%, var(--rose-500) 100%);
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 8px 16px rgba(217, 117, 154, 0.24);
  transition: transform var(--dur-fast), box-shadow var(--dur-base), filter var(--dur-base);
}

.btn-primary:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 12px 20px rgba(217, 117, 154, 0.3);
  filter: brightness(1.02);
}

.btn-primary:disabled {
  opacity: 0.62;
  cursor: not-allowed;
}

.info-list {
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}

.info-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.55rem 0.65rem;
  border-radius: var(--radius-sm);
  border: 1px solid #f6e7ee;
  background: #fffafc;
  font-size: 0.875rem;
}

.info-label {
  color: var(--text-secondary);
}

.info-value {
  font-weight: 600;
  color: var(--text-primary);
}

.danger-card {
  border: 1px solid #f4ccd8;
  background: #fff8fa;
}

.danger-title {
  color: #a14867;
}

.btn-danger {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.56rem 1rem;
  background: #d07a98;
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: transform var(--dur-fast), background-color var(--dur-base), box-shadow var(--dur-base);
}

.btn-danger:hover:not(:disabled) {
  transform: translateY(-1px);
  background: #c16789;
  box-shadow: 0 10px 18px rgba(193, 103, 137, 0.26);
}

.btn-danger:disabled {
  opacity: 0.62;
  cursor: not-allowed;
}

.danger-note {
  font-size: 0.75rem;
  color: #875d71;
  margin: 0.6rem 0 0;
}

.ml-2 {
  margin-left: 0.5rem;
}

@media (max-width: 768px) {
  .page-title {
    font-size: 1.3rem;
  }

  .info-item {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.2rem;
  }
}
</style>
