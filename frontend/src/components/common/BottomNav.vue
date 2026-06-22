<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()
const items = [
  { name: 'feed', label: '피드', match: ['feed'], path: 'M3 11.5 12 4l9 7.5V21h-6v-6H9v6H3z' },
  { name: 'finance-hub', label: '금융', match: ['finance-hub','finance-products','finance-recommend','commodities','youtube-search','youtube-detail','nearby-banks','stocks','analysis'], path: 'M4 20V10m5 10V4m6 16v-7m5 7V7' },
  { name: 'log-create', label: '기록', match: ['log-create'], create: true, path: 'M12 5v14M5 12h14' },
  { name: 'friends', label: '친구', match: ['friends'], path: 'M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2m7-10a4 4 0 1 0 0-8 4 4 0 0 0 0 8m13 10v-2a4 4 0 0 0-3-3.87m-2-12a4 4 0 0 1 0 7.75' },
  { name: 'profile', label: '프로필', match: ['profile','user-profile','mypage','logs','log-edit','log-detail'], path: 'M20 21a8 8 0 0 0-16 0m8-9a4 4 0 1 0 0-8 4 4 0 0 0 0 8' },
]
const activeName = computed(() => route.name)
</script>

<template>
  <nav class="bottom-navigation" aria-label="주요 메뉴">
    <RouterLink v-for="item in items" :key="item.name" :to="{ name: item.name }" :class="{ active: item.match.includes(activeName), create: item.create }">
      <span class="nav-icon"><svg viewBox="0 0 24 24" aria-hidden="true"><path :d="item.path" /></svg></span>
      <span>{{ item.label }}</span>
    </RouterLink>
  </nav>
</template>

<style scoped>
.bottom-navigation{position:fixed;right:0;bottom:0;left:0;z-index:60;display:grid;grid-template-columns:repeat(5,1fr);height:66px;margin:0;padding:0 max(10px,env(safe-area-inset-right)) env(safe-area-inset-bottom) max(10px,env(safe-area-inset-left));border-top:1px solid var(--border);background:rgba(255,255,255,.97);box-shadow:0 -4px 18px rgba(0,0,0,.03)}.bottom-navigation a{display:grid;align-content:center;justify-items:center;gap:2px;color:var(--muted);font-size:10px;font-weight:650}.bottom-navigation a.active{color:var(--ink)}.nav-icon{display:grid;width:29px;height:29px;place-items:center}.nav-icon svg{width:24px;height:24px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}.create .nav-icon{width:34px;height:27px;border-radius:9px;background:var(--accent);color:#fff}.create.active .nav-icon{box-shadow:0 0 0 3px var(--accent-soft)}@media(min-width:760px){.bottom-navigation{left:50%;bottom:18px;width:520px;height:62px;transform:translateX(-50%);border:1px solid var(--border);border-radius:18px;padding:0 8px;box-shadow:0 8px 28px rgba(0,0,0,.09)}}
</style>
