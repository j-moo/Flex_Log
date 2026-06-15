<script setup>
import { useRouter } from 'vue-router'

import { useAccountStore } from './stores/account'


const router = useRouter()
const account = useAccountStore()

const logout = async () => {
  account.logout()
  await router.push({ name: 'login' })
}
</script>

<template>
  <header class="site-header">
    <nav class="nav container">
      <RouterLink class="brand" :to="{ name: 'home' }">Flex Log</RouterLink>
      <div class="nav-links">
        <template v-if="account.isAuthenticated">
          <RouterLink :to="{ name: 'log-create' }">로그 작성</RouterLink>
          <RouterLink :to="{ name: 'logs' }">내 로그</RouterLink>
          <RouterLink :to="{ name: 'profile' }">프로필</RouterLink>
          <span class="user-name">{{ account.user?.username }}</span>
          <button class="button secondary" type="button" @click="logout">로그아웃</button>
        </template>
        <template v-else>
          <RouterLink :to="{ name: 'signup' }">회원가입</RouterLink>
          <RouterLink :to="{ name: 'login' }">로그인</RouterLink>
        </template>
      </div>
    </nav>
  </header>

  <main class="container page">
    <RouterView />
  </main>
</template>
