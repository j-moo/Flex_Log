<script setup>
import { onMounted, ref } from 'vue'

import { searchYoutube } from '../api/financial'

const query = ref('주식 투자')
const videos = ref([])
const isLoading = ref(false)
const errorMessage = ref('')
const searched = ref(false)

const search = async () => {
  if (!query.value.trim()) return
  isLoading.value = true
  searched.value = true
  errorMessage.value = ''
  try {
    const response = await searchYoutube(query.value.trim())
    videos.value = response.data.videos || []
  } catch (error) {
    videos.value = []
    errorMessage.value = error.response?.data?.detail || '영상을 검색하지 못했습니다.'
  } finally {
    isLoading.value = false
  }
}

onMounted(search)
</script>

<template>
  <section class="video-page page-shell">
    <div class="section-head">
      <div>
        <h1>주식 정보 검색</h1>
        <p>YouTube 영상으로 관심 종목과 금융 정보를 빠르게 확인합니다.</p>
      </div>
      <RouterLink class="ghost-link" :to="{ name: 'finance-hub', query: { tab: 'stocks' } }">보유 현황</RouterLink>
    </div>

    <form class="search-bar glass-panel" @submit.prevent="search">
      <span>검색</span>
      <input v-model="query" type="search" placeholder="예: 삼성전자 전망, ETF 투자" required>
      <button class="vintage-button" type="submit" :disabled="isLoading">
        {{ isLoading ? '검색 중...' : '검색' }}
      </button>
    </form>

    <p v-if="errorMessage" class="state-card error">{{ errorMessage }}</p>
    <div v-if="isLoading" class="state-card">YouTube Data API에서 영상을 찾는 중입니다.</div>
    <div v-else-if="searched && !videos.length" class="state-card">검색 결과가 없습니다. 다른 키워드로 검색해보세요.</div>

    <TransitionGroup v-else name="feed-list" tag="div" class="video-grid">
      <RouterLink
        v-for="(video, index) in videos"
        :key="video.video_id"
        class="video-card vintage-card stagger-item"
        :style="{ '--delay': `${index * 70}ms` }"
        :to="{ name: 'youtube-detail', params: { videoId: video.video_id } }"
      >
        <img :src="video.thumbnail_url" :alt="video.title">
        <div class="video-meta">
          <span class="channel-avatar">{{ video.channel_title?.slice(0, 1) }}</span>
          <div>
            <strong>{{ video.title }}</strong>
            <p>{{ video.channel_title }}</p>
          </div>
        </div>
      </RouterLink>
    </TransitionGroup>
  </section>
</template>

<style scoped>
.video-page {
  display: grid;
  gap: 18px;
}

.ghost-link {
  border: 2px solid var(--color-ink);
  border-radius: 999px;
  background: rgba(255, 248, 231, 0.74);
  color: var(--color-ink);
  padding: 9px 14px;
  font-weight: 900;
}

.search-bar {
  display: grid;
  grid-template-columns: auto 1fr auto;
  align-items: center;
  gap: 10px;
  padding: 10px;
}

.search-bar span {
  color: var(--color-muted);
  font-weight: 900;
  padding-left: 8px;
}

.search-bar input {
  width: 100%;
  border: 0;
  border-radius: 999px;
  background: rgba(255, 248, 231, 0.78);
  outline: 0;
  padding: 12px 14px;
}

.video-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.video-card {
  overflow: hidden;
}

.video-card > img {
  width: 100%;
  aspect-ratio: 16 / 9;
  border-bottom: 2px solid var(--color-ink);
  object-fit: cover;
  background: #2c2419;
}

.video-meta {
  display: grid;
  grid-template-columns: 40px 1fr;
  gap: 10px;
  padding: 12px;
}

.video-meta strong {
  display: -webkit-box;
  overflow: hidden;
  -webkit-box-orient: vertical;
  -webkit-line-clamp: 2;
  line-height: 1.35;
}

.video-meta p {
  margin: 5px 0 0;
  color: var(--color-muted);
  font-size: 13px;
}

.channel-avatar {
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

.feed-list-enter-active,
.feed-list-leave-active {
  transition: opacity 0.22s ease, transform 0.22s ease;
}

.feed-list-enter-from,
.feed-list-leave-to {
  opacity: 0;
  transform: translateY(16px);
}

@media (max-width: 850px) {
  .video-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 560px) {
  .search-bar,
  .video-grid {
    grid-template-columns: 1fr;
  }
}
</style>
