<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'

import MainLayout from './layouts/MainLayout.vue'
import { useAccountStore } from './stores/account'

const router = useRouter()
const account = useAccountStore()

const showChrome = computed(() => account.isAuthenticated)
const routeKey = (route) => `${route.name}:${JSON.stringify(route.params)}`

const logout = async () => {
  await account.logout()
  await router.push({ name: 'login' })
}
</script>

<template>
  <MainLayout v-if="showChrome" @logout="logout">
    <RouterView v-slot="{ Component, route }">
      <Transition name="page" mode="out-in">
        <component :is="Component" :key="routeKey(route)" />
      </Transition>
    </RouterView>
  </MainLayout>

  <main v-else class="guest-layout">
    <RouterView v-slot="{ Component, route }">
      <Transition name="page" mode="out-in">
        <component :is="Component" :key="routeKey(route)" />
      </Transition>
    </RouterView>
  </main>
</template>
