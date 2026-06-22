<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import BrandLogo from '../components/common/BrandLogo.vue'
import { useAccountStore } from '../stores/account'

const router = useRouter()
const account = useAccountStore()
const form = reactive({
  username: '',
  name: '',
  email: '',
  password: '',
  password_confirm: '',
})
const errors = ref({})
const generalError = ref('')
const isSubmitting = ref(false)

const toMessage = (value) => {
  if (Array.isArray(value)) return value.join(' ')
  return typeof value === 'string' ? value : '입력값을 확인해 주세요.'
}

const submit = async () => {
  errors.value = {}
  generalError.value = ''

  if (form.password !== form.password_confirm) {
    errors.value = { password_confirm: '비밀번호가 일치하지 않습니다.' }
    return
  }

  isSubmitting.value = true
  try {
    await account.signup({ ...form })
    await router.push({ name: 'feed' })
  } catch (error) {
    const data = error.response?.data
    if (data && typeof data === 'object') {
      const fields = new Set(['username', 'name', 'email', 'password', 'password_confirm'])
      const fieldErrors = {}
      const otherErrors = []

      Object.entries(data).forEach(([field, value]) => {
        const message = toMessage(value)
        if (fields.has(field)) fieldErrors[field] = message
        else otherErrors.push(message)
      })
      errors.value = fieldErrors
      generalError.value = otherErrors.join(' ')
    } else {
      generalError.value = '회원가입 중 오류가 발생했습니다.'
    }
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <section class="auth-page">
    <form class="auth-card vintage-card" @submit.prevent="submit">
      <BrandLogo :variant="1" size="medium" />
      <div>
        <p class="auth-kicker">Join Flex-Log</p>
        <h1 class="display-title">회원가입</h1>
        <p>소비 기록을 피드로 남기고, 금융 인사이트까지 이어가세요.</p>
      </div>

      <label>
        아이디
        <input v-model.trim="form.username" class="form-control" autocomplete="username" required>
        <span v-if="errors.username">{{ errors.username }}</span>
      </label>

      <label>
        이름
        <input v-model.trim="form.name" class="form-control" maxlength="50">
        <span v-if="errors.name">{{ errors.name }}</span>
      </label>

      <label>
        이메일
        <input v-model.trim="form.email" class="form-control" type="email" autocomplete="email" required>
        <span v-if="errors.email">{{ errors.email }}</span>
      </label>

      <label>
        비밀번호
        <input v-model="form.password" class="form-control" type="password" autocomplete="new-password" required>
        <small>8자 이상, 너무 흔하거나 숫자만으로 된 비밀번호는 사용할 수 없습니다.</small>
        <span v-if="errors.password">{{ errors.password }}</span>
      </label>

      <label>
        비밀번호 확인
        <input
          v-model="form.password_confirm"
          class="form-control"
          type="password"
          autocomplete="new-password"
          required
        >
        <span v-if="errors.password_confirm">{{ errors.password_confirm }}</span>
      </label>

      <button class="vintage-button auth-submit" :disabled="isSubmitting">
        {{ isSubmitting ? '가입 중...' : '회원가입' }}
      </button>

      <p v-if="generalError" class="auth-error">{{ generalError }}</p>
      <p class="auth-link">이미 계정이 있다면 <RouterLink :to="{ name: 'login' }">로그인</RouterLink></p>
    </form>
  </section>
</template>

<style scoped>
.auth-page {
  display: grid;
  min-height: 100vh;
  place-items: center;
  padding: 32px 18px;
}

.auth-card {
  display: grid;
  gap: 14px;
  width: min(100%, 470px);
  padding: 28px;
}

.auth-kicker {
  margin: 8px 0 0;
  color: var(--color-dark-gold);
  font-weight: 900;
  letter-spacing: 0.06em;
  text-transform: uppercase;
}

h1 {
  margin: 2px 0;
  font-size: 42px;
}

p,
small {
  margin: 0;
  color: var(--color-muted);
}

label {
  display: grid;
  gap: 7px;
  color: var(--color-muted);
  font-weight: 900;
}

label span,
.auth-error {
  color: var(--color-red);
  font-size: 13px;
}

.auth-submit {
  min-height: 48px;
}

.auth-link a {
  color: var(--color-ink);
  font-weight: 900;
  text-decoration: underline;
}
</style>
