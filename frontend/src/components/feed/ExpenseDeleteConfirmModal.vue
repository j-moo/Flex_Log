<script setup>
import { computed, ref, watch } from 'vue'

import {
  DELETE_NAG_MESSAGES,
  buildExpenseDeleteConfirmText,
  pickRandomMessage,
} from '../../constants/expense'

const props = defineProps({
  open: Boolean,
  targetTitle: {
    type: String,
    default: '선택한 게시글',
  },
  isDeleting: Boolean,
  errorMessage: {
    type: String,
    default: '',
  },
})

const emit = defineEmits(['close', 'confirm'])

const confirmCode = ref('')
const confirmInput = ref('')
const nagMessage = ref('')

const fullConfirmText = computed(() => buildExpenseDeleteConfirmText(confirmCode.value))
const isMatched = computed(() => confirmInput.value === fullConfirmText.value)

const generateConfirmCode = () => String(Math.floor(1000 + Math.random() * 9000))

const resetModal = () => {
  confirmCode.value = generateConfirmCode()
  confirmInput.value = ''
  nagMessage.value = ''
}

const showRandomNag = () => {
  nagMessage.value = pickRandomMessage(DELETE_NAG_MESSAGES)
}

const blockPasteShortcut = (event) => {
  const key = event.key.toLowerCase()
  if ((key === 'v' && (event.ctrlKey || event.metaKey)) || (event.key === 'Insert' && event.shiftKey)) {
    event.preventDefault()
    showRandomNag()
  }
}

const blockInsertedText = (event) => {
  event.preventDefault()
  showRandomNag()
}

const blockBeforeInput = (event) => {
  if (['insertFromPaste', 'insertFromDrop'].includes(event.inputType)) {
    event.preventDefault()
    showRandomNag()
  }
}

const submit = () => {
  if (!isMatched.value || props.isDeleting) {
    if (confirmInput.value) showRandomNag()
    return
  }
  emit('confirm', {
    confirmation_text: fullConfirmText.value,
    confirmation_code: confirmCode.value,
  })
}

const handleDisabledAttempt = () => {
  if (!isMatched.value && confirmInput.value && !props.isDeleting) showRandomNag()
}

watch(
  () => props.open,
  (open) => {
    if (open) resetModal()
  },
  { immediate: true },
)

watch(confirmInput, (value) => {
  if (!value || isMatched.value) {
    nagMessage.value = ''
    return
  }
  showRandomNag()
})
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="delete-confirm-backdrop"
      @click.self="$emit('close')"
      @keydown.esc="$emit('close')"
    >
      <form class="delete-confirm-modal glass-panel" @submit.prevent="submit">
        <header>
          <div>
            <span>DELETE FEED</span>
            <h2>피드 삭제 확인</h2>
            <p>{{ targetTitle }}</p>
          </div>
          <button type="button" aria-label="닫기" :disabled="isDeleting" @click="$emit('close')">×</button>
        </header>

        <!-- 삭제는 통계와 AI 분석 원본 데이터에 영향을 주므로 경고 문구를 직접 입력받는다. -->
        <section class="delete-warning" @contextmenu.prevent>
          {{ fullConfirmText }}
        </section>

        <label>
          위 문구를 정확히 입력해야 삭제할 수 있습니다.
          <textarea
            v-model="confirmInput"
            rows="5"
            autocomplete="off"
            spellcheck="false"
            :disabled="isDeleting"
            :placeholder="fullConfirmText"
            @keydown="blockPasteShortcut"
            @beforeinput="blockBeforeInput"
            @paste="blockInsertedText"
            @dragover.prevent
            @drop="blockInsertedText"
          ></textarea>
        </label>

        <p v-if="errorMessage" class="delete-error">{{ errorMessage }}</p>
        <p v-else-if="nagMessage" class="nag-message">{{ nagMessage }}</p>
        <p v-else class="delete-hint">
          삭제 후에는 프로필 피드, 월별 소비 통계, AI 추천 결과가 달라질 수 있습니다.
        </p>

        <div class="delete-actions">
          <button type="button" class="ghost-button" :disabled="isDeleting" @click="$emit('close')">취소</button>
          <span class="danger-action-wrap" @pointerdown="handleDisabledAttempt">
            <button class="danger-button" type="submit" :disabled="!isMatched || isDeleting">
              {{ isDeleting ? '삭제 중...' : '삭제' }}
            </button>
          </span>
        </div>
      </form>
    </div>
  </Teleport>
</template>

<style scoped>
.delete-confirm-backdrop {
  position: fixed;
  inset: 0;
  z-index: 120;
  display: grid;
  place-items: center;
  background: rgba(23, 19, 13, 0.46);
  padding: 20px;
}

.delete-confirm-modal {
  display: grid;
  gap: 14px;
  width: min(100%, 560px);
  border: 2px solid var(--color-ink);
  border-radius: 22px;
  background: var(--color-paper);
  box-shadow: 6px 6px 0 var(--color-ink);
  padding: 20px;
}

.delete-confirm-modal header {
  display: flex;
  align-items: start;
  justify-content: space-between;
  gap: 12px;
}

.delete-confirm-modal header span {
  color: var(--color-red);
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0.12em;
}

.delete-confirm-modal h2,
.delete-confirm-modal p {
  margin: 0;
}

.delete-confirm-modal header p,
.delete-confirm-modal label,
.delete-hint {
  color: var(--color-muted);
}

.delete-confirm-modal header > button {
  display: grid;
  width: 34px;
  height: 34px;
  place-items: center;
  border: 2px solid var(--color-ink);
  border-radius: 50%;
  background: var(--color-paper);
  color: var(--color-ink);
  font-size: 22px;
  font-weight: 900;
  line-height: 1;
}

.delete-warning {
  user-select: none;
  border: 2px solid rgba(182, 74, 53, 0.4);
  border-radius: 16px;
  background: rgba(182, 74, 53, 0.12);
  color: var(--color-red);
  padding: 12px;
  font-weight: 900;
  line-height: 1.55;
}

.delete-confirm-modal label {
  display: grid;
  gap: 8px;
  font-weight: 900;
}

.delete-confirm-modal textarea {
  width: 100%;
  resize: vertical;
  border: 2px solid rgba(23, 19, 13, 0.24);
  border-radius: 14px;
  background: rgba(255, 248, 231, 0.86);
  color: var(--color-ink);
  padding: 11px;
  line-height: 1.5;
}

.delete-error,
.nag-message {
  border: 2px solid rgba(182, 74, 53, 0.28);
  border-radius: 14px;
  background: rgba(182, 74, 53, 0.1);
  color: var(--color-red);
  padding: 10px;
  font-weight: 900;
}

.nag-message {
  border-color: rgba(216, 165, 38, 0.5);
  background: rgba(216, 165, 38, 0.16);
  color: var(--color-dark-gold);
}

.delete-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.danger-action-wrap {
  display: inline-flex;
}

.ghost-button,
.danger-button {
  border: 2px solid var(--color-ink);
  border-radius: 999px;
  padding: 9px 14px;
  font-weight: 900;
}

.ghost-button {
  background: var(--color-paper);
  color: var(--color-ink);
}

.danger-button {
  background: var(--color-red);
  color: var(--color-paper);
}

.danger-button:disabled {
  opacity: 0.48;
  cursor: not-allowed;
}
</style>
