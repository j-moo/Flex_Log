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
    errorMessage.value = '아이디 또는 비밀번호를 확인해주세요.'
  } finally {
    isSubmitting.value = false
  }
}
</script>

<template>
  <section class="card">
    <h1>로그인</h1>
    <form class="form" @submit.prevent="submit">
      <div class="field">
        <label for="login-username">아이디</label>
        <input id="login-username" v-model.trim="form.username" autocomplete="username" required>
      </div>

      <div class="field">
        <label for="login-password">비밀번호</label>
        <input id="login-password" v-model="form.password" type="password" autocomplete="current-password" required>
      </div>

      <button class="button" :disabled="isSubmitting">
        {{ isSubmitting ? '로그인 중...' : '로그인' }}
      </button>
      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
    </form>
  </section>
</template>
