<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

import MainLayout from './layouts/MainLayout.vue'
import { useAccountStore } from './stores/account'


const router = useRouter()
const account = useAccountStore()

const showChrome = computed(() => account.isAuthenticated)

const logout = async () => {
  await account.logout()
  await router.push({ name: 'login' })
}
</script>

<template>
  <MainLayout v-if="showChrome" @logout="logout">
    <RouterView />
  </MainLayout>
  <main v-else class="guest-layout">
      <RouterView />
  </main>
</template>
