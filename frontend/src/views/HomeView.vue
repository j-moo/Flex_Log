<script setup>
import { useAccountStore } from '@/stores/account'

const accountStore = useAccountStore()
</script>

<template>
  <div>
    <h2>Flex-Log Home</h2>

    <div v-if="accountStore.isAuthenticated">
      <h3>로그인 상태 ✅</h3>

      <p>
        Access Token 존재:
        {{ accountStore.accessToken ? 'O' : 'X' }}
      </p>

      <h4>내 정보</h4>

      <pre>
{{ accountStore.user }}
      </pre>

      <button @click="accountStore.logout">
        로그아웃
      </button>
    </div>

    <div v-else>
      <h3>로그인되지 않음 ❌</h3>
    </div>
  </div>
</template>