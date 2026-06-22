<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { useAccountStore } from './stores/account'


const router = useRouter()
const route = useRoute()
const account = useAccountStore()

const displayName = computed(() => account.user?.name || account.user?.username || '')
const showChrome = computed(() => account.isAuthenticated)

const goBack = () => {
  if (window.history.length > 1) {
    router.back()
  } else {
    router.push({ name: 'feed' })
  }
}

const logout = async () => {
  account.logout()
  await router.push({ name: 'login' })
}
</script>

<template>
  <div class="app-shell">
    <header v-if="showChrome" class="top-bar">
      <button class="icon-button" type="button" aria-label="뒤로가기" @click="goBack">
        ‹
      </button>
      <RouterLink class="brand" :to="{ name: 'feed' }">Flex Log</RouterLink>
      <div class="top-actions">
        <span class="user-name">{{ displayName }}</span>
        <RouterLink class="primary-link" :to="{ name: 'log-create' }">기록</RouterLink>
        <button class="text-button" type="button" @click="logout">로그아웃</button>
      </div>
    </header>

    <main class="page-wrap" :class="{ 'with-bottom-nav': showChrome }">
      <RouterView />
    </main>

    <nav v-if="showChrome" class="bottom-nav" aria-label="주요 메뉴">
      <RouterLink :class="{ active: route.name === 'feed' }" :to="{ name: 'feed' }">피드</RouterLink>
      <RouterLink :class="{ active: route.name === 'logs' }" :to="{ name: 'logs' }">소비</RouterLink>
      <RouterLink :class="{ active: route.name === 'stocks' }" :to="{ name: 'stocks' }">주식</RouterLink>
      <RouterLink :class="{ active: route.name === 'friends' }" :to="{ name: 'friends' }">친구</RouterLink>
      <RouterLink :class="{ active: route.name === 'mypage' }" :to="{ name: 'mypage' }">마이</RouterLink>
    </nav>
  </div>
</template>
