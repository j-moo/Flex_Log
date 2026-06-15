<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { useAccountStore } from '../stores/account'


const router = useRouter()
const account = useAccountStore()
const form = reactive({
  username: '',
  email: '',
  password: '',
  password_confirm: '',
})
const errors = ref({})
const generalError = ref('')
const isSubmitting = ref(false)

const toMessage = (value) => {
  if (Array.isArray(value)) return value.join(' ')
  return typeof value === 'string' ? value : '입력값을 확인해주세요.'
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
    await router.push({ name: 'home' })
  } catch (error) {
    const data = error.response?.data
    if (data && typeof data === 'object') {
      const fields = new Set(['username', 'email', 'password', 'password_confirm'])
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
  <section class="card">
    <h1>회원가입</h1>
    <form class="form" @submit.prevent="submit">
      <div class="field">
        <label for="username">아이디</label>
        <input id="username" v-model.trim="form.username" autocomplete="username" required :aria-invalid="Boolean(errors.username)">
        <p v-if="errors.username" class="field-error">{{ errors.username }}</p>
      </div>

      <div class="field">
        <label for="email">이메일</label>
        <input id="email" v-model.trim="form.email" type="email" autocomplete="email" required :aria-invalid="Boolean(errors.email)">
        <p v-if="errors.email" class="field-error">{{ errors.email }}</p>
      </div>

      <div class="field">
        <label for="password">비밀번호</label>
        <input id="password" v-model="form.password" type="password" autocomplete="new-password" required :aria-invalid="Boolean(errors.password)">
        <p class="help">8자 이상이며 흔하거나 숫자로만 된 비밀번호는 사용할 수 없습니다.</p>
        <p v-if="errors.password" class="field-error">{{ errors.password }}</p>
      </div>

      <div class="field">
        <label for="password-confirm">비밀번호 확인</label>
        <input id="password-confirm" v-model="form.password_confirm" type="password" autocomplete="new-password" required :aria-invalid="Boolean(errors.password_confirm)">
        <p v-if="errors.password_confirm" class="field-error">{{ errors.password_confirm }}</p>
      </div>

      <button class="button" :disabled="isSubmitting">
        {{ isSubmitting ? '가입 중...' : '회원가입' }}
      </button>
      <p v-if="generalError" class="error">{{ generalError }}</p>
    </form>
  </section>
</template>
