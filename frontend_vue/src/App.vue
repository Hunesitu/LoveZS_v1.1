<script setup lang="ts">
import { RouterView } from 'vue-router'
import { useUiStore } from '@/stores/ui'

const uiStore = useUiStore()
</script>

<template>
  <RouterView />

  <!-- 全局 Toast 通知 -->
  <Transition name="slide-up">
    <div v-if="uiStore.toast.show" class="toast" :class="uiStore.toast.type">
      <span>{{ uiStore.toast.message }}</span>
      <button class="toast-close" @click="uiStore.hideToast">×</button>
    </div>
  </Transition>
</template>

<style>
/* 全局样式重置 */
*,
*::before,
*::after {
  box-sizing: border-box;
}

html {
  font-size: 16px;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  margin: 0;
  padding: 0;
  background-color: var(--bg-base);
  color: var(--text-primary);
}

#app {
  min-height: 100vh;
}

/* 全局 Toast 样式 */
.toast {
  position: fixed;
  bottom: 1.5rem;
  right: 1.5rem;
  max-width: min(92vw, 420px);
  color: var(--text-primary);
  background: #fff7fa;
  border: 1px solid transparent;
  padding: 0.875rem 1rem;
  border-radius: 0.875rem;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
}

.toast.success {
  border-color: #bde7d4;
  background: #ecfaf3;
}

.toast.error {
  border-color: #f7c6cf;
  background: #fff1f3;
}

.toast.info {
  border-color: #cfe4ff;
  background: #eff6ff;
}

.toast.warning {
  border-color: #f6dfb9;
  background: #fff8ea;
}

.toast-close {
  background: transparent;
  border: none;
  color: var(--text-secondary);
  font-size: 1.25rem;
  cursor: pointer;
  padding: 0;
  line-height: 1;
  transition: color 0.2s;
}

.toast-close:hover {
  color: var(--text-primary);
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.slide-up-enter-from,
.slide-up-leave-to {
  opacity: 0;
  transform: translateY(10px);
}

@media (max-width: 768px) {
  .toast {
    left: 1rem;
    right: 1rem;
    bottom: 1rem;
    max-width: none;
  }
}
</style>
