<script setup>
import { onMounted, reactive, ref } from 'vue'

import api from '../api/client'


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
  <section class="card">
    <h1>프로필</h1>
    <p v-if="isLoading" class="help">불러오는 중...</p>
    <form v-else class="form" @submit.prevent="submit">
      <div class="profile-image-wrap">
        <img v-if="imagePreview" class="profile-image" :src="imagePreview" alt="프로필 이미지">
        <div v-else class="profile-placeholder">{{ profile?.username?.slice(0, 1).toUpperCase() }}</div>
      </div>

      <div class="field">
        <label>아이디</label>
        <input :value="profile?.username" disabled>
      </div>

      <div class="field">
        <label>이메일</label>
        <input :value="profile?.email" disabled>
      </div>

      <div class="field">
        <label for="profile-name">이름</label>
        <input id="profile-name" v-model.trim="form.name" maxlength="50">
      </div>

      <div class="field">
        <label for="profile-nickname">닉네임</label>
        <input id="profile-nickname" v-model.trim="form.nickname" maxlength="30" required>
      </div>

      <div class="field">
        <label for="profile-bio">소개</label>
        <textarea id="profile-bio" v-model="form.bio" rows="4"></textarea>
      </div>

      <div class="field">
        <label for="profile-image">프로필 이미지</label>
        <input id="profile-image" type="file" accept="image/*" @change="selectImage">
      </div>

      <button class="button" :disabled="isSubmitting">
        {{ isSubmitting ? '저장 중...' : '프로필 저장' }}
      </button>
      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
      <p v-if="successMessage" class="success">{{ successMessage }}</p>
    </form>
  </section>
</template>
