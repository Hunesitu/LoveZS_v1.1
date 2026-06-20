import { createRouter, createWebHistory, type RouteRecordRaw } from 'vue-router'
import Layout from '@/components/Layout.vue'
import { useUserStore } from '@/stores/user'

const routes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', public: true },
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/views/Register.vue'),
    meta: { title: '注册', public: true },
  },
  {
    path: '/',
    component: Layout,
    children: [
      {
        path: '',
        redirect: '/dashboard',
      },
      {
        path: 'dashboard',
        name: 'dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '首页' },
      },
      {
        path: 'diaries',
        name: 'diaries',
        component: () => import('@/views/Diaries.vue'),
        meta: { title: '日记' },
      },
      {
        path: 'diaries/new',
        name: 'diary-create',
        component: () => import('@/views/DiaryEditor.vue'),
        meta: { title: '新建日记' },
      },
      {
        path: 'diaries/:id',
        name: 'diary-detail',
        component: () => import('@/views/DiaryDetail.vue'),
        props: true,
        meta: { title: '日记详情' },
      },
      {
        path: 'diaries/:id/edit',
        name: 'diary-edit',
        component: () => import('@/views/DiaryEditor.vue'),
        props: true,
        meta: { title: '编辑日记' },
      },
      {
        path: 'countdowns',
        name: 'countdowns',
        component: () => import('@/views/Countdowns.vue'),
        meta: { title: '重要日' },
      },
      {
        path: 'notifications',
        name: 'notifications',
        component: () => import('@/views/Notifications.vue'),
        meta: { title: '消息' },
      },
      {
        path: 'settings',
        name: 'settings',
        component: () => import('@/views/Settings.vue'),
        meta: { title: '设置' },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/dashboard',
  },
]

export const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior(to, from, savedPosition) {
    return savedPosition || { top: 0 }
  },
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - LoveZs` : 'LoveZs'

  const userStore = useUserStore()
  const isAuthenticated = userStore.isAuthenticated
  const isPublicRoute = to.meta.public === true

  if (!isAuthenticated && !isPublicRoute) {
    next({
      name: 'login',
      query: { redirect: to.fullPath },
    })
    return
  }

  if (isAuthenticated && (to.name === 'login' || to.name === 'register')) {
    next({ name: 'dashboard' })
    return
  }

  next()
})

export default router
