<!--
Layout 布局组件
对应原 frontend/src/components/Layout.tsx
提供侧边栏导航和主内容区域
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
  ChevronRight,
  LogOut,
  User
} from 'lucide-vue-next'
import { useUiStore } from '@/stores/ui'
import { useUserStore } from '@/stores/user'
import { logout } from '@/api/auth'

const route = useRoute()
const router = useRouter()
const uiStore = useUiStore()
const userStore = useUserStore()

// 侧边栏菜单项
const menuItems = [
  { name: 'dashboard', label: '仪表盘', icon: Home, path: '/dashboard' },
  { name: 'diaries', label: '日记', icon: BookOpen, path: '/diaries' },
  { name: 'countdowns', label: '重要日', icon: Calendar, path: '/countdowns' },
  { name: 'settings', label: '设置', icon: Settings, path: '/settings' },
]

// 当前激活路由名称
const currentRouteName = computed(() => route.name as string)

// 检测是否是移动端
const isMobile = ref(window.innerWidth < 768)

// 响应式处理窗口大小变化
const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}

if (typeof window !== 'undefined') {
  window.addEventListener('resize', checkMobile)
  checkMobile()
}

// 导航跳转
const navigate = (path: string) => {
  router.push(path)
  // 在移动端点击菜单项后关闭侧边栏
  if (isMobile.value) {
    uiStore.closeSidebar()
  }
}

// 切换侧边栏
const toggleSidebar = () => {
  uiStore.toggleSidebar()
}

// 关闭侧边栏
const closeSidebar = () => {
  uiStore.closeSidebar()
}

// 用户菜单显示状态
const showUserMenu = ref(false)

// 登出
const handleLogout = async () => {
  try {
    await logout()
    userStore.logout()
    uiStore.showToast('已登出', 'success')
    router.push('/login')
  } catch (error) {
    console.error('Logout error:', error)
    // 即使请求失败也清除本地状态
    userStore.logout()
    router.push('/login')
  }
  showUserMenu.value = false
}

// 切换用户菜单
const toggleUserMenu = () => {
  showUserMenu.value = !showUserMenu.value
}
</script>

<template>
  <div class="layout">
    <!-- 移动端遮罩层 (点击关闭侧边栏) -->
    <Transition name="fade">
      <div
        v-if="isMobile && uiStore.isSidebarOpen"
        class="sidebar-overlay"
        @click="closeSidebar"
      ></div>
    </Transition>

    <!-- 侧边栏 -->
    <aside class="sidebar" :class="{ 'mobile': isMobile, 'open': uiStore.isSidebarOpen }">
      <!-- Logo -->
      <div class="sidebar-header">
        <div class="logo">
          <Heart :size="28" class="logo-icon" />
          <span class="logo-text">LoveZs</span>
        </div>
        <!-- 关闭按钮 (仅移动端) -->
        <button v-if="isMobile" class="close-btn" @click="closeSidebar">
          <X :size="24" />
        </button>
      </div>

      <!-- 菜单导航 -->
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

      <!-- 底部用户信息 -->
      <div class="sidebar-footer">
        <div class="user-section">
          <div class="user-info" @click="toggleUserMenu">
            <div class="user-avatar">
              <User :size="18" />
            </div>
            <div class="user-details">
              <p class="user-name">{{ userStore.username || '用户' }}</p>
              <p class="user-email">{{ userStore.email || '' }}</p>
            </div>
          </div>
          <Transition name="fade">
            <div v-if="showUserMenu" class="user-menu">
              <button class="logout-btn" @click="handleLogout">
                <LogOut :size="16" />
                <span>登出</span>
              </button>
            </div>
          </Transition>
        </div>
      </div>
    </aside>

    <!-- 主内容区域 -->
    <main class="main-content">
      <!-- 顶部导航栏 (仅移动端) -->
      <header v-if="isMobile" class="top-bar">
        <button class="menu-btn" @click="toggleSidebar">
          <Menu :size="24" />
        </button>
        <div class="top-bar-title">
          <template v-if="route.meta?.title">{{ route.meta.title }}</template>
        </div>
      </header>

      <!-- 页面内容 -->
      <div class="page-content">
        <router-view />
      </div>
    </main>
  </div>
</template>

<style scoped>
/* ========================================
   全局布局
   ======================================== */
.layout {
  display: flex;
  min-height: 100vh;
}

/* ========================================
   侧边栏样式
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

.user-section {
  position: relative;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.5rem;
  border-radius: 0.625rem;
  cursor: pointer;
  transition: background-color var(--dur-fast);
}

.user-info:hover {
  background: var(--pink-50);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--pink-500) 0%, var(--rose-500) 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
}

.user-details {
  flex: 1;
  overflow: hidden;
}

.user-name {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-email {
  margin: 0;
  font-size: 0.75rem;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-menu {
  position: absolute;
  bottom: 100%;
  left: 0;
  right: 0;
  margin-bottom: 0.5rem;
  background: #fff;
  border: 1px solid var(--border-soft);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-soft);
  overflow: hidden;
}

.logout-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.625rem;
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 0.875rem;
  cursor: pointer;
  transition: background-color var(--dur-fast), color var(--dur-fast);
}

.logout-btn:hover {
  background: var(--pink-50);
  color: var(--pink-500);
}

/* 遮罩层 */
.sidebar-overlay {
  position: fixed;
  inset: 0;
  background: rgba(42, 31, 38, 0.28);
  backdrop-filter: blur(2px);
  z-index: 40;
}

/* ========================================
   主内容区域样式
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

/* 顶部导航栏 (仅移动端) */
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

/* 页面内容 */
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
   动画效果
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
}
</style>
