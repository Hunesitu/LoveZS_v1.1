<script setup lang="ts">
import { RouterView } from 'vue-router'
import { useUiStore } from '@/stores/ui'

const uiStore = useUiStore()
</script>

<template>
  <RouterView />

  <Transition name="slide-up">
    <div v-if="uiStore.toast.show" class="toast" :class="uiStore.toast.type">
      <span>{{ uiStore.toast.message }}</span>
      <button class="toast-close" type="button" aria-label="关闭通知" @click="uiStore.hideToast">×</button>
    </div>
  </Transition>
</template>

<style>
.toast {
  position: fixed;
  right: 1.5rem;
  bottom: 1.5rem;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.85rem;
  width: min(92vw, 420px);
  padding: 0.9rem 1rem;
  border: 1px solid var(--line);
  border-radius: var(--radius-lg);
  color: var(--ink);
  background: rgba(18, 16, 36, 0.94);
  box-shadow: var(--shadow-lg);
  backdrop-filter: blur(18px);
}

.toast.success {
  border-color: rgba(139, 230, 189, 0.45);
}

.toast.error {
  border-color: rgba(255, 127, 154, 0.55);
}

.toast.info {
  border-color: rgba(159, 200, 255, 0.45);
}

.toast.warning {
  border-color: rgba(245, 200, 143, 0.5);
}

.toast-close {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  padding: 0;
  border: 1px solid var(--line);
  border-radius: 999px;
  color: var(--ink-soft);
  background: rgba(255, 255, 255, 0.06);
  font-size: 1.2rem;
  line-height: 1;
}

.toast-close:hover {
  color: var(--rose-bright);
  border-color: var(--line-strong);
}

@media (max-width: 768px) {
  .toast {
    right: 1rem;
    bottom: 1rem;
    left: 1rem;
    width: auto;
  }
}
</style>
