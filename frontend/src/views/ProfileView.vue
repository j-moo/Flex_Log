<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { getProfile, getMyProfile, updateMyProfile } from '../api/profile'
import { getUserExpenses } from '../api/expenses'
import { useAccountStore } from '../stores/account'
import { formatDate, isVideo } from '../utils/format'


const route = useRoute()
const account = useAccountStore()
const profile = ref(null)
const logs = ref([])
const form = reactive({ name: '', nickname: '', bio: '' })
const imageFile = ref(null)
const imagePreview = ref('')
const isLoading = ref(true)
const isSubmitting = ref(false)
const errorMessage = ref('')
const successMessage = ref('')

const requestedUserId = computed(() => route.params.userId ? Number(route.params.userId) : account.user?.id)
const isOwnProfile = computed(() => requestedUserId.value === account.user?.id)

const applyProfile = (data) => {
  profile.value = data
  form.name = data.name || ''
  form.nickname = data.nickname || ''
  form.bio = data.bio || ''
  imagePreview.value = data.image || ''
  if (isOwnProfile.value) {
    account.user = {
      ...account.user,
      name: data.name || '',
      username: data.username,
      email: data.email,
    }
  }
}

const loadProfile = async () => {
  isLoading.value = true
  errorMessage.value = ''
  successMessage.value = ''
  try {
    const response = isOwnProfile.value
      ? await getMyProfile()
      : await getProfile(requestedUserId.value)
    applyProfile(response.data)

    const logsResponse = await getUserExpenses(response.data.user_id)
    logs.value = logsResponse.data
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
    const response = await updateMyProfile(payload)
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

watch(() => route.params.userId, loadProfile)
onMounted(loadProfile)
</script>

<template>
  <section>
    <div v-if="isLoading" class="alert alert-secondary">불러오는 중입니다.</div>
    <div v-else-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>

    <template v-else-if="profile">
      <div class="surface p-4 mb-4">
        <div class="d-flex flex-column flex-md-row gap-4">
          <div class="text-center">
            <img v-if="imagePreview" class="profile-image rounded-circle border" :src="imagePreview" alt="프로필 이미지">
            <div v-else class="profile-placeholder rounded-circle">
              {{ profile.username?.slice(0, 1).toUpperCase() }}
            </div>
          </div>

          <div class="flex-grow-1">
            <div class="d-flex flex-column flex-md-row justify-content-between gap-3 mb-3">
              <div>
                <h1 class="h3 mb-1">{{ profile.nickname }}</h1>
                <p class="text-secondary mb-0">@{{ profile.username }} · 친구 {{ profile.friend_count }}명</p>
              </div>
              <RouterLink class="btn btn-outline-secondary align-self-start" :to="{ name: 'friends' }">친구 보기</RouterLink>
            </div>
            <p v-if="profile.bio" class="content-preline mb-0">{{ profile.bio }}</p>
            <p v-else class="text-secondary mb-0">소개가 없습니다.</p>
          </div>
        </div>
      </div>

      <form v-if="isOwnProfile" class="surface p-4 mb-4" @submit.prevent="submit">
        <h2 class="h5 mb-3">프로필 수정</h2>
        <div class="row g-3">
          <div class="col-12 col-md-6">
            <label class="form-label">아이디</label>
            <input class="form-control" :value="profile.username" disabled>
          </div>
          <div class="col-12 col-md-6">
            <label class="form-label">이메일</label>
            <input class="form-control" :value="profile.email" disabled>
          </div>
          <div class="col-12 col-md-6">
            <label for="profile-name" class="form-label">이름</label>
            <input id="profile-name" v-model.trim="form.name" class="form-control" maxlength="50">
          </div>
          <div class="col-12 col-md-6">
            <label for="profile-nickname" class="form-label">닉네임</label>
            <input id="profile-nickname" v-model.trim="form.nickname" class="form-control" maxlength="30" required>
          </div>
          <div class="col-12">
            <label for="profile-bio" class="form-label">소개</label>
            <textarea id="profile-bio" v-model="form.bio" class="form-control" rows="3"></textarea>
          </div>
          <div class="col-12">
            <label for="profile-image" class="form-label">프로필 이미지</label>
            <input id="profile-image" class="form-control" type="file" accept="image/*" @change="selectImage">
          </div>
        </div>

        <button class="btn btn-primary mt-3" :disabled="isSubmitting">
          {{ isSubmitting ? '저장 중...' : '저장' }}
        </button>
        <div v-if="successMessage" class="alert alert-success mt-3 mb-0">{{ successMessage }}</div>
      </form>

      <div class="section-head">
        <div>
          <h1 class="h4">작성한 피드</h1>
          <p>최신 소비 기록 {{ logs.length }}개</p>
        </div>
      </div>
      <div v-if="logs.length" class="profile-grid">
        <RouterLink
          v-for="log in logs"
          :key="log.id"
          class="profile-grid-item"
          :to="isOwnProfile ? { name: 'log-edit', params: { id: log.id } } : { name: 'feed' }"
        >
          <video v-if="log.media && isVideo(log.media)" :src="log.media"></video>
          <img v-else-if="log.media" :src="log.media" alt="소비 피드 이미지">
          <div v-else class="grid-empty p-2">
            <span>{{ log.category_name }}</span>
            <small>{{ formatDate(log.created_at) }}</small>
          </div>
        </RouterLink>
      </div>
      <div v-else class="surface grid-empty">작성한 피드가 없습니다.</div>
    </template>
  </section>
</template>
