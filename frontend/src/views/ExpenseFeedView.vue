<script setup>
import { onMounted, ref } from 'vue'
import FeedCard from '../components/feed/FeedCard.vue'
import { getFriendFeed } from '../api/expenses'

const logs = ref([])
const isLoading = ref(true)
const errorMessage = ref('')

const loadFeed = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try { logs.value = (await getFriendFeed()).data }
  catch { errorMessage.value = '친구 피드를 불러오지 못했습니다.' }
  finally { isLoading.value = false }
}
onMounted(loadFeed)
</script>

<template>
  <section class="feed-page">
    <div class="feed-intro">
      <div><p>FRIENDS FEED</p><h1>친구들의 오늘 소비</h1></div>
      <RouterLink :to="{ name: 'log-create' }">새 기록</RouterLink>
    </div>
    <p v-if="errorMessage" class="state-card error">{{ errorMessage }}</p>
    <p v-else-if="isLoading" class="state-card">피드를 불러오는 중입니다.</p>
    <div v-else-if="logs.length" class="feed-stream"><FeedCard v-for="log in logs" :key="log.id" :log="log" /></div>
    <div v-else class="state-card empty"><strong>아직 친구 피드가 비어 있어요.</strong><p>프로필의 친구 수를 눌러 친구를 관리하거나 첫 소비 기록을 공유해보세요.</p><RouterLink :to="{ name: 'profile' }">프로필에서 친구 관리</RouterLink></div>
  </section>
</template>

<style scoped>
.feed-page{width:min(100%,620px);margin:auto}.feed-intro{display:flex;align-items:flex-end;justify-content:space-between;gap:12px;margin-bottom:18px}.feed-intro p{margin:0;color:var(--accent);font-size:10px;font-weight:850;letter-spacing:.14em}.feed-intro h1{margin:4px 0 0;font-size:23px}.feed-intro>a{border-radius:8px;background:var(--accent);color:white;padding:8px 13px;font-size:12px;font-weight:750}.feed-stream{display:grid;gap:20px}.state-card{border:1px solid var(--border);border-radius:14px;background:white;padding:34px 20px;color:var(--muted);text-align:center}.state-card.error{color:#d93025}.state-card p{margin:6px 0 14px}.state-card a{color:var(--accent);font-weight:800}
</style>
