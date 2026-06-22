<script setup>
import { onMounted, ref } from 'vue'
import { searchYoutube } from '../api/financial'

const query = ref('재테크')
const videos = ref([])
const isLoading = ref(false)
const errorMessage = ref('')

const search = async () => {
  if (!query.value.trim()) return
  isLoading.value = true
  errorMessage.value = ''
  try {
    const response = await searchYoutube(query.value.trim())
    videos.value = response.data.videos
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '영상을 검색하지 못했습니다.'
  } finally { isLoading.value = false }
}
onMounted(search)
</script>

<template>
  <section class="video-page">
    <div class="section-head"><div><h1>관심 종목 영상</h1><p>YouTube에서 금융·종목 콘텐츠를 찾아봅니다.</p></div><RouterLink class="btn btn-outline-dark" :to="{ name: 'finance-hub' }">금융 홈</RouterLink></div>
    <form class="search-bar surface" @submit.prevent="search"><span>⌕</span><input v-model="query" type="search" placeholder="종목명 또는 금융 키워드" required><button type="submit" :disabled="isLoading">검색</button></form>
    <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
    <div v-if="isLoading" class="surface grid-empty">검색 중입니다.</div>
    <div v-else-if="!videos.length" class="surface grid-empty">검색 결과가 없습니다.</div>
    <div v-else class="video-grid">
      <RouterLink v-for="video in videos" :key="video.video_id" class="video-card surface" :to="{ name: 'youtube-detail', params: { videoId: video.video_id } }">
        <img :src="video.thumbnail_url" :alt="video.title"><div class="video-meta"><span class="channel-avatar">{{ video.channel_title?.slice(0, 1) }}</span><div><strong>{{ video.title }}</strong><p>{{ video.channel_title }}</p></div></div>
      </RouterLink>
    </div>
  </section>
</template>

<style scoped>
.video-page{width:min(100%,960px);margin:auto}.search-bar{display:grid;grid-template-columns:auto 1fr auto;align-items:center;gap:10px;padding:8px 10px;margin-bottom:20px}.search-bar span{font-size:25px}.search-bar input{width:100%;max-width:none;margin:0;border:0;outline:0;padding:10px}.search-bar button{margin:0;border:0;background:#0095f6;color:white;border-radius:8px;padding:10px 18px;font-weight:800}.video-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:16px}.video-card{overflow:hidden}.video-card>img{width:100%;aspect-ratio:16/9;object-fit:cover;background:#eee}.video-meta{display:grid;grid-template-columns:38px 1fr;gap:10px;padding:12px}.video-meta strong{display:-webkit-box;overflow:hidden;-webkit-line-clamp:2;-webkit-box-orient:vertical;line-height:1.35}.video-meta p{margin:5px 0 0;color:#737373;font-size:13px}.channel-avatar{display:grid;width:38px;height:38px;place-items:center;border-radius:50%;background:linear-gradient(135deg,#833ab4,#fd1d1d,#fcb045);color:white;font-weight:900}@media(max-width:800px){.video-grid{grid-template-columns:repeat(2,1fr)}}@media(max-width:520px){.video-grid{grid-template-columns:1fr}}
</style>
