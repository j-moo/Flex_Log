<script setup>
import { computed, onBeforeUnmount, onMounted, ref } from 'vue'

import logo1 from '../../assets/brand/logo-1.png'
import logo2 from '../../assets/brand/logo-2.png'
import logo3 from '../../assets/brand/logo-3.png'
import logo4 from '../../assets/brand/logo-4.png'
import logo5 from '../../assets/brand/logo-5.png'
import logo6 from '../../assets/brand/logo-6.png'
import logo7 from '../../assets/brand/logo-7.png'
import logo8 from '../../assets/brand/logo-8.png'

const props = defineProps({
  variant: {
    type: Number,
    default: 2,
  },
  rotating: {
    type: Boolean,
    default: false,
  },
  size: {
    type: String,
    default: 'medium',
  },
  alt: {
    type: String,
    default: 'Flex-Log logo',
  },
})

const logos = [logo1, logo2, logo3, logo4, logo5, logo6, logo7, logo8]
const index = ref(Math.max(0, Math.min(logos.length - 1, props.variant - 1)))
let timer = null

const source = computed(() => logos[index.value] || logo2)

onMounted(() => {
  if (!props.rotating) return
  timer = window.setInterval(() => {
    index.value = (index.value + 1) % logos.length
  }, 3000)
})

onBeforeUnmount(() => {
  if (timer) window.clearInterval(timer)
})
</script>

<template>
  <span class="brand-logo" :class="`brand-logo--${size}`">
    <Transition name="logo-swap" mode="out-in">
      <img :key="source" :src="source" :alt="alt">
    </Transition>
  </span>
</template>

<style scoped>
.brand-logo {
  position: relative;
  display: inline-grid;
  place-items: center;
  overflow: hidden;
  border: 2px solid var(--color-ink);
  border-radius: 50%;
  background: var(--color-paper);
  box-shadow: 3px 3px 0 var(--color-ink);
}

.brand-logo--small {
  width: 46px;
  height: 46px;
}

.brand-logo--medium {
  width: 74px;
  height: 74px;
}

.brand-logo--large {
  width: min(56vw, 330px);
  height: min(56vw, 330px);
  border-width: 3px;
  box-shadow: 7px 7px 0 var(--color-ink);
}

.brand-logo--wide {
  width: min(68vw, 300px);
  height: 170px;
  border-radius: 26px;
}

img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: center;
  transform: scale(1.08);
}

.brand-logo--small img,
.brand-logo--medium img {
  transform: scale(1.18);
}

.brand-logo--large img {
  transform: scale(1.16);
}

.brand-logo--wide img {
  transform: scale(1.12);
}

.logo-swap-enter-active,
.logo-swap-leave-active {
  transition: opacity 0.28s ease, transform 0.28s ease;
}

.logo-swap-enter-from {
  opacity: 0;
  transform: rotate(-4deg) scale(0.92);
}

.logo-swap-leave-to {
  opacity: 0;
  transform: rotate(4deg) scale(1.08);
}
</style>
