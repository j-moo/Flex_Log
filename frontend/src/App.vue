<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

import { useAccountStore } from './stores/account'


const router = useRouter()
const account = useAccountStore()

const displayName = computed(() => account.user?.name || account.user?.username || '')

const logout = async () => {
  account.logout()
  await router.push({ name: 'login' })
}
</script>

<template>
  <div class="app-shell">
    <nav class="navbar navbar-expand-lg bg-white border-bottom sticky-top">
      <div class="container-fluid px-3 px-lg-4">
        <RouterLink class="navbar-brand" :to="{ name: 'home' }">Flex Log</RouterLink>
        <button
          class="navbar-toggler"
          type="button"
          data-bs-toggle="collapse"
          data-bs-target="#mainNav"
          aria-controls="mainNav"
          aria-expanded="false"
          aria-label="메뉴 열기"
        >
          <span class="navbar-toggler-icon"></span>
        </button>

        <div id="mainNav" class="collapse navbar-collapse">
          <ul class="navbar-nav me-auto mb-2 mb-lg-0">
            <template v-if="account.isAuthenticated">
              <li class="nav-item">
                <RouterLink class="nav-link" :to="{ name: 'logs' }">내 로그</RouterLink>
              </li>
              <li class="nav-item">
                <RouterLink class="nav-link" :to="{ name: 'feed' }">친구 피드</RouterLink>
              </li>
              <li class="nav-item">
                <RouterLink class="nav-link" :to="{ name: 'analysis' }">월별 분석</RouterLink>
              </li>
              <li class="nav-item">
                <RouterLink class="nav-link" :to="{ name: 'finance-products' }">금융상품</RouterLink>
              </li>
              <li class="nav-item">
                <RouterLink class="nav-link" :to="{ name: 'finance-recommend' }">AI 추천</RouterLink>
              </li>
              <li class="nav-item">
                <RouterLink class="nav-link" :to="{ name: 'friends' }">친구</RouterLink>
              </li>
              <li class="nav-item">
                <RouterLink class="nav-link" :to="{ name: 'profile' }">프로필</RouterLink>
              </li>
            </template>
          </ul>

          <div v-if="account.isAuthenticated" class="d-flex align-items-center gap-2">
            <span class="text-secondary small">{{ displayName }}</span>
            <RouterLink class="btn btn-primary btn-sm" :to="{ name: 'log-create' }">로그 작성</RouterLink>
            <button class="btn btn-outline-secondary btn-sm" type="button" @click="logout">로그아웃</button>
          </div>
          <div v-else class="d-flex gap-2">
            <RouterLink class="btn btn-outline-secondary btn-sm" :to="{ name: 'login' }">로그인</RouterLink>
            <RouterLink class="btn btn-primary btn-sm" :to="{ name: 'signup' }">회원가입</RouterLink>
          </div>
        </div>
      </div>
    </nav>

    <main class="page-wrap">
      <RouterView />
    </main>
  </div>
</template>
