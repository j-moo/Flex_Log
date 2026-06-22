<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import BrandLogo from '../components/common/BrandLogo.vue'
import { useAccountStore } from '../stores/account'

const router = useRouter()
const account = useAccountStore()
const form = reactive({ username: '', password: '' })
const errorMessage = ref('')
const isSubmitting = ref(false)

const submit = async () => {
  errorMessage.value = ''
  isSubmitting.value = true
  try {
    await account.login({ ...form })
    await router.push({ name: 'feed' })
  } catch {
    errorMessage.value = '아이디 또는 비밀번호를 확인해 주세요.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <section class="auth-page">
    <form class="auth-card vintage-card" @submit.prevent="submit">
      <BrandLogo :variant="6" size="medium" />
      <div>
        <p class="auth-kicker">Welcome Back</p>
        <h1 class="display-title">로그인</h1>
        <p>내 소비 피드와 금융 대시보드로 돌아가세요.</p>
      </div>

      <label>
        아이디
        <input v-model.trim="form.username" class="form-control" autocomplete="username" required>
      </label>

      <label>
        비밀번호
        <input
          v-model="form.password"
          class="form-control"
          type="password"
          autocomplete="current-password"
          required
        >
      </label>

      <button class="vintage-button auth-submit" :disabled="isSubmitting">
        {{ isSubmitting ? '로그인 중...' : '로그인' }}
      </button>

      <p v-if="errorMessage" class="auth-error">{{ errorMessage }}</p>
      <p class="auth-link">계정이 없다면 <RouterLink :to="{ name: 'signup' }">회원가입</RouterLink></p>
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
  gap: 16px;
  width: min(100%, 430px);
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

p {
  margin: 0;
  color: var(--color-muted);
}

label {
  display: grid;
  gap: 7px;
  color: var(--color-muted);
  font-weight: 900;
}

.auth-submit {
  min-height: 48px;
}

.auth-error {
  border-radius: 14px;
  background: rgba(182, 74, 53, 0.12);
  color: var(--color-red);
  padding: 10px 12px;
}

.auth-link a {
  color: var(--color-ink);
  font-weight: 900;
  text-decoration: underline;
}
</style>
