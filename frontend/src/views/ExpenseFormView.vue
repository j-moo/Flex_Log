<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import api from '../api/client'


const route = useRoute()
const router = useRouter()
const isEdit = computed(() => Boolean(route.params.id))
const categories = ref([])
const mediaFile = ref(null)
const currentMedia = ref('')
const isLoading = ref(true)
const isSubmitting = ref(false)
const errorMessage = ref('')
const form = reactive({
  category: '',
  amount: '',
  content: '',
  is_visible: true,
})

const loadData = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const requests = [api.get('/api/v1/expenses/categories/')]
    if (isEdit.value) requests.push(api.get(`/api/v1/expenses/${route.params.id}/`))
    const [categoryResponse, logResponse] = await Promise.all(requests)
    categories.value = categoryResponse.data

    if (logResponse) {
      form.category = String(logResponse.data.category)
      form.amount = String(logResponse.data.amount)
      form.content = logResponse.data.content || ''
      form.is_visible = logResponse.data.is_visible
      currentMedia.value = logResponse.data.media || ''
    } else if (categories.value.length) {
      form.category = String(categories.value[0].id)
    }
  } catch {
    errorMessage.value = '로그 작성 정보를 불러오지 못했습니다.'
  } finally {
    isLoading.value = false
  }
}

const selectMedia = (event) => {
  mediaFile.value = event.target.files?.[0] || null
}

const submit = async () => {
  isSubmitting.value = true
  errorMessage.value = ''

  const payload = new FormData()
  payload.append('category', form.category)
  payload.append('amount', form.amount)
  payload.append('content', form.content)
  payload.append('is_visible', String(form.is_visible))
  if (mediaFile.value) payload.append('media', mediaFile.value)

  try {
    if (isEdit.value) {
      await api.patch(`/api/v1/expenses/${route.params.id}/`, payload)
    } else {
      await api.post('/api/v1/expenses/', payload)
    }
    await router.push({ name: 'logs' })
  } catch (error) {
    const data = error.response?.data
    errorMessage.value = data
      ? Object.values(data).flat().join(' ')
      : '소비 로그 저장 중 오류가 발생했습니다.'
  } finally {
    isSubmitting.value = false
  }
}

onMounted(loadData)
</script>

<template>
  <section class="card">
    <h1>{{ isEdit ? '소비 로그 수정' : '소비 로그 작성' }}</h1>
    <p v-if="isLoading" class="help">불러오는 중...</p>
    <form v-else class="form" @submit.prevent="submit">
      <div class="field">
        <label for="log-category">카테고리</label>
        <select id="log-category" v-model="form.category" required>
          <option v-for="category in categories" :key="category.id" :value="String(category.id)">
            {{ category.name }}
          </option>
        </select>
      </div>

      <div class="field">
        <label for="log-amount">금액</label>
        <input id="log-amount" v-model="form.amount" type="number" min="1" step="1" required>
      </div>

      <div class="field">
        <label for="log-content">내용</label>
        <textarea id="log-content" v-model="form.content" rows="5" placeholder="어디에, 왜 소비했는지 기록해보세요."></textarea>
      </div>

      <div class="field">
        <label for="log-media">사진 또는 영상</label>
        <input id="log-media" type="file" accept="image/*,video/mp4,video/webm" @change="selectMedia">
        <a v-if="currentMedia" class="media-link" :href="currentMedia" target="_blank" rel="noreferrer">현재 미디어 보기</a>
        <p class="help">JPG, PNG, GIF, WEBP, MP4, WEBM 형식, 최대 10MB</p>
      </div>

      <label class="checkbox-field">
        <input v-model="form.is_visible" type="checkbox">
        친구 피드에 공개
      </label>

      <div class="row-actions">
        <button class="button" :disabled="isSubmitting">
          {{ isSubmitting ? '저장 중...' : '저장' }}
        </button>
        <RouterLink class="button secondary" :to="{ name: 'logs' }">취소</RouterLink>
      </div>
      <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
    </form>
  </section>
</template>
