<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'


const phrases = [
  '소비를 기록하세요.',
  '소비 습관을 돌아보세요.',
  'AI가 소비 패턴을 분석합니다.',
  '나에게 맞는 금융 습관을 만들어보세요.',
]

const index = ref(0)
let timer = null

const isLast = computed(() => index.value === phrases.length - 1)

onMounted(() => {
  timer = window.setInterval(() => {
    if (index.value < phrases.length - 1) {
      index.value += 1
    } else {
      window.clearInterval(timer)
    }
  }, 1500)
})

onBeforeUnmount(() => {
  if (timer) window.clearInterval(timer)
})
</script>

<template>
  <section class="home-hero">
    <div class="hero-content">
      <p class="eyebrow">Flex Log</p>
      <Transition name="phrase" mode="out-in">
        <h1 :key="phrases[index]">{{ phrases[index] }}</h1>
      </Transition>
      <p class="hero-copy">
        소비 기록을 피드로 남기고, 친구와 공유하고, AI 분석과 금융상품 추천까지 연결합니다.
      </p>
      <div v-if="isLast" class="hero-actions">
        <RouterLink class="btn btn-primary btn-lg" :to="{ name: 'signup' }">회원가입</RouterLink>
        <RouterLink class="btn btn-outline-dark btn-lg" :to="{ name: 'login' }">로그인</RouterLink>
      </div>
    </div>
  </section>
</template>

<style scoped>
.home-hero {
  display: grid;
  min-height: calc(100vh - 56px);
  place-items: center;
}

.hero-content {
  width: min(100%, 680px);
}

.eyebrow {
  margin-bottom: 18px;
  color: #2f6b5e;
  font-weight: 850;
}

h1 {
  min-height: 140px;
  margin: 0;
  color: #172033;
  font-size: clamp(42px, 9vw, 76px);
  font-weight: 900;
  letter-spacing: 0;
  line-height: 1.05;
}

.hero-copy {
  max-width: 560px;
  margin: 18px 0 0;
  color: #566273;
  font-size: 18px;
  line-height: 1.7;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 28px;
}

.phrase-enter-active,
.phrase-leave-active {
  transition: opacity 0.35s ease, transform 0.35s ease;
}

.phrase-enter-from,
.phrase-leave-to {
  opacity: 0;
  transform: translateY(12px);
}

@media (max-width: 640px) {
  h1 {
    min-height: 116px;
  }

  .hero-copy {
    font-size: 16px;
  }

  .hero-actions .btn {
    width: 100%;
  }
}
</style>
