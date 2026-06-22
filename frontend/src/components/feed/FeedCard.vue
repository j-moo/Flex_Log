<script setup>
import { computed, ref } from 'vue'
import { toggleExpenseLike } from '../../api/expenses'
import { formatAmount, formatDate, isVideo } from '../../utils/format'
import CommentSection from './CommentSection.vue'
import LikeButton from './LikeButton.vue'

const props = defineProps({ log: { type: Object, required: true } })
const isLiking = ref(false)
const commentSection = ref(null)
const avatarLetter = computed(() => (props.log.display_name || props.log.username || '?').slice(0, 1).toUpperCase())
const savedOverlayStyle = computed(() => ({
  left: `${Number(props.log.overlay_style?.x ?? 50)}%`,
  top: `${Number(props.log.overlay_style?.y ?? 50)}%`,
  color: props.log.overlay_style?.color || '#fff',
  fontSize: `${Number(props.log.overlay_style?.fontSize || 25)}px`,
}))

const toggleLike = async () => {
  if (isLiking.value) return
  isLiking.value = true
  try {
    const response = await toggleExpenseLike(props.log.id)
    props.log.is_liked = response.data.liked
    props.log.like_count = response.data.like_count
  } finally { isLiking.value = false }
}
</script>

<template>
  <article class="feed-card">
    <header class="post-header">
      <RouterLink class="post-user" :to="{ name: 'user-profile', params: { userId: log.user_id } }">
        <span class="avatar">{{ avatarLetter }}</span>
        <span><strong>{{ log.display_name }}</strong><small>{{ formatDate(log.created_at) }}</small></span>
      </RouterLink>
      <span class="category-badge">{{ log.category_name }}</span>
    </header>

    <div class="post-media">
      <video v-if="log.media && isVideo(log.media)" :src="log.media" controls playsinline></video>
      <img v-else-if="log.media" :src="log.media" :alt="log.title || '소비 기록 이미지'">
      <div v-else class="media-fallback"><span>{{ log.category_name?.slice(0,1) }}</span><p>{{ log.title }}</p></div>
      <p v-if="log.overlay_text || log.amount" class="media-overlay" :style="savedOverlayStyle"><span v-if="log.overlay_text">{{ log.overlay_text }}</span><small v-if="log.amount !== null">{{ formatAmount(log.amount) }}</small></p>
    </div>

    <div class="post-body">
      <div class="post-actions">
        <LikeButton :liked="log.is_liked" :count="log.like_count" :disabled="isLiking" @toggle="toggleLike" />
        <button class="comment-icon" type="button" aria-label="댓글 보기/숨기기" @click="commentSection?.toggle()"><svg viewBox="0 0 24 24"><path d="M21 15a4 4 0 0 1-4 4H8l-5 3V7a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4Z"/></svg><span>{{ log.comment_count }}</span></button>
        <span class="amount">{{ formatAmount(log.amount) }}</span>
      </div>
      <p class="caption"><strong>{{ log.display_name }}</strong> <b v-if="log.title">{{ log.title }}</b><span v-if="log.content"> {{ log.content }}</span></p>
      <p v-if="log.product_name || log.merchant" class="purchase-meta">{{ [log.product_name, log.merchant].filter(Boolean).join(' · ') }}</p>
      <CommentSection ref="commentSection" :log-id="log.id" :count="log.comment_count" @count-change="log.comment_count = $event" />
    </div>
  </article>
</template>

<style scoped>
.feed-card{overflow:hidden;border:1px solid rgba(255,255,255,.82);border-radius:18px;background:rgba(255,255,255,.7);box-shadow:0 16px 45px rgba(75,139,194,.11);backdrop-filter:blur(18px)}.post-header{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:12px 14px}.post-user{display:flex;align-items:center;gap:10px;min-width:0;color:var(--ink)}.avatar{display:grid;width:38px;height:38px;flex:0 0 auto;place-items:center;border:1px solid #fff;border-radius:50%;background:linear-gradient(135deg,#bfe4ff,#4f8cff);box-shadow:0 0 0 2px #dceeff;color:white;font-weight:850}.post-user>span:last-child{display:grid;min-width:0}.post-user strong,.post-user small{overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.post-user strong{font-size:13px}.post-user small{color:var(--muted);font-size:11px}.category-badge{flex:0 0 auto;border-radius:999px;background:#e8f5ff;color:#357bc3;padding:5px 9px;font-size:11px;font-weight:750}.post-media{position:relative;display:grid;aspect-ratio:1/1;place-items:center;overflow:hidden;background:#edf7ff}.post-media img,.post-media video{width:100%;height:100%;object-fit:cover}.media-fallback{display:grid;justify-items:center;color:#6d7580}.media-fallback span{display:grid;width:74px;height:74px;place-items:center;border-radius:50%;background:rgba(255,255,255,.8);color:var(--accent);font-size:30px;font-weight:900;box-shadow:0 8px 35px rgba(79,140,255,.15)}.media-fallback p{font-weight:700}.media-overlay{position:absolute;display:grid;max-width:86%;transform:translate(-50%,-50%);font-weight:850;text-align:center;text-shadow:0 2px 12px #000;white-space:pre-wrap}.media-overlay small{font-size:.7em}.post-body{display:grid;gap:5px;padding:10px 14px 13px}.post-actions{display:flex;align-items:center;gap:13px}.comment-icon{display:inline-flex;align-items:center;gap:6px;margin:0;border:0;background:transparent;color:var(--ink);padding:3px}.comment-icon svg{width:25px;height:25px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}.comment-icon span{font-weight:750}.amount{margin-left:auto;font-size:15px;font-weight:850}.caption{margin:2px 0 0;font-size:13px;line-height:1.55;white-space:pre-wrap}.caption strong{margin-right:5px}.caption b{margin-right:3px}.purchase-meta{margin:0;color:var(--muted);font-size:12px}@media(min-width:640px){.feed-card{border-radius:20px}.post-media{aspect-ratio:4/3}}
</style>
