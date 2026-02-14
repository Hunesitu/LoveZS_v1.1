<!--
登录页面
用户登录认证
-->
<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useUiStore } from '@/stores/ui'
import { login } from '@/api/auth'
import type { LoginRequest } from '@/types'
import { LogIn } from 'lucide-vue-next'

const router = useRouter()
const userStore = useUserStore()
const uiStore = useUiStore()

const formData = ref<LoginRequest>({
  username: '',
  password: ''
})

const isSubmitting = ref(false)
const showPassword = ref(false)

// 表单验证
const validateForm = (): boolean => {
  if (!formData.value.username) {
    uiStore.showToast('请输入用户名', 'error')
    return false
  }
  if (!formData.value.password) {
    uiStore.showToast('请输入密码', 'error')
    return false
  }
  return true
}

// 登录
const handleLogin = async () => {
  if (!validateForm()) return

  isSubmitting.value = true
  try {
    const response = await login(formData.value)
    if (response.success && response.data) {
      userStore.login(response.data.token, response.data.user)
      uiStore.showToast('登录成功', 'success')

      // 跳转到原目标页面或首页
      const redirect = router.currentRoute.value.query.redirect as string
      router.push(redirect || '/')
    }
  } catch (error: any) {
    console.error('Login error:', error)
    const message = error.response?.data?.message || error.response?.data?.detail || '登录失败'
    uiStore.showToast(message, 'error')
  } finally {
    isSubmitting.value = false
  }
}

// 跳转到注册页
const goToRegister = () => {
  router.push('/register')
}
</script>

<template>
  <div class="login-page">
    <div class="login-card">
      <!-- Logo/标题 -->
      <div class="login-header">
        <div class="logo">LoveZs</div>
        <h1 class="title">欢迎回来</h1>
        <p class="subtitle">登录到你的回忆空间</p>
      </div>

      <!-- 登录表单 -->
      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label for="username">用户名</label>
          <input
            id="username"
            v-model="formData.username"
            type="text"
            class="form-input"
            placeholder="请输入用户名"
            autocomplete="username"
            :disabled="isSubmitting"
          />
        </div>

        <div class="form-group">
          <label for="password">密码</label>
          <div class="password-input">
            <input
              id="password"
              v-model="formData.password"
              :type="showPassword ? 'text' : 'password'"
              class="form-input"
              placeholder="请输入密码"
              autocomplete="current-password"
              :disabled="isSubmitting"
            />
            <button
              type="button"
              class="toggle-password"
              @click="showPassword = !showPassword"
              tabindex="-1"
            >
              {{ showPassword ? '隐藏' : '显示' }}
            </button>
          </div>
        </div>

        <button
          type="submit"
          class="login-btn"
          :disabled="isSubmitting"
        >
          <LogIn :size="18" />
          <span>{{ isSubmitting ? '登录中...' : '登录' }}</span>
        </button>
      </form>

      <!-- 注册链接 -->
      <div class="register-link">
        还没有账号？
        <button type="button" @click="goToRegister" class="link-btn">
          立即注册
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  background: linear-gradient(135deg, #fce4f4 0%, #ffe6ec 50%, #fff0f5 100%);
}

.login-card {
  width: 100%;
  max-width: 400px;
  background: #fff;
  border-radius: var(--radius-xl);
  box-shadow: 0 20px 60px rgba(217, 117, 154, 0.15);
  padding: 2.5rem;
  animation: fadeInUp 0.4s ease-out;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.login-header {
  text-align: center;
  margin-bottom: 2rem;
}

.logo {
  font-size: 2rem;
  font-weight: 800;
  background: linear-gradient(135deg, var(--pink-500) 0%, var(--rose-500) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 0.75rem;
}

.title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0 0 0.5rem;
}

.subtitle {
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin: 0;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group > label {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-primary);
}

.form-input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1.5px solid #f0d0e0;
  border-radius: var(--radius-md);
  font-size: 0.9375rem;
  color: var(--text-primary);
  background: #fff;
  transition: border-color var(--dur-fast), box-shadow var(--dur-fast);
}

.form-input:focus {
  outline: none;
  border-color: var(--pink-400);
  box-shadow: 0 0 0 3px rgba(217, 117, 154, 0.1);
}

.form-input:disabled {
  background: #fafafa;
  cursor: not-allowed;
}

.password-input {
  position: relative;
  display: flex;
}

.password-input .form-input {
  padding-right: 4rem;
}

.toggle-password {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--pink-500);
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  padding: 0.25rem 0.5rem;
}

.toggle-password:hover {
  color: var(--rose-500);
}

.login-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.875rem;
  margin-top: 0.5rem;
  background: linear-gradient(135deg, var(--pink-500) 0%, var(--rose-500) 100%);
  color: #fff;
  border: none;
  border-radius: var(--radius-md);
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 8px 16px rgba(217, 117, 154, 0.24);
  transition: transform var(--dur-fast), box-shadow var(--dur-base);
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 12px 20px rgba(217, 117, 154, 0.3);
}

.login-btn:active:not(:disabled) {
  transform: translateY(0);
}

.login-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.register-link {
  text-align: center;
  margin-top: 1.5rem;
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.link-btn {
  background: none;
  border: none;
  color: var(--pink-500);
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  padding: 0;
  font-size: inherit;
}

.link-btn:hover {
  color: var(--rose-500);
  text-decoration: underline;
}
</style>
