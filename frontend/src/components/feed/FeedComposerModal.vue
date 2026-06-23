<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'

import { createExpense, getCategories, getExpense, updateExpense } from '../../api/expenses'
import { isVideo } from '../../utils/format'

const props = defineProps({
  editId: {
    type: [String, Number, null],
    default: null,
  },
})

const emit = defineEmits(['close', 'saved'])

const categories = ref([])
const mediaFile = ref(null)
const currentMedia = ref('')
const previewUrl = ref('')
const fileInput = ref(null)
const mediaEditor = ref(null)
const isLoading = ref(true)
const isSubmitting = ref(false)
const errorMessage = ref('')
const step = ref('upload')
const activeOverlayId = ref(1)
const dragOverlayId = ref(null)

const form = reactive({
  category: '',
  amount: '',
  product_name: '',
  merchant: '',
  content: '',
  visibility: 'friends',
  hide_amount: false,
  is_visible: true,
})

const overlayBoxes = ref([])

const isEdit = computed(() => Boolean(props.editId))
const activeOverlay = computed(() =>
  overlayBoxes.value.find((box) => box.id === activeOverlayId.value) || overlayBoxes.value[0] || null,
)
const hasMedia = computed(() => Boolean(previewUrl.value || currentMedia.value))
const previewMedia = computed(() => previewUrl.value || currentMedia.value)
const previewIsVideo = computed(() => mediaFile.value?.type?.startsWith('video/') || isVideo(previewMedia.value))

const normalizedOverlayText = computed(() =>
  overlayBoxes.value
    .map((box) => box.text.trim())
    .filter(Boolean)
    .join(' / ')
    .slice(0, 120),
)

const buildTitle = (content, selectedCategory) => {
  const firstLine = content
    .split(/\r?\n/)
    .map((line) => line.trim())
    .find(Boolean)
  return (firstLine || normalizedOverlayText.value || `${selectedCategory?.name || '소비'} 기록`).slice(0, 150)
}

const overlayStyle = (box) => ({
  left: `${box.x}%`,
  top: `${box.y}%`,
  color: box.color,
  fontSize: `${box.fontSize}px`,
  transform: `translate(-50%, -50%) rotate(${Number(box.rotate || 0)}deg)`,
})

const openFileDialog = () => {
  fileInput.value?.click()
}

const setFile = (file) => {
  if (!file) return
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
  mediaFile.value = file
  previewUrl.value = URL.createObjectURL(file)
  step.value = 'detail'
}

const selectMedia = (event) => {
  setFile(event.target.files?.[0])
}

const handleDrop = (event) => {
  event.preventDefault()
  setFile(event.dataTransfer.files?.[0])
}

const addOverlay = () => {
  const next = {
    id: Date.now(),
    text: '오늘의 기록',
    x: 50,
    y: 50,
    fontSize: 28,
    color: '#fff8e7',
    rotate: 0,
  }
  overlayBoxes.value.push(next)
  activeOverlayId.value = next.id
}

const removeOverlay = (id) => {
  overlayBoxes.value = overlayBoxes.value.filter((box) => box.id !== id)
  activeOverlayId.value = overlayBoxes.value[0]?.id || null
}

const addEmoji = (emoji) => {
  if (!activeOverlay.value) addOverlay()
  activeOverlay.value.text = `${activeOverlay.value.text || ''}${emoji}`
}

const updateOverlayPosition = (event, id = dragOverlayId.value) => {
  if (!id || !mediaEditor.value) return
  const box = overlayBoxes.value.find((item) => item.id === id)
  if (!box) return
  const rect = mediaEditor.value.getBoundingClientRect()
  box.x = Math.round(Math.min(96, Math.max(4, ((event.clientX - rect.left) / rect.width) * 100)))
  box.y = Math.round(Math.min(94, Math.max(6, ((event.clientY - rect.top) / rect.height) * 100)))
}

const startOverlayDrag = (event, id) => {
  dragOverlayId.value = id
  activeOverlayId.value = id
  event.currentTarget.setPointerCapture?.(event.pointerId)
  updateOverlayPosition(event, id)
}

const stopOverlayDrag = () => {
  dragOverlayId.value = null
}

const loadData = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const requests = [getCategories()]
    if (isEdit.value) requests.push(getExpense(props.editId))
    const [categoryResponse, logResponse] = await Promise.all(requests)
    categories.value = categoryResponse.data

    if (logResponse) {
      const data = logResponse.data
      form.category = String(data.category)
      form.amount = String(data.amount || '')
      form.product_name = data.product_name || ''
      form.merchant = data.merchant || ''
      form.content = data.content || data.title || ''
      form.visibility = data.visibility || 'friends'
      form.hide_amount = Boolean(data.hide_amount)
      form.is_visible = Boolean(data.is_visible)
      currentMedia.value = data.media || ''
      const boxes = data.overlay_style?.boxes
      if (Array.isArray(boxes) && boxes.length) {
        overlayBoxes.value = boxes.map((box, index) => ({
          id: box.id || index + 1,
          text: box.text || '',
          x: Number(box.x ?? 50),
          y: Number(box.y ?? 50),
          fontSize: Number(box.fontSize || 28),
          color: box.color || '#fff8e7',
          rotate: Number(box.rotate || 0),
        }))
      } else {
        overlayBoxes.value = data.overlay_text
          ? [
              {
                id: 1,
                text: data.overlay_text || '',
                x: Number(data.overlay_style?.x ?? 50),
                y: Number(data.overlay_style?.y ?? 50),
                fontSize: Number(data.overlay_style?.fontSize || 28),
                color: data.overlay_style?.color || '#fff8e7',
                rotate: Number(data.overlay_style?.rotate || 0),
              },
            ]
          : []
      }
      activeOverlayId.value = overlayBoxes.value[0]?.id || null
      step.value = 'detail'
    } else if (categories.value.length) {
      form.category = String(categories.value[0].id)
    }
  } catch {
    errorMessage.value = '작성 정보를 불러오지 못했습니다.'
  } finally {
    isLoading.value = false
  }
}

const submit = async () => {
  isSubmitting.value = true
  errorMessage.value = ''

  const selectedCategory = categories.value.find((item) => String(item.id) === String(form.category))
  const content = form.content.trim()
  const payload = new FormData()
  payload.append('title', buildTitle(content, selectedCategory))
  payload.append('category', form.category)
  payload.append('amount', form.amount)
  payload.append('product_name', form.product_name)
  payload.append('merchant', form.merchant)
  payload.append('content', content)
  payload.append('overlay_text', normalizedOverlayText.value)
  payload.append(
    'overlay_style',
    JSON.stringify({
      ...(overlayBoxes.value[0] || {}),
      boxes: overlayBoxes.value,
    }),
  )
  payload.append('visibility', form.visibility)
  payload.append('hide_amount', String(form.hide_amount))
  payload.append('is_visible', String(form.is_visible))
  if (mediaFile.value) payload.append('media', mediaFile.value)

  try {
    if (isEdit.value) await updateExpense(props.editId, payload)
    else await createExpense(payload)
    emit('saved')
  } catch (error) {
    const data = error.response?.data
    errorMessage.value = data
      ? Object.values(data).flat().join(' ')
      : '피드 저장 중 오류가 발생했습니다.'
  } finally {
    isSubmitting.value = false
  }
}

onMounted(loadData)

onBeforeUnmount(() => {
  if (previewUrl.value) URL.revokeObjectURL(previewUrl.value)
})
</script>

<template>
  <Teleport to="body">
    <div class="composer-backdrop" @click.self="$emit('close')">
      <section class="composer-modal" role="dialog" aria-modal="true" aria-label="피드 작성">
        <header class="composer-header">
          <div>
            <span>{{ isEdit ? 'EDIT FEED' : 'NEW FEED' }}</span>
            <h2 class="display-title">{{ isEdit ? '피드 수정' : '피드 작성' }}</h2>
          </div>
          <button type="button" aria-label="닫기" @click="$emit('close')">×</button>
        </header>

        <div v-if="isLoading" class="composer-state">작성 도구를 준비하는 중...</div>

        <form v-else class="composer-body" @submit.prevent="submit">
          <div
            ref="mediaEditor"
            class="upload-panel"
            :class="{ ready: hasMedia }"
            @dragover.prevent
            @drop="handleDrop"
          >
            <template v-if="hasMedia">
              <video v-if="previewIsVideo" :src="previewMedia" controls playsinline></video>
              <img v-else :src="previewMedia" alt="피드 미리보기">
              <button class="change-media" type="button" @click="openFileDialog">파일 변경</button>
            </template>
            <template v-else>
              <div class="drop-copy">
                <strong>사진이나 영상을 끌어다 놓으세요</strong>
                <p>JPG, PNG, GIF, WEBP, MP4, WEBM · 최대 10MB</p>
                <button class="vintage-button" type="button" @click="openFileDialog">파일 선택</button>
              </div>
            </template>

            <button
              v-for="box in overlayBoxes"
              :key="box.id"
              class="overlay-box"
              :class="{ active: activeOverlayId === box.id }"
              :style="overlayStyle(box)"
              type="button"
              @pointerdown.stop.prevent="startOverlayDrag($event, box.id)"
              @pointermove.stop.prevent="updateOverlayPosition"
              @pointerup="stopOverlayDrag"
              @pointercancel="stopOverlayDrag"
            >
              {{ box.text || '텍스트' }}
            </button>

            <input
              ref="fileInput"
              class="visually-hidden"
              type="file"
              accept="image/*,video/mp4,video/webm"
              @change="selectMedia"
            >
          </div>

          <Transition name="composer-slide">
            <div v-if="step === 'detail'" class="detail-panel">
              <div class="field-grid">
                <label>
                  카테고리
                  <select v-model="form.category" class="form-select" required>
                    <option v-for="category in categories" :key="category.id" :value="String(category.id)">
                      {{ category.name }}
                    </option>
                  </select>
                </label>

                <label>
                  금액
                  <input v-model="form.amount" class="form-control" type="number" min="1" step="1" required>
                </label>
              </div>

              <label>
                내용
                <textarea
                  v-model="form.content"
                  class="form-control"
                  rows="5"
                  maxlength="2000"
                  placeholder="오늘의 소비를 기록해보세요."
                ></textarea>
              </label>

              <div class="field-grid">
                <label>
                  상품/물건
                  <input v-model.trim="form.product_name" class="form-control" maxlength="100">
                </label>
                <label>
                  상호/장소
                  <input v-model.trim="form.merchant" class="form-control" maxlength="100">
                </label>
              </div>

              <section class="overlay-editor glass-panel">
                <div class="editor-head">
                  <strong>이미지 안 텍스트 박스</strong>
                  <button type="button" @click="addOverlay">+ 추가</button>
                </div>

                <div v-if="overlayBoxes.length" class="overlay-list">
                  <button
                    v-for="box in overlayBoxes"
                    :key="box.id"
                    type="button"
                    :class="{ active: activeOverlayId === box.id }"
                    @click="activeOverlayId = box.id"
                  >
                    {{ box.text || '빈 텍스트' }}
                  </button>
                </div>

                <template v-if="activeOverlay">
                  <label>
                    텍스트
                    <input v-model="activeOverlay.text" class="form-control" maxlength="80">
                  </label>

                  <div class="emoji-row">
                    <button v-for="emoji in ['✨', '💸', '💰', '☕', '🍽️', '📈']" :key="emoji" type="button" @click="addEmoji(emoji)">
                      {{ emoji }}
                    </button>
                  </div>

                  <div class="field-grid overlay-controls">
                    <label>
                      크기
                      <input v-model.number="activeOverlay.fontSize" class="form-range" type="range" min="16" max="58">
                    </label>
                    <label>
                      회전
                      <input v-model.number="activeOverlay.rotate" class="form-range" type="range" min="-45" max="45">
                    </label>
                    <label>
                      색상
                      <input v-model="activeOverlay.color" class="form-control form-control-color" type="color">
                    </label>
                  </div>

                  <button class="remove-overlay" type="button" @click="removeOverlay(activeOverlay.id)">텍스트 박스 삭제</button>
                </template>
                <p v-else class="overlay-empty">추가 버튼을 눌러 이미지 안 텍스트 박스를 만들 수 있습니다.</p>
              </section>

              <div class="option-grid">
                <label>
                  공개 범위
                  <select v-model="form.visibility" class="form-select">
                    <option value="public">전체 공개</option>
                    <option value="friends">친구 공개</option>
                    <option value="private">나만 보기</option>
                  </select>
                </label>
                <label class="check-row">
                  <input v-model="form.hide_amount" type="checkbox">
                  금액 숨김
                </label>
                <label class="check-row">
                  <input v-model="form.is_visible" type="checkbox">
                  피드에 표시
                </label>
              </div>

              <p v-if="errorMessage" class="composer-error">{{ errorMessage }}</p>

              <div class="composer-actions">
                <button class="vintage-button" :disabled="isSubmitting">
                  {{ isSubmitting ? '저장 중...' : '저장하기' }}
                </button>
                <button type="button" class="ghost-button" @click="$emit('close')">취소</button>
              </div>
            </div>
          </Transition>
        </form>
      </section>
    </div>
  </Teleport>
</template>

<style scoped>
.composer-backdrop {
  position: fixed;
  inset: 0;
  z-index: 120;
  display: grid;
  place-items: center;
  background: rgba(23, 19, 13, 0.34);
  padding: 18px;
  backdrop-filter: blur(10px);
}

.composer-modal {
  display: grid;
  width: min(100%, 1040px);
  max-height: min(92vh, 820px);
  overflow: hidden;
  border: 3px solid var(--color-ink);
  border-radius: 28px;
  background: rgba(255, 248, 231, 0.92);
  box-shadow: 9px 9px 0 var(--color-ink), 0 30px 90px rgba(0, 0, 0, 0.24);
}

.composer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  border-bottom: 2px solid var(--color-ink);
  padding: 16px 20px;
}

.composer-header span {
  color: var(--color-dark-gold);
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0.12em;
}

.composer-header h2 {
  margin: 2px 0 0;
  font-size: 30px;
}

.composer-header button {
  width: 40px;
  height: 40px;
  border: 2px solid var(--color-ink);
  border-radius: 50%;
  background: var(--color-paper);
  color: var(--color-ink);
  font-size: 28px;
  line-height: 1;
}

.composer-state {
  min-height: 360px;
  display: grid;
  place-items: center;
  color: var(--color-muted);
}

.composer-body {
  display: grid;
  grid-template-columns: minmax(300px, 0.92fr) minmax(360px, 1.08fr);
  gap: 0;
  min-height: 580px;
  overflow: auto;
}

.upload-panel {
  position: sticky;
  top: 0;
  display: grid;
  min-height: 580px;
  place-items: center;
  overflow: hidden;
  border-right: 2px solid var(--color-ink);
  background:
    radial-gradient(circle at 20% 20%, rgba(216, 165, 38, 0.18), transparent 30%),
    var(--color-money-light);
}

.upload-panel img,
.upload-panel video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.drop-copy {
  display: grid;
  justify-items: center;
  gap: 12px;
  max-width: 300px;
  padding: 22px;
  text-align: center;
}

.drop-copy strong {
  font-size: 22px;
}

.drop-copy p {
  margin: 0;
  color: var(--color-muted);
}

.change-media {
  position: absolute;
  top: 16px;
  right: 16px;
  border: 2px solid var(--color-ink);
  border-radius: 999px;
  background: rgba(255, 248, 231, 0.86);
  color: var(--color-ink);
  padding: 8px 12px;
  font-size: 12px;
  font-weight: 900;
}

.overlay-box {
  position: absolute;
  max-width: 82%;
  border: 0;
  background: transparent;
  color: #fff8e7;
  padding: 2px;
  font-weight: 900;
  line-height: 1.1;
  text-align: center;
  text-shadow: 2px 2px 0 var(--color-ink), 0 10px 24px rgba(0, 0, 0, 0.45);
  transform: translate(-50%, -50%);
  touch-action: none;
  user-select: none;
  white-space: pre-wrap;
}

.overlay-box.active {
  outline: 2px dashed rgba(255, 248, 231, 0.8);
}

.detail-panel {
  display: grid;
  align-content: start;
  gap: 14px;
  padding: 20px;
}

label {
  display: grid;
  gap: 6px;
  color: var(--color-muted);
  font-weight: 900;
}

.field-grid,
.option-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.overlay-editor {
  display: grid;
  gap: 12px;
  padding: 14px;
}

.editor-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.editor-head button,
.overlay-list button,
.emoji-row button,
.remove-overlay,
.ghost-button {
  border: 2px solid var(--color-ink);
  border-radius: 999px;
  background: var(--color-paper);
  color: var(--color-ink);
  padding: 7px 11px;
  font-size: 12px;
  font-weight: 900;
}

.overlay-list,
.emoji-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.overlay-list button.active {
  background: var(--color-gold);
}

.emoji-row button {
  width: 38px;
  height: 38px;
  padding: 0;
}

.overlay-controls {
  align-items: end;
}

.overlay-empty {
  margin: 0;
  color: var(--color-muted);
  font-size: 13px;
}

.option-grid {
  grid-template-columns: minmax(180px, 1fr) auto auto;
  align-items: end;
}

.check-row {
  display: inline-flex;
  align-items: center;
  gap: 7px;
  min-height: 44px;
}

.composer-error {
  border-radius: 14px;
  background: rgba(182, 74, 53, 0.12);
  color: var(--color-red);
  margin: 0;
  padding: 10px 12px;
}

.composer-actions {
  display: flex;
  align-items: center;
  gap: 10px;
  padding-top: 4px;
}

.visually-hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0 0 0 0);
}

.composer-slide-enter-active,
.composer-slide-leave-active {
  transition: opacity 0.26s ease, transform 0.26s ease;
}

.composer-slide-enter-from,
.composer-slide-leave-to {
  opacity: 0;
  transform: translateX(18px);
}

@media (max-width: 860px) {
  .composer-body {
    grid-template-columns: 1fr;
  }

  .upload-panel {
    position: relative;
    min-height: 360px;
    border-right: 0;
    border-bottom: 2px solid var(--color-ink);
  }

  .field-grid,
  .option-grid {
    grid-template-columns: 1fr;
  }
}
</style>
