<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

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
    await router.push({ name: 'home' })
  } catch {
    errorMessage.value = '아이디 또는 비밀번호를 확인해 주세요.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <section class="auth-card card">
    <div class="card-body p-4">
      <h1 class="h4 mb-4">로그인</h1>
      <form class="d-grid gap-3" @submit.prevent="submit">
        <div>
          <label for="login-username" class="form-label">아이디</label>
          <input id="login-username" v-model.trim="form.username" class="form-control" autocomplete="username" required>
        </div>

        <div>
          <label for="login-password" class="form-label">비밀번호</label>
          <input id="login-password" v-model="form.password" class="form-control" type="password" autocomplete="current-password" required>
        </div>

        <button class="btn btn-primary" :disabled="isSubmitting">
          {{ isSubmitting ? '로그인 중...' : '로그인' }}
        </button>
        <div v-if="errorMessage" class="alert alert-danger mb-0">{{ errorMessage }}</div>
      </form>
    </div>
  </section>
</template>
