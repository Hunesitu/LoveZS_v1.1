/**
 * Vue Router 閰嶇疆
 * 瀵瑰簲鍘? frontend/src/App.tsx 涓殑璺敱閰嶇疆
 */

import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import Layout from '@/components/Layout.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    component: Layout,
    children: [
      {
        path: '',
        redirect: '/dashboard'
      },
      {
        path: 'dashboard',
        name: 'dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '仪表盘' }
      },
      {
        path: 'diaries',
        name: 'diaries',
        component: () => import('@/views/Diaries.vue'),
        meta: { title: '日记' }
      },
      {
        path: 'diaries/new',
        name: 'diary-create',
        component: () => import('@/views/DiaryEditor.vue'),
        meta: { title: '新建日记' }
      },
      {
        path: 'diaries/:id',
        name: 'diary-detail',
        component: () => import('@/views/DiaryDetail.vue'),
        props: true,
        meta: { title: '日记详情' }
      },
      {
        path: 'diaries/:id/edit',
        name: 'diary-edit',
        component: () => import('@/views/DiaryEditor.vue'),
        props: true,
        meta: { title: '编辑日记' }
      },
      {
        path: 'countdowns',
        name: 'countdowns',
        component: () => import('@/views/Countdowns.vue'),
        meta: { title: '重要日' }
      },
      {
        path: 'settings',
        name: 'settings',
        component: () => import('@/views/Settings.vue'),
        meta: { title: '设置' }
      }
    ]
  },
  {
    // 404 椤甸潰
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard'
  }
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    // 婊氬姩琛屼负
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 璺敱瀹堝崼
router.beforeEach((to, from, next) => {
  // 璁剧疆椤甸潰鏍囬
  if (to.meta.title) {
    document.title = `${to.meta.title} - LoveZs`
  } else {
    document.title = 'LoveZs'
  }
  next()
})

export default router

