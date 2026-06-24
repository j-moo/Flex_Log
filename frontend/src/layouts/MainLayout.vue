<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import FeedComposerModal from '../components/feed/FeedComposerModal.vue'
import TopBar from '../components/common/TopBar.vue'

defineEmits(['logout'])

const route = useRoute()
const router = useRouter()

const composeId = computed(() => {
  if (route.query.composeEdit) return route.query.composeEdit
  if (route.name === 'log-edit') return route.params.id
  return null
})
const isComposeRoute = computed(() => ['log-create', 'log-edit'].includes(route.name))
const showComposer = computed(() => route.query.compose === '1' || isComposeRoute.value)

const openComposer = () => {
  router.push({ query: { ...route.query, compose: '1' } })
}

const closeComposer = () => {
  if (isComposeRoute.value) {
    router.push({ name: 'feed' })
    return
  }
  const nextQuery = { ...route.query }
  delete nextQuery.compose
  delete nextQuery.composeEdit
  router.push({ query: nextQuery })
}

const handleComposerSaved = () => {
  window.dispatchEvent(new CustomEvent('flexlog:feed-saved'))
  closeComposer()
}
</script>

<template>
  <div class="main-layout">
    <TopBar @logout="$emit('logout')" @compose="openComposer" />
    <main class="layout-content">
      <slot />
    </main>
    <FeedComposerModal
      v-if="showComposer"
      :edit-id="composeId"
      @close="closeComposer"
      @saved="handleComposerSaved"
    />
  </div>
</template>

<style scoped>
.main-layout {
  min-height: 100vh;
}

.layout-content {
  width: min(100% - 28px, 1160px);
  margin: 0 auto;
  padding: 28px 0 62px;
}

@media (max-width: 900px) {
  .layout-content {
    padding-top: 20px;
  }
}
</style>
