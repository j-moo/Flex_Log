<script setup>
import { computed, ref } from 'vue'

import { toggleExpenseLike } from '../../api/expenses'
import { formatAmount, formatDate, isVideo } from '../../utils/format'
import CommentSection from './CommentSection.vue'
import LikeButton from './LikeButton.vue'

const props = defineProps({
  log: {
    type: Object,
    required: true,
  },
})

const isLiking = ref(false)
const avatarImageFailed = ref(false)
const commentSection = ref(null)

const hasAvatarImage = computed(() => (
  Boolean(props.log.profile_image) && !avatarImageFailed.value
))

const overlayBoxes = computed(() => {
  const boxes = props.log.overlay_style?.boxes
  if (Array.isArray(boxes) && boxes.length) {
    return boxes.filter((box) => String(box.text || '').trim())
  }
  if (!props.log.overlay_text && props.log.amount === null) return []
  return [
    {
      id: 'legacy',
      text: props.log.overlay_text || '',
      x: Number(props.log.overlay_style?.x ?? 50),
      y: Number(props.log.overlay_style?.y ?? 50),
      fontSize: Number(props.log.overlay_style?.fontSize || 28),
      color: props.log.overlay_style?.color || '#fff8e7',
    },
  ]
})

const amountLabel = computed(() => formatAmount(props.log.amount))
const displayText = computed(() => props.log.content || props.log.title || '')

const boxStyle = (box) => ({
  left: `${Number(box.x ?? 50)}%`,
  top: `${Number(box.y ?? 50)}%`,
  color: box.color || '#fff8e7',
  fontSize: `${Number(box.fontSize || 28)}px`,
  transform: `translate(-50%, -50%) rotate(${Number(box.rotate || 0)}deg)`,
})

const toggleLike = async () => {
  if (isLiking.value) return
  isLiking.value = true
  try {
    const response = await toggleExpenseLike(props.log.id)
    props.log.is_liked = response.data.liked
    props.log.like_count = response.data.like_count
  } finally {
    isLiking.value = false
  }
}
</script>

<template>
  <article class="feed-card">
    <header class="post-header">
      <RouterLink class="post-user" :to="{ name: 'user-profile', params: { userId: log.user_id } }">
        <img
          v-if="hasAvatarImage"
          class="avatar"
          :src="log.profile_image"
          alt="profile image"
          @error="avatarImageFailed = true"
        >
        <span v-else class="avatar" aria-hidden="true"></span>
        <span>
          <strong>{{ log.display_name || log.username }}</strong>
          <small>{{ formatDate(log.created_at) }}</small>
        </span>
      </RouterLink>
      <span class="vintage-badge">{{ log.category_name || '소비' }}</span>
    </header>

    <div class="post-media" :class="{ 'has-media': log.media }">
      <video v-if="log.media && isVideo(log.media)" :src="log.media" controls playsinline></video>
      <img v-else-if="log.media" :src="log.media" :alt="log.title || '소비 기록 이미지'">
      <div v-else class="media-fallback">
        <span>{{ (log.category_name || 'F').slice(0, 1) }}</span>
        <p>{{ log.title || 'Flex-Log' }}</p>
      </div>

      <p
        v-for="box in overlayBoxes"
        :key="box.id"
        class="media-overlay"
        :style="boxStyle(box)"
      >
        {{ box.text }}
      </p>
    </div>

    <div class="post-body">
      <div class="post-actions">
        <LikeButton
          :liked="log.is_liked"
          :count="log.like_count"
          :disabled="isLiking"
          @toggle="toggleLike"
        />
        <button class="comment-icon" type="button" aria-label="댓글 보기" @click="commentSection?.toggle()">
          <svg viewBox="0 0 24 24" aria-hidden="true">
            <path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4Z" />
          </svg>
          <span>{{ log.comment_count }}</span>
        </button>
        <span class="amount">{{ amountLabel }}</span>
      </div>

      <p class="caption">
        <strong>{{ log.display_name || log.username }}</strong>
        <span v-if="displayText"> {{ displayText }}</span>
      </p>

      <p v-if="log.product_name || log.merchant" class="purchase-meta">
        {{ [log.product_name, log.merchant].filter(Boolean).join(' · ') }}
      </p>

      <CommentSection
        ref="commentSection"
        :log-id="log.id"
        :count="log.comment_count"
        @count-change="log.comment_count = $event"
      />
    </div>
  </article>
</template>

<style scoped>
.feed-card {
  overflow: hidden;
  border: 2px solid var(--color-ink);
  border-radius: 26px;
  background: var(--color-paper);
  box-shadow: 5px 5px 0 var(--color-ink);
}

.post-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  padding: 14px 16px;
}

.post-user {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.avatar {
  display: grid;
  width: 42px;
  height: 42px;
  flex: 0 0 auto;
  place-items: center;
  border: 2px solid var(--color-ink);
  border-radius: 50%;
  background: var(--color-money);
  color: var(--color-paper);
  font-weight: 900;
  object-fit: cover;
}

.post-user > span:last-child {
  display: grid;
  min-width: 0;
}

.post-user strong,
.post-user small {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.post-user small {
  color: var(--color-muted);
  font-size: 12px;
}

.post-media {
  position: relative;
  display: grid;
  aspect-ratio: 1 / 1;
  place-items: center;
  overflow: hidden;
  border-block: 2px solid var(--color-ink);
  background: #262017;
}

.post-media.has-media {
  aspect-ratio: auto;
}

.post-media img,
.post-media video {
  width: 100%;
  height: auto;
  object-fit: contain;
}

.post-media video {
  display: block;
  background: #262017;
}

.media-fallback {
  display: grid;
  justify-items: center;
  color: var(--color-paper);
}

.media-fallback span {
  display: grid;
  width: 82px;
  height: 82px;
  place-items: center;
  border: 2px solid var(--color-paper);
  border-radius: 50%;
  background: var(--color-money);
  font-size: 34px;
  font-weight: 900;
}

.media-fallback p {
  margin: 12px 0 0;
  font-weight: 900;
}

.media-overlay {
  position: absolute;
  max-width: 84%;
  margin: 0;
  font-weight: 900;
  line-height: 1.12;
  text-align: center;
  text-shadow: 2px 2px 0 var(--color-ink), 0 8px 24px rgba(0, 0, 0, 0.45);
  white-space: pre-wrap;
}

.post-body {
  display: grid;
  gap: 7px;
  padding: 12px 16px 16px;
}

.post-actions {
  display: flex;
  align-items: center;
  gap: 14px;
}

.comment-icon {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  border: 0;
  background: transparent;
  color: var(--color-ink);
  padding: 3px;
  font-weight: 900;
}

.comment-icon svg {
  width: 26px;
  height: 26px;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 1.9;
}

.amount {
  margin-left: auto;
  color: var(--color-dark-gold);
  font-size: 16px;
  font-weight: 900;
}

.caption {
  margin: 2px 0 0;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
}

.caption strong,
.caption b {
  margin-right: 5px;
}

.purchase-meta {
  margin: 0;
  color: var(--color-muted);
  font-size: 13px;
}

@media (min-width: 700px) {
  .post-media:not(.has-media) {
    aspect-ratio: 4 / 3;
  }
}
</style>
