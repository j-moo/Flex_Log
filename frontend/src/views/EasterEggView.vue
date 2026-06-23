<script setup>
import { onBeforeUnmount, onMounted, ref } from 'vue'

const message = '케로챠~~~'
const typedText = ref('')
let timer = null

onMounted(() => {
  let cursor = 0
  timer = window.setInterval(() => {
    typedText.value = message.slice(0, cursor + 1)
    cursor += 1
    if (cursor >= message.length) window.clearInterval(timer)
  }, 260)
})

onBeforeUnmount(() => {
  if (timer) window.clearInterval(timer)
})
</script>

<template>
  <section class="easter-page page-shell">
    <div class="easter-panel glass-panel">
      <span>EASTER EGG</span>
      <h1>{{ typedText }}<i v-if="typedText.length < message.length">|</i></h1>
      <RouterLink class="vintage-button" :to="{ name: 'feed' }">피드로 돌아가기</RouterLink>
    </div>
  </section>
</template>

<style scoped>
.easter-page {
  min-height: calc(100vh - 180px);
  display: grid;
  place-items: center;
}

.easter-panel {
  display: grid;
  justify-items: center;
  gap: 18px;
  width: min(100%, 620px);
  border: 2px solid var(--color-ink);
  border-radius: 26px;
  background: var(--color-paper);
  box-shadow: 7px 7px 0 var(--color-ink);
  padding: clamp(34px, 8vw, 72px) 24px;
  text-align: center;
}

.easter-panel span {
  color: var(--color-dark-gold);
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.16em;
}

.easter-panel h1 {
  min-height: 1.2em;
  margin: 0;
  font-size: clamp(54px, 12vw, 112px);
  line-height: 1;
}

.easter-panel i {
  font-style: normal;
  animation: blink 0.8s steps(2, start) infinite;
}

@keyframes blink {
  50% {
    opacity: 0;
  }
}
</style>
