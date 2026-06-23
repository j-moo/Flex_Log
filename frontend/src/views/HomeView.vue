<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

import BrandLogo from '../components/common/BrandLogo.vue'

const phrases = [
  '소비를 기록하세요.',
  '소비를 관리하세요.',
  '함께 성장하세요.',
  '기록이 자산이 됩니다.',
]

const index = ref(0)
const showActions = computed(() => index.value >= phrases.length - 1)
let timer = null

onMounted(() => {
  timer = window.setInterval(() => {
    if (index.value < phrases.length - 1) index.value += 1
    else window.clearInterval(timer)
  }, 1450)
})

onBeforeUnmount(() => {
  if (timer) window.clearInterval(timer)
})
</script>

<template>
  <section class="intro-page">
    <div class="intro-stage">
      <div class="coin-halo" aria-hidden="true"></div>
      <BrandLogo class="hero-logo" :variant="2" size="large" alt="Flex-Log 대표 로고" />

      <p class="intro-kicker">Finance SNS</p>
      <h1 class="display-title">Flex-Log</h1>

      <Transition name="phrase" mode="out-in">
        <p :key="phrases[index]" class="intro-phrase">{{ phrases[index] }}</p>
      </Transition>

      <Transition name="fade-slide">
        <div v-if="showActions" class="intro-actions">
          <RouterLink class="vintage-button intro-primary" :to="{ name: 'signup' }">
            Flex-Log 시작하기
          </RouterLink>
          <RouterLink class="intro-login" :to="{ name: 'login' }">이미 계정이 있어요</RouterLink>
        </div>
      </Transition>
    </div>
  </section>
</template>

<style scoped>
.intro-page {
  position: relative;
  display: grid;
  min-height: 100vh;
  place-items: center;
  overflow: hidden;
  padding: 44px 18px 34px;
}

.intro-page::before,
.intro-page::after {
  position: absolute;
  width: 340px;
  height: 340px;
  border: 2px solid rgba(23, 19, 13, 0.12);
  border-radius: 50%;
  content: '';
  filter: blur(1px);
}

.intro-page::before {
  top: -90px;
  left: -110px;
  background: rgba(200, 210, 170, 0.36);
}

.intro-page::after {
  right: -110px;
  bottom: -90px;
  background: rgba(216, 165, 38, 0.24);
}

.intro-stage {
  position: relative;
  z-index: 1;
  display: grid;
  justify-items: center;
  width: min(100%, 720px);
  text-align: center;
}

.coin-halo {
  position: absolute;
  top: 24px;
  width: min(72vw, 430px);
  height: min(72vw, 430px);
  border: 2px dashed rgba(140, 100, 20, 0.35);
  border-radius: 50%;
  animation: spin-slow 24s linear infinite;
}

.hero-logo {
  animation: logo-pop 0.72s cubic-bezier(.2, 1.2, .28, 1) both;
}

.intro-kicker {
  margin: 26px 0 4px;
  border: 2px solid var(--color-ink);
  border-radius: 999px;
  background: var(--color-money-light);
  padding: 6px 14px;
  font-family: 'Fredoka', sans-serif;
  font-size: 12px;
  font-weight: 900;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

h1 {
  margin: 8px 0 0;
  font-size: clamp(52px, 10vw, 96px);
  line-height: 0.95;
  text-shadow: 4px 4px 0 rgba(216, 165, 38, 0.72);
}

.intro-phrase {
  min-height: 42px;
  margin: 22px 0 0;
  color: var(--color-muted);
  font-size: clamp(20px, 4vw, 30px);
  font-weight: 900;
}

.intro-actions {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 14px;
  margin-top: 20px;
}

.intro-primary {
  min-height: 54px;
  padding: 0 28px;
  font-size: 17px;
}

.intro-login {
  border-bottom: 2px solid var(--color-ink);
  color: var(--color-ink);
  font-weight: 900;
}

.phrase-enter-active,
.phrase-leave-active {
  transition: opacity 0.34s ease, transform 0.34s ease;
}

.phrase-enter-from,
.phrase-leave-to {
  opacity: 0;
  transform: translateY(14px) scale(0.98);
}

@keyframes logo-pop {
  from {
    opacity: 0;
    transform: translateY(20px) rotate(-3deg) scale(0.88);
  }
  to {
    opacity: 1;
    transform: translateY(0) rotate(0) scale(1);
  }
}

@keyframes spin-slow {
  to {
    transform: rotate(360deg);
  }
}
</style>
