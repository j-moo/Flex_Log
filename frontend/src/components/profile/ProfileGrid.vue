<script setup>
import { isVideo } from '../../utils/format'

defineProps({
  logs: {
    type: Array,
    default: () => [],
  },
  isOwn: Boolean,
})

const icons = {
  식비: '밥',
  카페: '커피',
  교통: '길',
  쇼핑: '쇼핑',
  문화: '문화',
  주거: '집',
}
</script>

<template>
  <div v-if="logs.length" class="profile-post-grid">
    <RouterLink
      v-for="log in logs"
      :key="log.id"
      class="post-preview"
      :to="{ name: 'log-detail', params: { id: log.id } }"
    >
      <video v-if="log.media && isVideo(log.media)" :src="log.media" muted></video>
      <img v-else-if="log.media" :src="log.media" :alt="log.title">
      <div v-else class="grid-fallback">
        <span>{{ icons[log.category_name] || '기록' }}</span>
        <strong>{{ log.category_name }}</strong>
      </div>
      <div class="grid-overlay">
        <span>좋아요 {{ log.like_count }}</span>
        <span>댓글 {{ log.comment_count }}</span>
      </div>
    </RouterLink>
  </div>

  <RouterLink v-else-if="isOwn" class="empty-grid glass-panel empty-link" :to="{ name: 'log-create' }">
    <span>+</span>
    <strong>게시글 없음</strong>
    <p>소비 순간을 첫 게시글로 남겨보세요.</p>
  </RouterLink>

  <div v-else class="empty-grid glass-panel compact">
    <strong>게시글 없음</strong>
  </div>
</template>

<style scoped>
.profile-post-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 6px;
}

.post-preview {
  position: relative;
  display: grid;
  aspect-ratio: 1;
  place-items: center;
  overflow: hidden;
  border: 2px solid var(--color-ink);
  border-radius: 18px;
  background: var(--color-paper);
}

.profile-post-grid img,
.profile-post-grid video {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.grid-fallback {
  display: grid;
  justify-items: center;
  gap: 6px;
  color: var(--color-muted);
}

.grid-fallback span {
  font-weight: 900;
}

.grid-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  background: rgba(23, 19, 13, 0.56);
  color: var(--color-paper);
  opacity: 0;
  font-size: 12px;
  font-weight: 900;
  transition: opacity 0.16s ease;
}

.post-preview:hover .grid-overlay {
  opacity: 1;
}

.empty-grid {
  display: grid;
  min-height: 240px;
  place-content: center;
  justify-items: center;
  color: var(--color-ink);
  text-align: center;
}

.empty-link {
  transition: transform 0.16s ease, box-shadow 0.16s ease;
}

.empty-link:hover {
  transform: translateY(-2px);
}

.empty-grid.compact {
  min-height: 120px;
}

.empty-grid.compact strong {
  margin-top: 0;
}

.empty-grid > span {
  display: grid;
  width: 56px;
  height: 56px;
  place-items: center;
  border: 2px solid var(--color-ink);
  border-radius: 50%;
  background: var(--color-gold);
  font-size: 28px;
  font-weight: 900;
}

.empty-grid strong {
  margin-top: 12px;
}

.empty-grid p {
  margin: 4px 0;
  color: var(--color-muted);
}
</style>
