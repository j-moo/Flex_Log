<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { getYoutubeVideo } from '../api/financial'

const route = useRoute()
const video = ref(null)
const errorMessage = ref('')
const load = async () => {
  errorMessage.value = ''
  try { video.value = (await getYoutubeVideo(route.params.videoId)).data }
  catch (error) { errorMessage.value = error.response?.data?.detail || '영상 정보를 불러오지 못했습니다.' }
}
watch(() => route.params.videoId, load)
onMounted(load)
</script>

<template>
  <section class="detail-page">
    <RouterLink class="back-link" :to="{ name: 'youtube-search' }">‹ 검색 결과로</RouterLink>
    <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
    <article v-else-if="video" class="surface video-post">
      <header><span class="avatar">{{ video.channel_title?.slice(0,1) }}</span><div><strong>{{ video.channel_title }}</strong><small>{{ video.published_at?.slice(0,10) }}</small></div></header>
      <div class="player"><iframe :src="`https://www.youtube.com/embed/${video.video_id}`" :title="video.title" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe></div>
      <div class="post-actions"><span>♡</span><span>◯</span><a :href="`https://www.youtube.com/watch?v=${video.video_id}`" target="_blank" rel="noopener">↗</a></div>
      <div class="caption"><h1>{{ video.title }}</h1><p>{{ video.description }}</p><small>조회수 {{ Number(video.statistics?.viewCount || 0).toLocaleString() }}회</small></div>
    </article>
  </section>
</template>

<style scoped>
.detail-page{width:min(100%,820px);margin:auto}.back-link{display:inline-block;margin-bottom:14px;color:#737373;font-weight:800}.video-post{overflow:hidden}.video-post header{display:flex;align-items:center;gap:10px;padding:13px}.video-post header div{display:grid}.video-post small{color:#737373}.avatar{display:grid;width:38px;height:38px;place-items:center;border-radius:50%;background:linear-gradient(135deg,#833ab4,#fd1d1d,#fcb045);color:white;font-weight:900}.player{aspect-ratio:16/9;background:#000}.player iframe{width:100%;height:100%;border:0}.post-actions{display:flex;gap:16px;padding:14px;font-size:26px}.caption{padding:0 14px 18px}.caption h1{font-size:20px}.caption p{color:#525252;white-space:pre-wrap}.caption small{color:#737373}
</style>
