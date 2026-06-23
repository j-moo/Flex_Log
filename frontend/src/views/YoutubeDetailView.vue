<script setup>
import { onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'

import { getYoutubeVideo } from '../api/financial'

const route = useRoute()
const video = ref(null)
const errorMessage = ref('')
const isLoading = ref(false)

const load = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    video.value = (await getYoutubeVideo(route.params.videoId)).data
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '영상 정보를 불러오지 못했습니다.'
  } finally {
    isLoading.value = false
  }
}

watch(() => route.params.videoId, load)
onMounted(load)
</script>

<template>
  <section class="detail-page page-shell">
    <RouterLink class="back-link" :to="{ name: 'finance-hub', query: { tab: 'stock-search' } }">
      검색 결과로 돌아가기
    </RouterLink>

    <p v-if="errorMessage" class="state-card error">{{ errorMessage }}</p>
    <p v-else-if="isLoading" class="state-card">영상 정보를 불러오는 중입니다.</p>

    <article v-else-if="video" class="video-post vintage-card">
      <header>
        <span class="avatar">{{ video.channel_title?.slice(0, 1) }}</span>
        <div>
          <strong>{{ video.channel_title }}</strong>
          <small>{{ video.published_at?.slice(0, 10) }}</small>
        </div>
      </header>

      <div class="player">
        <iframe
          :src="`https://www.youtube.com/embed/${video.video_id}`"
          :title="video.title"
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
          allowfullscreen
        ></iframe>
      </div>

      <div class="caption">
        <h1>{{ video.title }}</h1>
        <p>{{ video.description }}</p>
        <small>조회수 {{ Number(video.statistics?.viewCount || 0).toLocaleString('ko-KR') }}회</small>
      </div>
    </article>
  </section>
</template>

<style scoped>
.detail-page {
  width: min(100%, 860px);
  margin: auto;
}

.back-link {
  display: inline-block;
  color: var(--color-dark-gold);
  font-weight: 900;
}

.video-post {
  overflow: hidden;
}

.video-post header {
  display: flex;
  align-items: center;
  gap: 10px;
  border-bottom: 2px solid var(--color-ink);
  padding: 14px;
}

.video-post header div {
  display: grid;
}

.video-post small {
  color: var(--color-muted);
}

.avatar {
  display: grid;
  width: 40px;
  height: 40px;
  place-items: center;
  border: 2px solid var(--color-ink);
  border-radius: 50%;
  background: var(--color-red);
  color: var(--color-paper);
  font-weight: 900;
}

.player {
  aspect-ratio: 16 / 9;
  background: #000;
}

.player iframe {
  width: 100%;
  height: 100%;
  border: 0;
}

.caption {
  padding: 18px;
}

.caption h1 {
  margin: 0 0 10px;
  font-size: 24px;
}

.caption p {
  color: var(--color-muted);
  white-space: pre-wrap;
}
</style>
