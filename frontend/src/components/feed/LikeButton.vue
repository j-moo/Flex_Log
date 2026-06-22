<script setup>
defineProps({ liked: Boolean, count: { type: Number, default: 0 }, disabled: Boolean })
defineEmits(['toggle'])
</script>

<template>
  <button class="like-button" :class="{ liked }" type="button" :disabled="disabled" :aria-label="liked ? '좋아요 취소' : '좋아요'" @click="$emit('toggle')">
    <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78L12 21.23l8.84-8.84a5.5 5.5 0 0 0 0-7.78Z" /></svg>
    <span>{{ count }}</span>
  </button>
</template>

<style scoped>
.like-button{display:inline-flex;align-items:center;gap:6px;margin:0;border:0;background:transparent;color:var(--ink);padding:3px;font-weight:750}.like-button svg{width:25px;height:25px;fill:transparent;stroke:currentColor;stroke-width:1.8;transition:transform .16s ease}.like-button:hover svg{transform:scale(1.08)}.like-button.liked{color:#ed4956}.like-button.liked svg{fill:currentColor}.like-button:disabled{opacity:.55}
</style>
