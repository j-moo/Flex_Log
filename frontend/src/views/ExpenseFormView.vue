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
const mediaEditor = ref(null)
const isDraggingOverlay = ref(false)
const isLoading = ref(true)
const isSubmitting = ref(false)
const errorMessage = ref('')
const form = reactive({
  title: '',
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
  x: 50,
  y: 50,
})

const overlayPreviewStyle = computed(() => {
  return {
    top: `${overlayStyle.y}%`,
    left: `${overlayStyle.x}%`,
    transform: 'translate(-50%, -50%)',
    fontSize: `${overlayStyle.fontSize}px`,
    color: overlayStyle.color,
  }
})
const previewOverlayText = computed(() => [
  form.overlay_text.trim(),
  form.amount ? `${Number(form.amount).toLocaleString('ko-KR')}원` : '',
].filter(Boolean))

const updateOverlayPosition = (event) => {
  if (!isDraggingOverlay.value || !mediaEditor.value) return
  const rect = mediaEditor.value.getBoundingClientRect()
  overlayStyle.x = Math.round(Math.min(96, Math.max(4, ((event.clientX - rect.left) / rect.width) * 100)))
  overlayStyle.y = Math.round(Math.min(94, Math.max(6, ((event.clientY - rect.top) / rect.height) * 100)))
}
const startOverlayDrag = (event) => {
  isDraggingOverlay.value = true
  event.currentTarget.setPointerCapture?.(event.pointerId)
  updateOverlayPosition(event)
}
const stopOverlayDrag = () => { isDraggingOverlay.value = false }

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
      form.title = data.title || ''
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
      if (!Number.isFinite(Number(overlayStyle.x))) overlayStyle.x = 50
      if (!Number.isFinite(Number(overlayStyle.y))) overlayStyle.y = 50
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
  payload.append('title', form.overlay_text.trim() || `${categories.value.find(item => String(item.id) === String(form.category))?.name || '소비'} 기록`)
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
  <section class="surface create-card">
    <div class="create-inner">
      <div class="create-title"><span>NEW POST</span><h1>{{ isEdit ? '소비기록 수정' : '새 소비기록' }}</h1><p>오늘의 소비 순간을 친구들과 공유해보세요.</p></div>
      <div v-if="isLoading" class="alert alert-secondary">불러오는 중입니다.</div>
      <form v-else class="row g-4" @submit.prevent="submit">
        <div class="col-12 col-lg-5">
          <div ref="mediaEditor" class="media-editor">
            <img v-if="previewUrl || currentMedia" :src="previewUrl || currentMedia" alt="소비 이미지 미리보기">
            <div v-else class="media-placeholder">이미지 미리보기</div>
            <div
              v-if="previewOverlayText.length"
              class="overlay-text draggable-overlay"
              :class="{ dragging: isDraggingOverlay }"
              :style="overlayPreviewStyle"
              @pointerdown.stop.prevent="startOverlayDrag"
              @pointermove.stop.prevent="updateOverlayPosition"
              @pointerup="stopOverlayDrag"
              @pointercancel="stopOverlayDrag"
            >
              <span v-for="line in previewOverlayText" :key="line">{{ line }}</span>
            </div>
          </div>
          <p class="drag-guide">텍스트를 드래그해 위치를 조절하세요. 좌표 {{ overlayStyle.x }}, {{ overlayStyle.y }}</p>

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

            <div class="col-12">
              <label for="overlay-text" class="form-label">이미지 안에 넣을 텍스트</label>
              <input id="overlay-text" v-model.trim="form.overlay_text" class="form-control" maxlength="120" placeholder="예: 오늘의 행복한 소비">
            </div>

            <div class="col-12 col-sm-4">
              <label for="overlay-size" class="form-label">텍스트 크기</label>
              <input id="overlay-size" v-model.number="overlayStyle.fontSize" class="form-range" type="range" min="16" max="56">
            </div>

            <div class="col-6 col-sm-4">
              <label for="overlay-color" class="form-label">텍스트 색상</label>
              <input id="overlay-color" v-model="overlayStyle.color" class="form-control form-control-color" type="color">
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

          <div class="submit-actions">
            <button class="submit-button" :disabled="isSubmitting">
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
.create-card{width:min(100%,900px);margin:auto;overflow:hidden}.create-inner{padding:20px}.create-title{margin-bottom:22px}.create-title>span{color:var(--accent);font-size:10px;font-weight:850;letter-spacing:.14em}.create-title h1{margin:4px 0;font-size:23px}.create-title p{margin:0;color:var(--muted);font-size:12px}.submit-actions{display:flex;gap:8px;margin-top:24px}.submit-button{border:0;border-radius:9px;background:var(--accent);color:white;padding:10px 20px;font-weight:800}
.media-editor {
  position: relative;
  display: grid;
  min-height: 360px;
  place-items: center;
  overflow: hidden;
  border-radius: 12px;
  background: #eef1f5;
}

.media-editor img {
  width: 100%;
  height: 100%;
  min-height: 360px;
  object-fit: cover;
}

.media-placeholder {
  color: var(--muted);
  font-weight: 800;
}
.draggable-overlay{display:grid;gap:3px;cursor:grab;touch-action:none;user-select:none}.draggable-overlay.dragging{cursor:grabbing}.draggable-overlay span:last-child{font-size:.7em}.drag-guide{margin:8px 0 0;color:var(--muted);font-size:10px;text-align:center}
@media(max-width:600px){.create-inner{padding:14px}.media-editor,.media-editor img{min-height:280px}.submit-actions{display:grid}.submit-button{width:100%}}
</style>
