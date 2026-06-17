<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

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
    await router.push({ name: 'home' })
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
  <section class="auth-card card">
    <div class="card-body p-4">
      <h1 class="h4 mb-4">회원가입</h1>
      <form class="d-grid gap-3" @submit.prevent="submit">
        <div>
          <label for="username" class="form-label">아이디</label>
          <input id="username" v-model.trim="form.username" class="form-control" autocomplete="username" required>
          <div v-if="errors.username" class="invalid-feedback d-block">{{ errors.username }}</div>
        </div>

        <div>
          <label for="name" class="form-label">이름</label>
          <input id="name" v-model.trim="form.name" class="form-control" maxlength="50">
          <div v-if="errors.name" class="invalid-feedback d-block">{{ errors.name }}</div>
        </div>

        <div>
          <label for="email" class="form-label">이메일</label>
          <input id="email" v-model.trim="form.email" class="form-control" type="email" autocomplete="email" required>
          <div v-if="errors.email" class="invalid-feedback d-block">{{ errors.email }}</div>
        </div>

        <div>
          <label for="password" class="form-label">비밀번호</label>
          <input id="password" v-model="form.password" class="form-control" type="password" autocomplete="new-password" required>
          <div class="form-text">8자 이상, 너무 흔하거나 숫자로만 된 비밀번호는 사용할 수 없습니다.</div>
          <div v-if="errors.password" class="invalid-feedback d-block">{{ errors.password }}</div>
        </div>

        <div>
          <label for="password-confirm" class="form-label">비밀번호 확인</label>
          <input id="password-confirm" v-model="form.password_confirm" class="form-control" type="password" autocomplete="new-password" required>
          <div v-if="errors.password_confirm" class="invalid-feedback d-block">{{ errors.password_confirm }}</div>
        </div>

        <button class="btn btn-primary" :disabled="isSubmitting">
          {{ isSubmitting ? '가입 중...' : '회원가입' }}
        </button>
        <div v-if="generalError" class="alert alert-danger mb-0">{{ generalError }}</div>
      </form>
    </div>
  </section>
</template>
