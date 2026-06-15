<script setup>
import { useAccountStore } from '../stores/account'


const account = useAccountStore()
</script>

<template>
  <section class="hero">
    <h1>Flex Log</h1>
    <p>
      사진과 함께 소비를 기록하고, 쌓인 기록을 바탕으로 소비 패턴을 확인하는 서비스입니다.
    </p>
    <div v-if="account.isAuthenticated" class="actions">
      <strong>{{ account.user?.username }}님, 환영합니다.</strong>
    </div>
    <div v-else class="actions">
      <RouterLink class="button" :to="{ name: 'signup' }">회원가입</RouterLink>
      <RouterLink class="button secondary" :to="{ name: 'login' }">로그인</RouterLink>
    </div>
  </section>
</template>
