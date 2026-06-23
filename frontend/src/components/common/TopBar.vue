<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useAccountStore } from '../../stores/account'
import BrandLogo from './BrandLogo.vue'

const emit = defineEmits(['logout', 'compose'])

const route = useRoute()
const router = useRouter()
const account = useAccountStore()
const imageLoadFailed = ref(false)
const brandClickCount = ref(0)
const isDarkMode = ref(false)
const THEME_KEY = 'flexlog.theme'
let brandClickResetTimer = null

const navItems = [
  {
    name: 'feed',
    label: '홈',
    icon: 'M3 11.5 12 4l9 7.5V21h-6v-6H9v6H3z',
    matches: ['feed'],
  },
  {
    name: 'finance-hub',
    label: '금융',
    icon: 'M4 20V10m5 10V4m6 16v-7m5 7V7',
    matches: [
      'finance-hub',
      'finance-products',
      'finance-recommend',
      'analysis',
      'commodities',
      'stocks',
      'stock-search',
      'youtube-search',
      'youtube-detail',
      'nearby-banks',
      'finance-day',
    ],
  },
  {
    name: 'notifications',
    label: '알림',
    icon: 'M18 8a6 6 0 0 0-12 0c0 7-3 7-3 9h18c0-2-3-2-3-9M13.73 21a2 2 0 0 1-3.46 0',
    matches: ['notifications'],
  },
  {
    name: 'compose',
    label: '피드작성',
    icon: 'M12 5v14M5 12h14',
    action: 'compose',
    matches: ['log-create', 'log-edit'],
  },
  {
    name: 'profile',
    label: '프로필',
    icon: 'M20 21a8 8 0 0 0-16 0m8-9a4 4 0 1 0 0-8 4 4 0 0 0 0 8',
    matches: ['profile', 'user-profile', 'mypage', 'logs', 'log-detail'],
  },
]

const userName = computed(() =>
  account.user?.name || account.user?.username || account.user?.email || 'Flexer',
)

const profileImage = computed(() => (
  imageLoadFailed.value ? null : account.user?.profile_image
))

watch(() => account.user?.profile_image, () => {
  imageLoadFailed.value = false
})

const applyTheme = (dark) => {
  isDarkMode.value = dark
  document.documentElement.dataset.theme = dark ? 'dark' : 'light'
  window.localStorage.setItem(THEME_KEY, dark ? 'dark' : 'light')
}

const toggleTheme = () => {
  applyTheme(!isDarkMode.value)
}

onMounted(() => {
  const savedTheme = window.localStorage.getItem(THEME_KEY)
  const prefersDark = window.matchMedia?.('(prefers-color-scheme: dark)').matches
  applyTheme(savedTheme ? savedTheme === 'dark' : Boolean(prefersDark))

  if (account.isAuthenticated && !account.user?.profile_image) {
    account.fetchMe().catch(() => {})
  }
})

onBeforeUnmount(() => {
  if (brandClickResetTimer) window.clearTimeout(brandClickResetTimer)
})

const isActive = (item) => item.matches.includes(route.name)

const handleNav = (item) => {
  if (item.action === 'compose') {
    emit('compose')
    return
  }
  router.push({ name: item.name })
}

const resetBrandClicks = () => {
  brandClickCount.value = 0
  if (brandClickResetTimer) window.clearTimeout(brandClickResetTimer)
  brandClickResetTimer = null
}

const handleBrandClick = () => {
  brandClickCount.value += 1
  if (brandClickResetTimer) window.clearTimeout(brandClickResetTimer)

  // 짧은 시간 안의 연속 로고 클릭만 이스터에그 진입 시도로 계산한다.
  if (brandClickCount.value >= 15) {
    resetBrandClicks()
    router.push({ name: 'easter-egg' })
    return
  }

  brandClickResetTimer = window.setTimeout(resetBrandClicks, 1800)
  if (route.name !== 'feed') router.push({ name: 'feed' })
}
</script>

<template>
  <header class="top-bar">
    <div class="top-bar__inner">
      <button class="brand-link" type="button" @click="handleBrandClick">
        <BrandLogo rotating size="small" />
        <span class="brand-type">Flex-Log</span>
      </button>

      <nav class="icon-nav" aria-label="주요 메뉴">
        <button
          v-for="item in navItems"
          :key="item.name"
          class="icon-nav__item"
          :class="{ active: isActive(item), compose: item.action === 'compose' }"
          type="button"
          :aria-label="item.label"
          @click="handleNav(item)"
        >
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path :d="item.icon" />
          </svg>
          <span>{{ item.label }}</span>
        </button>
      </nav>

      <div class="top-actions">
        <RouterLink class="profile-chip" :to="{ name: 'profile' }">
          <img
            v-if="profileImage"
            class="profile-chip__image"
            :src="profileImage"
            alt="profile image"
            @error="imageLoadFailed = true"
          >
          <span v-else>{{ userName.slice(0, 1).toUpperCase() }}</span>
          <strong>{{ userName }}</strong>
        </RouterLink>
        <button class="logout-button" type="button" @click="$emit('logout')">로그아웃</button>
        <button
          class="theme-toggle"
          type="button"
          :aria-pressed="isDarkMode"
          :aria-label="isDarkMode ? '라이트 모드로 전환' : '다크 모드로 전환'"
          @click="toggleTheme"
        >
          <span></span>
        </button>
      </div>
    </div>
  </header>
</template>

<style scoped>
.top-bar {
  position: sticky;
  top: 0;
  z-index: 70;
  border-bottom: 0;
  background: rgba(247, 239, 216, 0.76);
  backdrop-filter: blur(18px);
}

:global(html[data-theme='dark']) .top-bar {
  background: rgba(19, 22, 25, 0.78);
}

.top-bar__inner {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 22px;
  width: min(100% - 28px, 1180px);
  min-height: 78px;
  margin: 0 auto;
}

.brand-link {
  display: inline-flex;
  align-items: center;
  gap: 12px;
  min-width: 0;
  border: 0;
  background: transparent;
  color: var(--color-ink);
  padding: 0;
}

.brand-type {
  font-size: 26px;
  line-height: 1;
  text-shadow: 2px 2px 0 rgba(216, 165, 38, 0.45);
  white-space: nowrap;
}

.icon-nav {
  display: flex;
  justify-content: center;
  gap: 8px;
  min-width: 0;
}

.icon-nav__item {
  position: relative;
  display: grid;
  width: 58px;
  min-height: 54px;
  place-items: center;
  overflow: hidden;
  border: 2px solid transparent;
  border-radius: 999px;
  background: rgba(255, 248, 231, 0.34);
  color: var(--color-ink);
  padding: 7px 10px;
  transition: transform 0.18s ease, background 0.18s ease, border-color 0.18s ease;
}

.icon-nav__item svg {
  width: 24px;
  height: 24px;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 2;
  transition: transform 0.18s ease;
}

.icon-nav__item span {
  position: absolute;
  right: 9px;
  bottom: 4px;
  left: 9px;
  opacity: 0;
  color: var(--color-ink);
  font-size: 10px;
  font-weight: 900;
  line-height: 1;
  text-align: center;
  transform: translateY(10px);
  transition: opacity 0.18s ease, transform 0.18s ease;
}

.icon-nav__item:hover,
.icon-nav__item.active {
  border-color: var(--color-ink);
  background: var(--color-paper);
  box-shadow: 3px 3px 0 var(--color-ink);
  transform: translateY(-2px);
}

.icon-nav__item:hover svg,
.icon-nav__item.active svg {
  transform: translateY(-6px);
}

.icon-nav__item:hover span,
.icon-nav__item.active span {
  opacity: 1;
  transform: translateY(0);
}

.icon-nav__item.compose {
  background: var(--color-gold);
}

.top-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 10px;
  min-width: 0;
}

.profile-chip {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
  max-width: 190px;
  border: 0;
  border-radius: 999px;
  background: rgba(255, 248, 231, 0.56);
  padding: 5px 10px 5px 5px;
  font-weight: 900;
}

.profile-chip__image,
.profile-chip span {
  display: grid;
  width: 30px;
  height: 30px;
  place-items: center;
  border-radius: 50%;
  background: var(--color-money);
  color: var(--color-paper);
  font-weight: 900;
}

.profile-chip__image {
  object-fit: cover;
}

.profile-chip strong {
  overflow: hidden;
  font-size: 13px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.logout-button {
  border: 0;
  border-radius: 999px;
  background: rgba(255, 248, 231, 0.56);
  color: var(--color-ink);
  padding: 9px 13px;
  font-size: 12px;
  font-weight: 900;
}

.theme-toggle {
  position: relative;
  width: 54px;
  height: 30px;
  flex: 0 0 auto;
  border: 2px solid var(--color-ink);
  border-radius: 999px;
  background: var(--color-paper);
  padding: 2px;
  box-shadow: 2px 2px 0 var(--color-ink);
}

.theme-toggle span {
  display: block;
  width: 22px;
  height: 22px;
  border-radius: 50%;
  background: var(--color-gold);
  box-shadow: inset 0 0 0 2px rgba(23, 19, 13, 0.18);
  transition: transform 0.2s ease, background 0.2s ease;
}

.theme-toggle[aria-pressed='true'] span {
  background: var(--color-blue);
  transform: translateX(24px);
}

@media (max-width: 900px) {
  .top-bar__inner {
    grid-template-columns: 1fr auto;
    gap: 12px;
    min-height: 70px;
  }

  .brand-type {
    display: none;
  }

  .icon-nav {
    grid-column: 1 / -1;
    order: 3;
    justify-content: space-between;
    padding-bottom: 8px;
  }

  .icon-nav__item {
    width: 52px;
    min-height: 48px;
  }
}

@media (max-width: 560px) {
  .top-actions {
    gap: 6px;
  }

  .profile-chip strong,
  .logout-button {
    display: none;
  }
}
</style>
