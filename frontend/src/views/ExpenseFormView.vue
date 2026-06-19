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
const previewUrl = ref('')
const isLoading = ref(true)
const isSubmitting = ref(false)
const errorMessage = ref('')
const form = reactive({
  category: '',
  amount: '',
  product_name: '',
  merchant: '',
  content: '',
  overlay_text: '',
  visibility: 'friends',
  hide_amount: false,
  is_visible: true,
})
const overlayStyle = reactive({
  fontSize: 28,
  color: '#ffffff',
  position: 'center',
})

const overlayPreviewStyle = computed(() => {
  const positions = {
    top: { top: '18%', left: '50%', transform: 'translate(-50%, -50%)' },
    center: { top: '50%', left: '50%', transform: 'translate(-50%, -50%)' },
    bottom: { top: '82%', left: '50%', transform: 'translate(-50%, -50%)' },
  }
  return {
    ...positions[overlayStyle.position],
    fontSize: `${overlayStyle.fontSize}px`,
    color: overlayStyle.color,
  }
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
      const data = logResponse.data
      form.category = String(data.category)
      form.amount = String(data.amount || '')
      form.product_name = data.product_name || ''
      form.merchant = data.merchant || ''
      form.content = data.content || ''
      form.overlay_text = data.overlay_text || ''
      form.visibility = data.visibility || 'friends'
      form.hide_amount = Boolean(data.hide_amount)
      form.is_visible = Boolean(data.is_visible)
      currentMedia.value = data.media || ''
      Object.assign(overlayStyle, data.overlay_style || {})
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
  const file = event.target.files?.[0] || null
  mediaFile.value = file
  previewUrl.value = file ? URL.createObjectURL(file) : ''
}

const submit = async () => {
  isSubmitting.value = true
  errorMessage.value = ''

  const payload = new FormData()
  payload.append('category', form.category)
  payload.append('amount', form.amount)
  payload.append('product_name', form.product_name)
  payload.append('merchant', form.merchant)
  payload.append('content', form.content)
  payload.append('overlay_text', form.overlay_text)
  payload.append('overlay_style', JSON.stringify(overlayStyle))
  payload.append('visibility', form.visibility)
  payload.append('hide_amount', String(form.hide_amount))
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
  <section class="surface">
    <div class="p-4">
      <h1 class="h4 mb-4">{{ isEdit ? '소비 로그 수정' : '소비 로그 작성' }}</h1>
      <div v-if="isLoading" class="alert alert-secondary">불러오는 중입니다.</div>
      <form v-else class="row g-4" @submit.prevent="submit">
        <div class="col-12 col-lg-5">
          <div class="media-editor">
            <img v-if="previewUrl || currentMedia" :src="previewUrl || currentMedia" alt="소비 이미지 미리보기">
            <div v-else class="media-placeholder">이미지 미리보기</div>
            <div v-if="form.overlay_text" class="overlay-text" :style="overlayPreviewStyle">
              {{ form.overlay_text }}
            </div>
          </div>

          <label for="log-media" class="form-label mt-3">사진 또는 영상</label>
          <input id="log-media" class="form-control" type="file" accept="image/*,video/mp4,video/webm" @change="selectMedia">
          <div class="form-text">JPG, PNG, GIF, WEBP, MP4, WEBM, 최대 10MB</div>
        </div>

        <div class="col-12 col-lg-7">
          <div class="row g-3">
            <div class="col-12 col-sm-6">
              <label for="log-category" class="form-label">카테고리</label>
              <select id="log-category" v-model="form.category" class="form-select" required>
                <option v-for="category in categories" :key="category.id" :value="String(category.id)">
                  {{ category.name }}
                </option>
              </select>
            </div>

            <div class="col-12 col-sm-6">
              <label for="log-amount" class="form-label">금액</label>
              <input id="log-amount" v-model="form.amount" class="form-control" type="number" min="1" step="1" required>
            </div>

            <div class="col-12 col-sm-6">
              <label for="product-name" class="form-label">상품명</label>
              <input id="product-name" v-model.trim="form.product_name" class="form-control" maxlength="100">
            </div>

            <div class="col-12 col-sm-6">
              <label for="merchant" class="form-label">소비처</label>
              <input id="merchant" v-model.trim="form.merchant" class="form-control" maxlength="100">
            </div>

            <div class="col-12">
              <label for="log-content" class="form-label">메모</label>
              <textarea id="log-content" v-model="form.content" class="form-control" rows="4"></textarea>
            </div>

            <div class="col-12">
              <label for="overlay-text" class="form-label">사진 안 텍스트</label>
              <input id="overlay-text" v-model.trim="form.overlay_text" class="form-control" maxlength="120">
            </div>

            <div class="col-12 col-sm-4">
              <label for="overlay-size" class="form-label">텍스트 크기</label>
              <input id="overlay-size" v-model.number="overlayStyle.fontSize" class="form-range" type="range" min="16" max="56">
            </div>

            <div class="col-6 col-sm-4">
              <label for="overlay-color" class="form-label">텍스트 색상</label>
              <input id="overlay-color" v-model="overlayStyle.color" class="form-control form-control-color" type="color">
            </div>

            <div class="col-6 col-sm-4">
              <label for="overlay-position" class="form-label">텍스트 위치</label>
              <select id="overlay-position" v-model="overlayStyle.position" class="form-select">
                <option value="top">상단</option>
                <option value="center">중앙</option>
                <option value="bottom">하단</option>
              </select>
            </div>

            <div class="col-12 col-sm-6">
              <label for="visibility" class="form-label">공개 범위</label>
              <select id="visibility" v-model="form.visibility" class="form-select">
                <option value="public">전체 공개</option>
                <option value="friends">친구 공개</option>
                <option value="private">나만 보기</option>
              </select>
            </div>

            <div class="col-12 col-sm-6 d-flex align-items-end">
              <div class="form-check mb-2">
                <input id="hide-amount" v-model="form.hide_amount" class="form-check-input" type="checkbox">
                <label class="form-check-label" for="hide-amount">피드에서 금액 숨김</label>
              </div>
            </div>

            <div class="col-12">
              <div class="form-check">
                <input id="log-visible" v-model="form.is_visible" class="form-check-input" type="checkbox">
                <label class="form-check-label" for="log-visible">피드에 표시</label>
              </div>
            </div>
          </div>

          <div class="d-flex gap-2 mt-4">
            <button class="btn btn-primary" :disabled="isSubmitting">
              {{ isSubmitting ? '저장 중...' : '저장' }}
            </button>
            <RouterLink class="btn btn-outline-secondary" :to="{ name: 'logs' }">취소</RouterLink>
          </div>
          <div v-if="errorMessage" class="alert alert-danger mt-3 mb-0">{{ errorMessage }}</div>
        </div>
      </form>
    </div>
  </section>
</template>

<style scoped>
.media-editor {
  position: relative;
  display: grid;
  min-height: 360px;
  place-items: center;
  overflow: hidden;
  border-radius: 8px;
  background: #202833;
}

.media-editor img {
  width: 100%;
  height: 100%;
  min-height: 360px;
  object-fit: cover;
}

.media-placeholder {
  color: #aab4c0;
  font-weight: 800;
}
</style>
