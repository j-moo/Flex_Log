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
    errorMessage.value = '로그 정보를 불러오지 못했습니다.'
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
  <section class="card auth-card">
    <div class="card-body p-4">
      <h1 class="h4 mb-4">{{ isEdit ? '소비 로그 수정' : '소비 로그 작성' }}</h1>
      <div v-if="isLoading" class="alert alert-secondary">불러오는 중입니다.</div>
      <form v-else class="d-grid gap-3" @submit.prevent="submit">
        <div>
          <label for="log-category" class="form-label">카테고리</label>
          <select id="log-category" v-model="form.category" class="form-select" required>
            <option v-for="category in categories" :key="category.id" :value="String(category.id)">
              {{ category.name }}
            </option>
          </select>
        </div>

        <div>
          <label for="log-amount" class="form-label">금액</label>
          <input id="log-amount" v-model="form.amount" class="form-control" type="number" min="1" step="1" required>
        </div>

        <div>
          <label for="log-content" class="form-label">내용</label>
          <textarea id="log-content" v-model="form.content" class="form-control" rows="5"></textarea>
        </div>

        <div>
          <label for="log-media" class="form-label">사진 또는 영상</label>
          <input id="log-media" class="form-control" type="file" accept="image/*,video/mp4,video/webm" @change="selectMedia">
          <a v-if="currentMedia" class="d-inline-block small mt-2" :href="currentMedia" target="_blank" rel="noreferrer">현재 미디어 보기</a>
          <div class="form-text">JPG, PNG, GIF, WEBP, MP4, WEBM, 최대 10MB</div>
        </div>

        <div class="form-check">
          <input id="log-visible" v-model="form.is_visible" class="form-check-input" type="checkbox">
          <label class="form-check-label" for="log-visible">친구 피드에 공개</label>
        </div>

        <div class="d-flex gap-2">
          <button class="btn btn-primary" :disabled="isSubmitting">
            {{ isSubmitting ? '저장 중...' : '저장' }}
          </button>
          <RouterLink class="btn btn-outline-secondary" :to="{ name: 'logs' }">취소</RouterLink>
        </div>
        <div v-if="errorMessage" class="alert alert-danger mb-0">{{ errorMessage }}</div>
      </form>
    </div>
  </section>
</template>
