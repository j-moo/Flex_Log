<script setup>
import { onMounted, reactive, ref } from 'vue'

import api from '../api/client'
import { useAccountStore } from '../stores/account'


const account = useAccountStore()
const profile = ref(null)
const form = reactive({ name: '', nickname: '', bio: '' })
const imageFile = ref(null)
const imagePreview = ref('')
const isLoading = ref(true)
const isSubmitting = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const applyProfile = (data) => {
  profile.value = data
  form.name = data.name || ''
  form.nickname = data.nickname || ''
  form.bio = data.bio || ''
  imagePreview.value = data.image || ''
  account.user = {
    ...account.user,
    name: data.name || '',
    username: data.username,
    email: data.email,
  }
}

const loadProfile = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const response = await api.get('/api/v1/profiles/me/')
    applyProfile(response.data)
  } catch {
    errorMessage.value = '프로필을 불러오지 못했습니다.'
  } finally {
    isLoading.value = false
  }
}

const selectImage = (event) => {
  const file = event.target.files?.[0] || null
  imageFile.value = file
  if (file) imagePreview.value = URL.createObjectURL(file)
}

const submit = async () => {
  isSubmitting.value = true
  errorMessage.value = ''
  successMessage.value = ''

  const payload = new FormData()
  payload.append('name', form.name)
  payload.append('nickname', form.nickname)
  payload.append('bio', form.bio)
  if (imageFile.value) payload.append('image', imageFile.value)

  try {
    const response = await api.patch('/api/v1/profiles/me/', payload)
    applyProfile(response.data)
    imageFile.value = null
    successMessage.value = '프로필을 저장했습니다.'
  } catch (error) {
    const data = error.response?.data
    errorMessage.value = data
      ? Object.values(data).flat().join(' ')
      : '프로필 저장 중 오류가 발생했습니다.'
  } finally {
    isSubmitting.value = false
  }
}

onMounted(loadProfile)
</script>

<template>
  <section class="card auth-card">
    <div class="card-body p-4">
      <h1 class="h4 mb-4">프로필</h1>
      <div v-if="isLoading" class="alert alert-secondary">불러오는 중입니다.</div>
      <form v-else class="d-grid gap-3" @submit.prevent="submit">
        <div class="d-flex justify-content-center">
          <img v-if="imagePreview" class="profile-image rounded-circle border" :src="imagePreview" alt="프로필 이미지">
          <div v-else class="profile-placeholder rounded-circle">
            {{ profile?.username?.slice(0, 1).toUpperCase() }}
          </div>
        </div>

        <div>
          <label class="form-label">아이디</label>
          <input class="form-control" :value="profile?.username" disabled>
        </div>

        <div>
          <label class="form-label">이메일</label>
          <input class="form-control" :value="profile?.email" disabled>
        </div>

        <div>
          <label for="profile-name" class="form-label">이름</label>
          <input id="profile-name" v-model.trim="form.name" class="form-control" maxlength="50">
        </div>

        <div>
          <label for="profile-nickname" class="form-label">닉네임</label>
          <input id="profile-nickname" v-model.trim="form.nickname" class="form-control" maxlength="30" required>
        </div>

        <div>
          <label for="profile-bio" class="form-label">소개</label>
          <textarea id="profile-bio" v-model="form.bio" class="form-control" rows="4"></textarea>
        </div>

        <div>
          <label for="profile-image" class="form-label">프로필 이미지</label>
          <input id="profile-image" class="form-control" type="file" accept="image/*" @change="selectImage">
        </div>

        <button class="btn btn-primary" :disabled="isSubmitting">
          {{ isSubmitting ? '저장 중...' : '저장' }}
        </button>
        <div v-if="errorMessage" class="alert alert-danger mb-0">{{ errorMessage }}</div>
        <div v-if="successMessage" class="alert alert-success mb-0">{{ successMessage }}</div>
      </form>
    </div>
  </section>
</template>
