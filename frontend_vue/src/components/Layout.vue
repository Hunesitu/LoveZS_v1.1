<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  Bell,
  BookOpen,
  Calendar,
  ChevronRight,
  Heart,
  Home,
  LogOut,
  Menu,
  Settings,
  User,
  X,
} from 'lucide-vue-next'
import { useUiStore } from '@/stores/ui'
import { useUserStore } from '@/stores/user'
import { useNotificationStore } from '@/stores/notification'
import { logout } from '@/api/auth'

const route = useRoute()
const router = useRouter()
const uiStore = useUiStore()
const userStore = useUserStore()
const notificationStore = useNotificationStore()

const menuItems = [
  { name: 'dashboard', label: '首页', icon: Home, path: '/dashboard' },
  { name: 'diaries', label: '日记', icon: BookOpen, path: '/diaries' },
  { name: 'favorites', label: '收藏', icon: Heart, path: '/diaries?favorites=true' },
  { name: 'countdowns', label: '重要日', icon: Calendar, path: '/countdowns' },
  { name: 'notifications', label: '消息', icon: Bell, path: '/notifications', showBadge: true },
  { name: 'settings', label: '设置', icon: Settings, path: '/settings' },
]

const currentRouteName = computed(() => route.name as string)
const isFavoritesView = computed(() => route.name === 'diaries' && route.query.favorites === 'true')
const isMobile = ref(window.innerWidth < 768)
const showUserMenu = ref(false)

const checkMobile = () => {
  isMobile.value = window.innerWidth < 768
}

onMounted(() => {
  window.addEventListener('resize', checkMobile)
  checkMobile()

  if (userStore.isAuthenticated) {
    notificationStore.fetchNotifications()
  }
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})

const navigate = (path: string) => {
  router.push(path)
  if (isMobile.value) uiStore.closeSidebar()
}

const handleLogout = async () => {
  try {
    await logout()
    uiStore.showToast('已退出登录', 'success')
  } catch (error) {
    console.error('Logout error:', error)
  } finally {
    userStore.logout()
    showUserMenu.value = false
    router.push('/login')
  }
}
</script>

<template>
  <div class="layout">
    <Transition name="fade">
      <div
        v-if="isMobile && uiStore.isSidebarOpen"
        class="sidebar-overlay"
        @click="uiStore.closeSidebar"
      />
    </Transition>

    <aside class="sidebar" :class="{ mobile: isMobile, open: uiStore.isSidebarOpen }" aria-label="主导航">
      <div class="sidebar-header">
        <RouterLink class="logo" to="/dashboard" aria-label="LoveZS 首页" @click="isMobile && uiStore.closeSidebar()">
          <span class="heart-mark" aria-hidden="true">
            <Heart :size="16" fill="currentColor" />
          </span>
          <span class="logo-text">LoveZS</span>
        </RouterLink>
        <button v-if="isMobile" class="icon-btn" type="button" aria-label="关闭菜单" @click="uiStore.closeSidebar">
          <X :size="22" />
        </button>
      </div>

      <nav class="sidebar-nav">
        <button
          v-for="item in menuItems"
          :key="item.name"
          type="button"
          class="nav-item"
          :class="{ active: (item.name === 'favorites' && isFavoritesView) || (item.name === currentRouteName && !isFavoritesView) }"
          @click="navigate(item.path)"
        >
          <component :is="item.icon" :size="20" />
          <span class="nav-label">{{ item.label }}</span>
          <span v-if="item.showBadge && notificationStore.unreadCount > 0" class="badge">
            {{ notificationStore.unreadCount > 99 ? '99+' : notificationStore.unreadCount }}
          </span>
          <ChevronRight v-if="currentRouteName === item.name" :size="16" class="active-indicator" />
        </button>
      </nav>

      <div class="sidebar-footer">
        <button class="user-info" type="button" @click="showUserMenu = !showUserMenu">
          <span class="user-avatar">
            <User :size="17" />
          </span>
          <span class="user-details">
            <span class="user-name">{{ userStore.username || '用户' }}</span>
            <span class="user-email">{{ userStore.email || '未设置邮箱' }}</span>
          </span>
        </button>
        <Transition name="fade">
          <div v-if="showUserMenu" class="user-menu">
            <button class="logout-btn" type="button" @click="handleLogout">
              <LogOut :size="16" />
              <span>退出登录</span>
            </button>
          </div>
        </Transition>
      </div>
    </aside>

    <main class="main-content">
      <header v-if="isMobile" class="top-bar">
        <button class="icon-btn" type="button" aria-label="打开菜单" @click="uiStore.toggleSidebar">
          <Menu :size="22" />
        </button>
        <div class="top-bar-title">{{ route.meta?.title || 'LoveZS' }}</div>
      </header>

      <div class="page-content">
        <router-view />
      </div>
    </main>
  </div>
</template>

<style scoped>
.layout {
  --sidebar-collapsed-w: 64px;
  --sidebar-expanded-w: 248px;
  --sidebar-w: var(--sidebar-collapsed-w);
  --page-px: clamp(1rem, 3vw, 2.75rem);
  display: flex;
  min-height: 100vh;
  overflow-x: clip;
}

.sidebar {
  position: fixed;
  inset: 0 auto 0 0;
  z-index: 50;
  display: flex;
  flex-direction: column;
  width: var(--sidebar-collapsed-w);
  overflow: hidden;
  background:
    linear-gradient(180deg, rgba(12, 9, 18, 0.98), rgba(7, 7, 13, 0.98)),
    radial-gradient(circle at 100% 6%, rgba(245, 200, 143, 0.12), transparent 36%),
    radial-gradient(circle at 0% 32%, rgba(239, 111, 169, 0.12), transparent 38%);
  border-right: 1px solid rgba(245, 200, 143, 0.12);
  box-shadow: inset -1px 0 0 rgba(255, 255, 255, 0.04), 18px 0 54px rgba(0, 0, 0, 0.26);
  backdrop-filter: blur(18px);
  transition: width var(--dur-slow) ease, box-shadow var(--dur-slow) ease;
}

.sidebar:hover,
.sidebar:focus-within {
  width: var(--sidebar-expanded-w);
  box-shadow: inset -1px 0 0 rgba(255, 255, 255, 0.04), 26px 0 70px rgba(0, 0, 0, 0.36);
}

.sidebar::after {
  content: '';
  position: absolute;
  inset: 0;
  pointer-events: none;
  background:
    linear-gradient(180deg, transparent, rgba(245, 200, 143, 0.06) 52%, transparent),
    radial-gradient(1px 1px at 24% 18%, rgba(255,255,255,.5), transparent 2px),
    radial-gradient(1px 1px at 82% 42%, rgba(255,154,200,.42), transparent 2px);
  opacity: 0.55;
}

.sidebar-header {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: center;
  justify-content: space-between;
  min-height: 112px;
  width: var(--sidebar-expanded-w);
  padding: 34px 18px 22px;
}

.logo {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  min-width: 180px;
  color: #fff;
  font-size: 17px;
  font-weight: 800;
}

.heart-mark {
  display: inline-flex;
  flex: 0 0 auto;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  color: #fff;
  background: radial-gradient(circle at 36% 30%, #ffe2ef 0 20%, #ff7cb7 45%, #ee4fa1 100%);
  box-shadow: 0 0 24px rgba(255, 124, 183, 0.55);
}

.logo-text,
.sidebar-nav,
.sidebar-footer {
  opacity: 0;
  transform: translateX(-8px);
  transition: opacity var(--dur-base) ease, transform var(--dur-base) ease;
}

.sidebar:hover .logo-text,
.sidebar:focus-within .logo-text,
.sidebar:hover .sidebar-nav,
.sidebar:focus-within .sidebar-nav,
.sidebar:hover .sidebar-footer,
.sidebar:focus-within .sidebar-footer {
  opacity: 1;
  transform: translateX(0);
}

.sidebar:not(:hover):not(:focus-within) .sidebar-nav,
.sidebar:not(:hover):not(:focus-within) .sidebar-footer {
  pointer-events: none;
}

.sidebar-nav {
  position: relative;
  z-index: 1;
  display: flex;
  flex: 1;
  flex-direction: column;
  gap: 10px;
  width: var(--sidebar-expanded-w);
  padding: 8px 20px;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 14px;
  width: 100%;
  min-height: 54px;
  padding: 0 16px;
  border: 1px solid transparent;
  border-radius: 12px;
  color: #d8d0e5;
  background: transparent;
  text-align: left;
  transition: transform var(--dur-base) ease, background var(--dur-base) ease, border-color var(--dur-base) ease, color var(--dur-base) ease;
}

.nav-item svg {
  flex: 0 0 auto;
}

.nav-item:hover,
.nav-item:focus-visible {
  color: #fff;
  background: rgba(245, 200, 143, 0.08);
  outline: none;
  transform: translateX(3px);
}

.nav-item.active {
  color: var(--rose-bright);
  border-color: rgba(245, 200, 143, 0.14);
  background:
    linear-gradient(90deg, rgba(93, 33, 59, 0.66), rgba(37, 26, 55, 0.4)),
    radial-gradient(circle at 100% 50%, rgba(245, 200, 143, 0.12), transparent 38%);
  box-shadow: inset 0 0 0 1px rgba(255, 143, 200, 0.06), 0 10px 24px rgba(0, 0, 0, 0.18);
  font-weight: 700;
}

.badge,
.active-indicator {
  margin-left: auto;
}

.badge {
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  border-radius: 999px;
  color: #fff;
  background: var(--rose);
  font-size: 0.7rem;
  font-weight: 800;
  text-align: center;
  line-height: 20px;
  box-shadow: 0 0 14px rgba(240, 120, 182, 0.45);
}

.sidebar-footer {
  position: relative;
  z-index: 1;
  width: var(--sidebar-expanded-w);
  padding: 1rem 20px 1.5rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 0.5rem;
  border: 1px solid transparent;
  border-radius: 10px;
  color: #fff;
  background: transparent;
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.06);
}

.user-avatar {
  display: inline-flex;
  flex: 0 0 auto;
  align-items: center;
  justify-content: center;
  width: 30px;
  height: 30px;
  border: 1px solid rgba(255, 255, 255, 0.28);
  border-radius: 50%;
  background: linear-gradient(135deg, #f8c7d6, #5b6a9f);
}

.user-details {
  display: grid;
  min-width: 0;
  text-align: left;
}

.user-name {
  overflow: hidden;
  color: #fff;
  font-size: 15px;
  font-weight: 700;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-email {
  overflow: hidden;
  color: #8b8498;
  font-size: 11px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.user-menu {
  position: absolute;
  right: 20px;
  bottom: calc(100% - 0.5rem);
  left: 20px;
  overflow: hidden;
  border: 1px solid var(--line);
  border-radius: var(--radius-md);
  background: rgba(18, 16, 36, 0.96);
  box-shadow: var(--shadow-md);
}

.logout-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  width: 100%;
  min-height: 42px;
  border: 0;
  color: var(--ink-soft);
  background: transparent;
}

.logout-btn:hover {
  color: var(--rose-bright);
  background: rgba(240, 120, 182, 0.12);
}

.main-content {
  display: flex;
  flex: 1;
  flex-direction: column;
  min-width: 0;
  margin-left: var(--sidebar-w);
}

.page-content {
  width: 100%;
  max-width: 1480px;
  margin: 0 auto;
  padding: clamp(1rem, 2.4vw, 2rem) var(--page-px) clamp(1.5rem, 3vw, 3.5rem);
}

.top-bar {
  position: sticky;
  top: 0;
  z-index: 30;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  height: 56px;
  padding: 0 1rem;
  border-bottom: 1px solid rgba(245, 200, 143, 0.12);
  background: rgba(7, 7, 13, 0.86);
  backdrop-filter: blur(16px);
}

.top-bar-title {
  color: #fff;
  font-weight: 700;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  padding: 0;
  border: 1px solid var(--line);
  border-radius: var(--radius-sm);
  color: var(--ink-soft);
  background: rgba(255, 255, 255, 0.06);
  transition: transform var(--dur-base) ease, color var(--dur-base) ease, border-color var(--dur-base) ease, background var(--dur-base) ease;
}

.icon-btn:hover {
  color: var(--rose-bright);
  border-color: var(--line-strong);
  background: rgba(240, 120, 182, 0.14);
  transform: translateY(-1px);
}

.sidebar-overlay {
  position: fixed;
  inset: 0;
  z-index: 40;
  background: rgba(0, 0, 0, 0.58);
  backdrop-filter: blur(3px);
}

@media (max-width: 767px) {
  .layout {
    --sidebar-w: 0px;
  }

  .sidebar {
    width: min(86vw, 312px);
    transform: translateX(-100%);
    transition: transform var(--dur-slow) ease;
  }

  .sidebar:hover,
  .sidebar:focus-within {
    width: min(86vw, 312px);
    box-shadow: inset -1px 0 0 rgba(255, 255, 255, 0.04), 18px 0 54px rgba(0, 0, 0, 0.26);
  }

  .sidebar.open {
    transform: translateX(0);
  }

  .sidebar-header,
  .sidebar-nav,
  .sidebar-footer {
    width: min(86vw, 312px);
  }

  .logo-text,
  .sidebar-nav,
  .sidebar-footer {
    opacity: 1;
    transform: none;
  }

  .sidebar:not(:hover):not(:focus-within) .sidebar-nav,
  .sidebar:not(:hover):not(:focus-within) .sidebar-footer {
    pointer-events: auto;
  }

  .main-content {
    margin-left: 0;
  }

  .page-content {
    padding: 1rem max(1rem, env(safe-area-inset-left)) calc(1.5rem + env(safe-area-inset-bottom));
  }
}
</style>
