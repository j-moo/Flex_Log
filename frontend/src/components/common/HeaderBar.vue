<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

defineEmits(['logout'])

const route = useRoute()
const router = useRouter()
const titles = {
  feed: '피드',
  'finance-hub': '금융',
  'finance-products': '금융상품',
  'finance-recommend': 'AI 추천',
  commodities: '금·은 시세',
  'youtube-search': '관심 영상',
  'youtube-detail': '영상',
  'nearby-banks': '주변 은행',
  'log-create': '새 소비기록',
  'log-edit': '소비기록 수정',
  'log-detail': '게시물',
  logs: '내 소비기록',
  friends: '친구',
  profile: '프로필',
  'user-profile': '프로필',
  mypage: '마이페이지',
  analysis: '소비 분석',
  stocks: '보유 주식',
}
const title = computed(() => titles[route.name] || 'Flex Log')
const canGoBack = computed(() => !['feed', 'finance-hub', 'log-create', 'friends', 'profile'].includes(route.name))

const goBack = () => {
  if (window.history.length > 1) router.back()
  else router.push({ name: 'feed' })
}
const menuItems = [
  { name: 'feed', label: '피드', matches: ['feed'] },
  { name: 'log-create', label: '기록', matches: ['log-create', 'log-edit', 'log-detail', 'logs'] },
  { name: 'finance-hub', label: '금융', matches: ['finance-hub','finance-products','finance-recommend','analysis','commodities','stocks','youtube-search','youtube-detail','nearby-banks'] },
  { name: 'profile', label: '프로필', matches: ['profile','user-profile','mypage'] },
]
</script>

<template>
  <header class="header-bar">
    <div class="header-inner">
      <div class="header-leading"><button v-if="canGoBack" class="header-icon" type="button" aria-label="뒤로가기" @click="goBack"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="m15 18-6-6 6-6" /></svg></button><RouterLink v-else class="wordmark" :to="{ name: 'feed' }">Flex Log</RouterLink></div>
      <h1>{{ title }}</h1>
      <nav class="top-navigation" aria-label="주요 메뉴"><RouterLink v-for="item in menuItems" :key="item.name" :to="{name:item.name}" :class="{active:item.matches.includes(route.name)}">{{ item.label }}</RouterLink></nav>
      <div class="header-actions">
        <button class="header-icon logout-icon" type="button" aria-label="로그아웃" @click="$emit('logout')">
          <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M10 17l5-5-5-5M15 12H3M14 3h6v18h-6"/></svg>
        </button>
      </div>
    </div>
  </header>
</template>

<style scoped>
.header-bar{position:sticky;top:0;z-index:50;height:64px;border-bottom:1px solid rgba(255,255,255,.72);background:rgba(245,251,255,.78);box-shadow:0 7px 28px rgba(91,151,205,.08);backdrop-filter:blur(20px)}.header-inner{display:grid;grid-template-columns:auto auto 1fr auto;align-items:center;gap:18px;width:min(100% - 24px,1080px);height:100%;margin:auto}.header-leading{display:flex;align-items:center;min-width:85px}.header-inner>h1{margin:0;color:var(--ink);font-size:15px;font-weight:750;white-space:nowrap}.top-navigation{display:flex;justify-content:center;gap:4px;background:transparent;padding:0}.top-navigation a{border-radius:10px;color:var(--muted);padding:8px 12px;font-size:12px;font-weight:700}.top-navigation a:hover,.top-navigation a.active{background:rgba(255,255,255,.78);color:var(--accent);box-shadow:0 4px 14px rgba(79,140,255,.09)}.header-icon{display:grid;width:36px;height:36px;place-items:center;border:0;border-radius:50%;background:transparent;color:var(--ink);padding:7px}.header-icon:hover{background:rgba(255,255,255,.72)}.header-icon svg{width:22px;height:22px;fill:none;stroke:currentColor;stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round}.wordmark{color:#2f76c9;font-family:Georgia,serif;font-size:20px;font-style:italic;font-weight:800}.header-actions{display:flex;justify-self:end}.logout-icon{display:grid}@media(max-width:720px){.header-inner{grid-template-columns:auto 1fr auto;gap:7px}.header-inner>h1{display:none}.header-leading{min-width:36px}.wordmark{display:none}.top-navigation{justify-content:space-around;min-width:0}.top-navigation a{padding:8px 9px;font-size:11px}.logout-icon{width:32px;height:32px}}@media(max-width:390px){.top-navigation a{padding-inline:6px;font-size:10px}}
</style>
