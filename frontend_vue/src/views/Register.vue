<!--
注册页面
新用户注册（简化版：无需邮箱）
-->
<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useUiStore } from '@/stores/ui'
import { register } from '@/api/auth'
import type { RegisterRequest } from '@/types'
import { UserPlus } from 'lucide-vue-next'

const router = useRouter()
const userStore = useUserStore()
const uiStore = useUiStore()

const formData = ref<RegisterRequest>({
  username: '',
  password: ''
})

const confirmPassword = ref('')
const isSubmitting = ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)

// 表单验证
const validateForm = (): boolean => {
  if (!formData.value.username) {
    uiStore.showToast('请输入用户名', 'error')
    return false
  }
  if (formData.value.username.length < 3) {
    uiStore.showToast('用户名至少需要3个字符', 'error')
    return false
  }
  if (!formData.value.password) {
    uiStore.showToast('请输入密码', 'error')
    return false
  }
  if (formData.value.password.length < 6) {
    uiStore.showToast('密码至少需要6个字符', 'error')
    return false
  }
  if (formData.value.password !== confirmPassword.value) {
    uiStore.showToast('两次密码不一致', 'error')
    return false
  }
  return true
}

// 注册
const handleRegister = async () => {
  if (!validateForm()) return

  isSubmitting.value = true
  try {
    const response = await register(formData.value)
    if (response.success && response.data) {
      userStore.login(response.data.token, response.data.user)
      uiStore.showToast('注册成功', 'success')

      // 跳转到首页
      router.push('/')
    }
  } catch (error: any) {
    console.error('Register error:', error)
    const data = error.response?.data
    // 优先显示具体字段错误，再显示通用 message
    const message = data?.errors?.username?.[0]
      || data?.errors?.password?.[0]
      || data?.message
      || '注册失败'
    uiStore.showToast(message, 'error')
  } finally {
    isSubmitting.value = false
  }
}

// 跳转到登录页
const goToLogin = () => {
  router.push('/login')
}
</script>

<template>
  <div class="register-page">
    <div class="register-card">
      <!-- Logo/标题 -->
      <div class="register-header">
        <div class="logo">LoveZs</div>
        <h1 class="title">创建账号</h1>
        <p class="subtitle">加入我们，开始记录美好时光</p>
      </div>

      <!-- 注册表单 -->
      <form @submit.prevent="handleRegister" class="register-form">
        <div class="form-group">
          <label for="username">用户名</label>
          <input
            id="username"
            v-model="formData.username"
            type="text"
            class="form-input"
            placeholder="请输入用户名（至少3个字符）"
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
              placeholder="请输入密码（至少6个字符）"
              autocomplete="new-password"
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

        <div class="form-group">
          <label for="confirmPassword">确认密码</label>
          <div class="password-input">
            <input
              id="confirmPassword"
              v-model="confirmPassword"
              :type="showConfirmPassword ? 'text' : 'password'"
              class="form-input"
              placeholder="请再次输入密码"
              autocomplete="new-password"
              :disabled="isSubmitting"
            />
            <button
              type="button"
              class="toggle-password"
              @click="showConfirmPassword = !showConfirmPassword"
              tabindex="-1"
            >
              {{ showConfirmPassword ? '隐藏' : '显示' }}
            </button>
          </div>
        </div>

        <button
          type="submit"
          class="register-btn"
          :disabled="isSubmitting"
        >
          <UserPlus :size="18" />
          <span>{{ isSubmitting ? '注册中...' : '注册' }}</span>
        </button>
      </form>

      <!-- 登录链接 -->
      <div class="login-link">
        已有账号？
        <button type="button" @click="goToLogin" class="link-btn">
          立即登录
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.register-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  background: linear-gradient(135deg, #fce4f4 0%, #ffe6ec 50%, #fff0f5 100%);
}

.register-card {
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

.register-header {
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

.register-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
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

.register-btn {
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

.register-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 12px 20px rgba(217, 117, 154, 0.3);
}

.register-btn:active:not(:disabled) {
  transform: translateY(0);
}

.register-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.login-link {
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
