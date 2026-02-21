/**
 * Vue Router 路由配置
 * 对应原 frontend/src/App.tsx 的路由管理
 */

import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import Layout from '@/components/Layout.vue'
import { useUserStore } from '@/stores/user'

const routes: RouteRecordRaw[] = [
  // 公共路由（不需要认证）
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', public: true }
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/views/Register.vue'),
    meta: { title: '注册', public: true }
  },
  // 应用主路由（需要认证）
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
        meta: { title: '首页' }
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
        path: 'notifications',
        name: 'notifications',
        component: () => import('@/views/Notifications.vue'),
        meta: { title: '消息' }
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
    // 404 重定向
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard'
  }
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    // 滚动行为控制
    if (savedPosition) {
      return savedPosition
    } else {
      return { top: 0 }
    }
  }
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = `${to.meta.title} - LoveZs`
  } else {
    document.title = 'LoveZs'
  }

  // 认证检查
  const userStore = useUserStore()
  const isAuthenticated = userStore.isAuthenticated
  const isPublicRoute = to.meta.public === true

  if (!isAuthenticated && !isPublicRoute) {
    // 未登录且访问非公共路由，跳转到登录页
    next({
      name: 'login',
      query: { redirect: to.fullPath }
    })
  } else if (isAuthenticated && (to.name === 'login' || to.name === 'register')) {
    // 已登录用户访问登录/注册页，跳转到首页
    next({ name: 'dashboard' })
  } else {
    next()
  }
})

export default router
