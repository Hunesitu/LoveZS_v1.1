<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { Heart, UserPlus } from 'lucide-vue-next'
import { useUserStore } from '@/stores/user'
import { useUiStore } from '@/stores/ui'
import { register } from '@/api/auth'
import type { RegisterRequest } from '@/types'

const router = useRouter()
const userStore = useUserStore()
const uiStore = useUiStore()

const formData = ref<RegisterRequest>({ username: '', password: '' })
const confirmPassword = ref('')
const isSubmitting = ref(false)
const showPassword = ref(false)
const showConfirmPassword = ref(false)

const validateForm = () => {
  if (!formData.value.username.trim()) {
    uiStore.showToast('请输入用户名', 'error')
    return false
  }
  if (formData.value.username.length < 3) {
    uiStore.showToast('用户名至少需要 3 个字符', 'error')
    return false
  }
  if (!formData.value.password) {
    uiStore.showToast('请输入密码', 'error')
    return false
  }
  if (formData.value.password.length < 6) {
    uiStore.showToast('密码至少需要 6 个字符', 'error')
    return false
  }
  if (formData.value.password !== confirmPassword.value) {
    uiStore.showToast('两次密码不一致', 'error')
    return false
  }
  return true
}

const handleRegister = async () => {
  if (!validateForm()) return

  isSubmitting.value = true
  try {
    const response = await register(formData.value)
    if (response.success && response.data) {
      userStore.login(response.data.token, response.data.user)
      uiStore.showToast('注册成功', 'success')
      router.push('/')
    }
  } catch (error: any) {
    console.error('Register error:', error)
    const data = error.response?.data
    uiStore.showToast(
      data?.errors?.username?.[0] || data?.errors?.password?.[0] || data?.message || '注册失败',
      'error'
    )
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <main class="auth-page">
    <section class="auth-card">
      <div class="auth-header">
        <span class="brand-mark"><Heart :size="20" fill="currentColor" /></span>
        <div class="logo">LoveZs</div>
        <p class="romance-kicker">First Scene</p>
        <h1>创建账号</h1>
        <p>创建一间私人的放映厅，开始收藏你们的美好时光。</p>
      </div>

      <form class="auth-form" @submit.prevent="handleRegister">
        <div class="form-group">
          <label class="form-label" for="username">用户名</label>
          <input id="username" v-model="formData.username" type="text" class="form-input" placeholder="至少 3 个字符" autocomplete="username" :disabled="isSubmitting" />
        </div>

        <div class="form-group">
          <label class="form-label" for="password">密码</label>
          <div class="password-input">
            <input id="password" v-model="formData.password" :type="showPassword ? 'text' : 'password'" class="form-input" placeholder="至少 6 个字符" autocomplete="new-password" :disabled="isSubmitting" />
            <button type="button" class="toggle-password" tabindex="-1" @click="showPassword = !showPassword">
              {{ showPassword ? '隐藏' : '显示' }}
            </button>
          </div>
        </div>

        <div class="form-group">
          <label class="form-label" for="confirmPassword">确认密码</label>
          <div class="password-input">
            <input id="confirmPassword" v-model="confirmPassword" :type="showConfirmPassword ? 'text' : 'password'" class="form-input" placeholder="请再次输入密码" autocomplete="new-password" :disabled="isSubmitting" />
            <button type="button" class="toggle-password" tabindex="-1" @click="showConfirmPassword = !showConfirmPassword">
              {{ showConfirmPassword ? '隐藏' : '显示' }}
            </button>
          </div>
        </div>

        <button type="submit" class="btn-primary auth-submit" :disabled="isSubmitting">
          <UserPlus :size="18" />
          {{ isSubmitting ? '注册中...' : '注册' }}
        </button>
      </form>

      <p class="auth-link">
        已有账号？
        <button type="button" @click="router.push('/login')">立即登录</button>
      </p>
    </section>
  </main>
</template>

<style scoped>
.auth-page {
  position: relative;
  display: grid;
  min-height: 100vh;
  place-items: center;
  padding: 1.5rem;
  overflow: hidden;
}

.auth-page::before {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 22% 18%, rgba(255, 154, 200, 0.18), transparent 26%),
    radial-gradient(circle at 80% 24%, rgba(245, 200, 143, 0.12), transparent 28%),
    linear-gradient(135deg, rgba(5, 5, 11, 0.2), rgba(42, 18, 42, 0.28));
  animation: filmDrift 9s ease-in-out infinite alternate;
}

.auth-card {
  position: relative;
  width: min(100%, 420px);
  padding: 2.4rem;
  border: 1px solid rgba(245, 200, 143, 0.16);
  border-radius: var(--radius-xl);
  background:
    linear-gradient(135deg, rgba(28, 18, 38, 0.92), rgba(7, 7, 13, 0.92)),
    radial-gradient(circle at 50% 0%, rgba(245, 200, 143, 0.15), transparent 42%);
  box-shadow: var(--shadow-lg), var(--shadow-glow);
  backdrop-filter: blur(20px);
  animation: revealIn 520ms ease both;
}

.auth-header {
  margin-bottom: 2rem;
  text-align: center;
}

.brand-mark {
  display: inline-grid;
  width: 42px;
  height: 42px;
  margin-bottom: 0.8rem;
  place-items: center;
  border-radius: 50%;
  color: #fff;
  background: radial-gradient(circle at 36% 30%, #ffe2ef 0 20%, #ff7cb7 45%, #ee4fa1 100%);
  box-shadow: var(--shadow-glow);
}

.logo {
  color: #fff;
  font-size: 1.35rem;
  font-weight: 900;
}

.auth-header h1 {
  margin: 0.75rem 0 0.45rem;
  color: var(--ink);
  font-family: var(--font-serif);
  font-size: 1.7rem;
}

.auth-header .romance-kicker {
  justify-content: center;
  margin-top: 0.8rem;
}

.auth-header p,
.auth-link {
  margin: 0;
  color: var(--ink-soft);
}

.auth-form {
  display: grid;
  gap: 1rem;
}

.password-input {
  position: relative;
}

.password-input .form-input {
  padding-right: 4rem;
}

.toggle-password {
  position: absolute;
  top: 50%;
  right: 0.65rem;
  padding: 0.25rem 0.45rem;
  border: 0;
  color: var(--rose-bright);
  background: transparent;
  font-size: 0.75rem;
  font-weight: 800;
  transform: translateY(-50%);
}

.auth-submit {
  width: 100%;
  margin-top: 0.45rem;
}

.auth-link {
  margin-top: 1.5rem;
  text-align: center;
  font-size: 0.875rem;
}

.auth-link button {
  border: 0;
  color: var(--rose-bright);
  background: transparent;
  font-weight: 800;
}
</style>
