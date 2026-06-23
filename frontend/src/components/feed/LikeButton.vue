<script setup>
defineProps({
  liked: Boolean,
  count: {
    type: Number,
    default: 0,
  },
  disabled: Boolean,
})

defineEmits(['toggle'])
</script>

<template>
  <button
    class="like-button"
    :class="{ liked }"
    type="button"
    :disabled="disabled"
    :aria-label="liked ? '좋아요 취소' : '좋아요'"
    @click="$emit('toggle')"
  >
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78L12 21.23l8.84-8.84a5.5 5.5 0 0 0 0-7.78Z" />
    </svg>
    <span>{{ count }}</span>
  </button>
</template>

<style scoped>
.like-button {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 0;
  background: transparent;
  color: var(--color-ink);
  padding: 3px;
  font-weight: 900;
}

.like-button svg {
  width: 26px;
  height: 26px;
  fill: transparent;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.9;
  transition: transform 0.16s ease;
}

.like-button:hover svg {
  transform: scale(1.12) rotate(-4deg);
}

.like-button.liked {
  color: var(--color-red);
}

.like-button.liked svg {
  fill: currentColor;
}

.like-button:disabled {
  opacity: 0.55;
}
</style>
