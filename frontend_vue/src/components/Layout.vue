<!--
Layout 缁勪欢
瀵瑰簲鍘? frontend/src/components/Layout.tsx
鍖呭惈渚ц竟鏍忓鑸拰涓诲唴瀹瑰尯鍩?
-->
<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Home,
  BookOpen,
  Calendar,
  Settings,
  Menu,
  X,
  Heart,
  ChevronRight
} from 'lucide-vue-next'
import { useUiStore } from '@/stores/ui'

const route = useRoute()
const router = useRouter()
const uiStore = useUiStore()

// 渚ц竟鏍忚彍鍗曢」
const menuItems = [
  { name: 'dashboard', label: '仪表盘', icon: Home, path: '/dashboard' },
  { name: 'diaries', label: '日记', icon: BookOpen, path: '/diaries' },
  { name: 'countdowns', label: '重要日', icon: Calendar, path: '/countdowns' },
  { name: 'settings', label: '设置', icon: Settings, path: '/settings' },
]

// 褰撳墠璺敱鍚嶇О
const currentRouteName = computed(() => route.name as string)

// 鍒ゆ柇鏄惁鏄Щ鍔ㄧ
const isMobile = ref(window.innerWidth < 768)

// 鐩戝惉绐楀彛澶у皬鍙樺寲
const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}

if (typeof window !== 'undefined') {
  window.addEventListener('resize', checkMobile)
  checkMobile()
}

// 璺宠浆鍒版寚瀹氳矾鐢?
const navigate = (path: string) => {
  router.push(path)
  // 绉诲姩绔偣鍑诲悗鍏抽棴渚ц竟鏍?
  if (isMobile.value) {
    uiStore.closeSidebar()
  }
}

// 鍒囨崲渚ц竟鏍?
const toggleSidebar = () => {
  uiStore.toggleSidebar()
}

// 鍏抽棴渚ц竟鏍?
const closeSidebar = () => {
  uiStore.closeSidebar()
}
</script>

<template>
  <div class="layout">
    <!-- 閬僵灞?(绉诲姩绔? -->
    <Transition name="fade">
      <div
        v-if="isMobile && uiStore.isSidebarOpen"
        class="sidebar-overlay"
        @click="closeSidebar"
      ></div>
    </Transition>

    <!-- 渚ц竟鏍?-->
    <aside class="sidebar" :class="{ 'mobile': isMobile, 'open': uiStore.isSidebarOpen }">
      <!-- Logo -->
      <div class="sidebar-header">
        <div class="logo">
          <Heart :size="28" class="logo-icon" />
          <span class="logo-text">LoveZs</span>
        </div>
        <!-- 鍏抽棴鎸夐挳 (绉诲姩绔? -->
        <button v-if="isMobile" class="close-btn" @click="closeSidebar">
          <X :size="24" />
        </button>
      </div>

      <!-- 瀵艰埅鑿滃崟 -->
      <nav class="sidebar-nav">
        <ul class="nav-list">
          <li
            v-for="item in menuItems"
            :key="item.name"
            class="nav-item"
            :class="{ active: currentRouteName === item.name }"
            @click="navigate(item.path)"
          >
            <component :is="item.icon" :size="20" />
            <span>{{ item.label }}</span>
            <ChevronRight v-if="currentRouteName === item.name" :size="16" class="active-indicator" />
          </li>
        </ul>
      </nav>

      <!-- 搴曢儴淇℃伅 -->
      <div class="sidebar-footer">
        <p class="footer-text">记录美好时光 💕</p>
      </div>
    </aside>

    <!-- 涓诲唴瀹瑰尯鍩?-->
    <main class="main-content">
      <!-- 椤堕儴鏍?(绉诲姩绔眽鍫¤彍鍗? -->
      <header v-if="isMobile" class="top-bar">
        <button class="menu-btn" @click="toggleSidebar">
          <Menu :size="24" />
        </button>
        <div class="top-bar-title">
          <template v-if="route.meta?.title">{{ route.meta.title }}</template>
        </div>
      </header>

      <!-- 椤甸潰鍐呭 -->
      <div class="page-content">
        <router-view />
      </div>
    </main>

    <!-- Toast 閫氱煡 -->
    <Transition name="slide-up">
      <div v-if="uiStore.toast.show" class="toast" :class="uiStore.toast.type">
        <span>{{ uiStore.toast.message }}</span>
        <button class="toast-close" @click="uiStore.hideToast">脳</button>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
/* ========================================
   甯冨眬鏍峰紡
   ======================================== */
.layout {
  display: flex;
  min-height: 100vh;
}

/* ========================================
   渚ц竟鏍忔牱寮?
   ======================================== */
.sidebar {
  width: 248px;
  background: rgba(255, 255, 255, 0.88);
  border-right: 1px solid var(--border-soft);
  box-shadow: 8px 0 24px rgba(232, 143, 176, 0.08);
  backdrop-filter: blur(10px);
  display: flex;
  flex-direction: column;
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  z-index: 50;
  transition: transform var(--dur-slow) ease;
}

.sidebar.mobile {
  transform: translateX(-100%);
}

.sidebar.open {
  transform: translateX(0);
}

.sidebar-header {
  padding: 1.5rem 1.25rem;
  border-bottom: 1px solid var(--border-soft);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 700;
  font-size: 1.125rem;
  color: var(--text-primary);
}

.logo-icon {
  color: var(--pink-500);
}

.logo-text {
  letter-spacing: 0.02em;
}

.close-btn {
  border: 1px solid transparent;
  background: transparent;
  color: var(--text-secondary);
  padding: 0.375rem;
  border-radius: 0.625rem;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: transform var(--dur-fast), background-color var(--dur-base), color var(--dur-base), border-color var(--dur-base);
}

.close-btn:hover {
  background: var(--pink-50);
  border-color: var(--border-soft);
  color: var(--pink-500);
  transform: translateY(-1px);
}

.sidebar-nav {
  flex: 1;
  padding: 1rem 0.75rem;
  overflow-y: auto;
}

.nav-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.7rem 0.85rem;
  border-radius: 0.75rem;
  border: 1px solid transparent;
  color: var(--text-secondary);
  cursor: pointer;
  transition: transform var(--dur-fast), border-color var(--dur-base), background-color var(--dur-base), color var(--dur-base);
}

.nav-item:hover {
  background: var(--pink-50);
  border-color: var(--border-soft);
  color: var(--text-primary);
  transform: translateX(2px);
}

.nav-item.active {
  background: linear-gradient(135deg, #fff1f6 0%, #ffe8f1 100%);
  border-color: var(--border-strong);
  color: var(--pink-500);
  font-weight: 600;
}

.active-indicator {
  margin-left: auto;
}

.sidebar-footer {
  padding: 1rem 1.25rem;
  border-top: 1px solid var(--border-soft);
}

.footer-text {
  margin: 0;
  font-size: 0.8125rem;
  color: var(--text-secondary);
  text-align: center;
}

/* 閬僵灞?*/
.sidebar-overlay {
  position: fixed;
  inset: 0;
  background: rgba(42, 31, 38, 0.28);
  backdrop-filter: blur(2px);
  z-index: 40;
}

/* ========================================
   涓诲唴瀹瑰尯鍩熸牱寮?
   ======================================== */
.main-content {
  flex: 1;
  margin-left: 248px;
  display: flex;
  flex-direction: column;
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
  }
}

/* 椤堕儴鏍?(绉诲姩绔? */
.top-bar {
  display: none;
  height: 60px;
  background: rgba(255, 255, 255, 0.9);
  border-bottom: 1px solid var(--border-soft);
  backdrop-filter: blur(8px);
  align-items: center;
  padding: 0 1rem;
  gap: 0.75rem;
}

.menu-btn {
  border: 1px solid transparent;
  background: transparent;
  color: var(--text-secondary);
  padding: 0.375rem;
  border-radius: 0.625rem;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: transform var(--dur-fast), background-color var(--dur-base), color var(--dur-base), border-color var(--dur-base);
}

.menu-btn:hover {
  background: var(--pink-50);
  border-color: var(--border-soft);
  color: var(--pink-500);
  transform: translateY(-1px);
}

.top-bar-title {
  font-weight: 600;
  font-size: 1rem;
  color: var(--text-primary);
}

@media (max-width: 768px) {
  .top-bar {
    display: flex;
  }
}

/* 椤甸潰鍐呭 */
.page-content {
  flex: 1;
  padding: 1.75rem;
  max-width: 1240px;
  margin: 0 auto;
  width: 100%;
}

@media (max-width: 768px) {
  .page-content {
    padding: 1rem;
  }
}

/* ========================================
   Toast 閫氱煡鏍峰紡
   ======================================== */
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
  box-shadow: var(--shadow-soft);
  z-index: 100;
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
  transition: color var(--dur-base);
}

.toast-close:hover {
  color: var(--text-primary);
}

/* ========================================
   杩囨浮鍔ㄧ敾
   ======================================== */
.fade-enter-active,
.fade-leave-active {
  transition: opacity var(--dur-slow) ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: opacity var(--dur-slow) ease, transform var(--dur-slow) ease;
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

