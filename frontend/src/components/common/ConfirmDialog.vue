<script setup>
defineProps({
  open: Boolean,
  title: {
    type: String,
    default: '확인',
  },
  message: {
    type: String,
    default: '',
  },
  detail: {
    type: String,
    default: '',
  },
  confirmText: {
    type: String,
    default: '확인',
  },
  cancelText: {
    type: String,
    default: '취소',
  },
  tone: {
    type: String,
    default: 'danger',
  },
  loading: Boolean,
})

defineEmits(['close', 'confirm'])
</script>

<template>
  <Teleport to="body">
    <div
      v-if="open"
      class="confirm-backdrop"
      role="presentation"
      @click.self="$emit('close')"
      @keydown.esc="$emit('close')"
    >
      <section class="confirm-dialog" role="dialog" aria-modal="true" :aria-label="title">
        <header>
          <div>
            <span>{{ tone === 'danger' ? 'CONFIRM' : 'NOTICE' }}</span>
            <h2>{{ title }}</h2>
          </div>
          <button type="button" aria-label="닫기" :disabled="loading" @click="$emit('close')">×</button>
        </header>

        <p v-if="message" class="confirm-message">{{ message }}</p>
        <p v-if="detail" class="confirm-detail">{{ detail }}</p>

        <div class="confirm-actions">
          <button type="button" class="confirm-cancel" :disabled="loading" @click="$emit('close')">
            {{ cancelText }}
          </button>
          <button
            type="button"
            class="confirm-submit"
            :class="tone"
            :disabled="loading"
            @click="$emit('confirm')"
          >
            {{ loading ? '처리 중...' : confirmText }}
          </button>
        </div>
      </section>
    </div>
  </Teleport>
</template>

<style scoped>
.confirm-backdrop {
  position: fixed;
  inset: 0;
  z-index: 170;
  display: grid;
  place-items: center;
  background: rgba(23, 19, 13, 0.42);
  padding: 18px;
  backdrop-filter: blur(10px);
}

.confirm-dialog {
  display: grid;
  gap: 14px;
  width: min(100%, 420px);
  border: 2px solid var(--color-ink);
  border-radius: 22px;
  background: var(--color-paper);
  box-shadow: 6px 6px 0 var(--color-ink), var(--shadow-soft);
  padding: 20px;
}

.confirm-dialog header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
}

.confirm-dialog header span {
  color: var(--color-dark-gold);
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0.12em;
}

.confirm-dialog h2,
.confirm-message,
.confirm-detail {
  margin: 0;
}

.confirm-dialog h2 {
  margin-top: 3px;
  font-size: 23px;
}

.confirm-dialog header > button {
  display: grid;
  width: 36px;
  height: 36px;
  flex: 0 0 auto;
  place-items: center;
  border: 2px solid var(--color-ink);
  border-radius: 50%;
  background: var(--color-paper);
  color: var(--color-ink);
  padding: 0;
  font-size: 24px;
  font-weight: 900;
  line-height: 1;
}

.confirm-message {
  color: var(--color-ink);
  font-weight: 900;
  line-height: 1.55;
}

.confirm-detail {
  border-radius: 14px;
  background: rgba(23, 19, 13, 0.07);
  color: var(--color-muted);
  padding: 11px 12px;
  line-height: 1.55;
}

.confirm-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}

.confirm-cancel,
.confirm-submit {
  border: 2px solid var(--color-ink);
  border-radius: 999px;
  box-shadow: 3px 3px 0 var(--color-ink);
  padding: 9px 14px;
  font-weight: 900;
  transition: transform 0.16s ease, box-shadow 0.16s ease, background 0.16s ease;
}

.confirm-cancel {
  background: var(--color-paper);
  color: var(--color-ink);
}

.confirm-submit {
  background: var(--color-gold);
  color: var(--color-ink);
}

.confirm-submit.danger {
  background: var(--color-red);
  color: var(--color-paper);
}

.confirm-submit:hover:not(:disabled),
.confirm-cancel:hover:not(:disabled) {
  box-shadow: 1px 1px 0 var(--color-ink);
  transform: translate(2px, 2px);
}

.confirm-submit:active:not(:disabled),
.confirm-cancel:active:not(:disabled) {
  box-shadow: 0 0 0 var(--color-ink);
  transform: translate(3px, 3px);
}

.confirm-submit:disabled,
.confirm-cancel:disabled {
  opacity: 0.58;
  box-shadow: none;
}
</style>
