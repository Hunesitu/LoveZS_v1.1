/**
 * Pinia 状态管理 - UI Store
 */

import { ref } from 'vue'
import { defineStore } from 'pinia'

export const useUiStore = defineStore('ui', () => {
  // 侧边栏状态（移动端）
  const isSidebarOpen = ref(false)

  // 加载状态
  const globalLoading = ref(false)

  // Toast 通知
  const toast = ref({
    show: false,
    message: '',
    type: 'info' as 'success' | 'error' | 'info' | 'warning'
  })

  /**
   * 切换侧边栏
   */
  const toggleSidebar = () => {
    isSidebarOpen.value = !isSidebarOpen.value
  }

  /**
   * 关闭侧边栏
   */
  const closeSidebar = () => {
    isSidebarOpen.value = false
  }

  /**
   * 显示 Toast 通知
   */
  const showToast = (message: string, type: 'success' | 'error' | 'info' | 'warning' = 'info') => {
    toast.value = {
      show: true,
      message,
      type
    }

    // 3秒后自动隐藏
    setTimeout(() => {
      toast.value.show = false
    }, 3000)
  }

  /**
   * 隐藏 Toast
   */
  const hideToast = () => {
    toast.value.show = false
  }

  /**
   * 设置全局加载状态
   */
  const setGlobalLoading = (loading: boolean) => {
    globalLoading.value = loading
  }

  return {
    // 状态
    isSidebarOpen,
    globalLoading,
    toast,

    // 方法
    toggleSidebar,
    closeSidebar,
    showToast,
    hideToast,
    setGlobalLoading,
  }
})
