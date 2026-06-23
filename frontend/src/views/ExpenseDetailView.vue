<script setup>
import { onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import { getExpense } from '../api/expenses'
import FeedCard from '../components/feed/FeedCard.vue'

const route = useRoute()
const log = ref(null)
const errorMessage = ref('')

onMounted(async () => {
  try {
    log.value = (await getExpense(route.params.id)).data
  } catch {
    errorMessage.value = '게시물을 불러오지 못했습니다.'
  }
})
</script>

<template>
  <section class="detail-wrap page-shell">
    <p v-if="errorMessage" class="state-card error">{{ errorMessage }}</p>
    <p v-else-if="!log" class="state-card">게시물을 불러오는 중입니다.</p>
    <template v-else>
      <FeedCard :log="log" />
      <div v-if="log.can_edit" class="owner-actions">
        <RouterLink class="vintage-button" :to="{ name: 'log-edit', params: { id: log.id } }">게시물 수정</RouterLink>
      </div>
    </template>
  </section>
</template>

<style scoped>
.detail-wrap {
  width: min(100%, 650px);
  margin: auto;
}

.owner-actions {
  display: flex;
  justify-content: center;
}
</style>
