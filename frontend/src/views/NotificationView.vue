<script setup>
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

import { useNotificationStore } from '../stores/notifications'


const router = useRouter()
const notifications = useNotificationStore()

const toneByType = {
  like: 'red',
  comment: 'blue',
  ai_analysis: 'blue',
  friend_request: 'green',
  stock_movement: 'gold',
  product_recommendation: 'green',
}

const startOfToday = () => {
  const date = new Date()
  date.setHours(0, 0, 0, 0)
  return date
}

const daysAgo = (days) => {
  const date = new Date()
  date.setDate(date.getDate() - days)
  date.setHours(0, 0, 0, 0)
  return date
}

const groupedNotifications = computed(() => {
  const today = startOfToday()
  const week = daysAgo(7)
  const month = daysAgo(30)
  const groups = [
    { title: '오늘', items: [] },
    { title: '이번 주', items: [] },
    { title: '이번 달', items: [] },
    { title: '이전 알림', items: [] },
  ]

  notifications.items.forEach((item) => {
    const createdAt = new Date(item.created_at)
    if (createdAt >= today) groups[0].items.push(item)
    else if (createdAt >= week) groups[1].items.push(item)
    else if (createdAt >= month) groups[2].items.push(item)
    else groups[3].items.push(item)
  })

  return groups.filter((group) => group.items.length)
})

const toneFor = (item) => toneByType[item.notification_type] || 'gold'

const relativeTime = (value) => {
  const diffSeconds = Math.max(0, Math.floor((Date.now() - new Date(value).getTime()) / 1000))
  if (diffSeconds < 60) return '방금 전'
  const diffMinutes = Math.floor(diffSeconds / 60)
  if (diffMinutes < 60) return `${diffMinutes}분 전`
  const diffHours = Math.floor(diffMinutes / 60)
  if (diffHours < 24) return `${diffHours}시간 전`
  const diffDays = Math.floor(diffHours / 24)
  if (diffDays < 7) return `${diffDays}일 전`
  return new Intl.DateTimeFormat('ko-KR', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(value))
}

const openNotification = async (item) => {
  let target = item
  try {
    if (!item.is_read) target = await notifications.markAsRead(item.id)
  } finally {
    if (target.target_route) {
      router.push({
        name: target.target_route,
        params: target.target_params || {},
        query: target.target_query || {},
      })
    }
  }
}

onMounted(() => {
  notifications.fetchNotifications().catch(() => {})
})
</script>

<template>
  <section class="notification-page page-shell">
    <div class="section-head">
      <div>
        <h1>알림</h1>
        <p>좋아요, 댓글, 친구 요청, AI 분석, 주가 변동, 상품 추천 알림을 확인합니다.</p>
      </div>
      <button
        v-if="notifications.unreadCount"
        class="read-all-button"
        type="button"
        @click="notifications.markAllAsRead"
      >
        모두 읽음
      </button>
    </div>

    <div v-if="notifications.isLoading" class="state-card">알림을 불러오는 중입니다.</div>
    <p v-else-if="notifications.errorMessage" class="state-card error">{{ notifications.errorMessage }}</p>
    <div v-else-if="!notifications.items.length" class="state-card">
      <div>
        <strong>아직 알림이 없습니다.</strong>
        <p>새 좋아요, 댓글, 친구 요청, 분석 결과가 생기면 여기에 표시됩니다.</p>
      </div>
    </div>

    <div v-else class="timeline">
      <section v-for="group in groupedNotifications" :key="group.title" class="timeline-group">
        <h2>{{ group.title }}</h2>
        <div class="notification-list">
          <button
            v-for="item in group.items"
            :key="item.id"
            class="notification-card glass-panel"
            :class="[`tone-${toneFor(item)}`, { unread: !item.is_read }]"
            type="button"
            @click="openNotification(item)"
          >
            <span class="type-badge">{{ item.type_label }}</span>
            <div>
              <strong>{{ item.title }}</strong>
              <p>{{ item.message }}</p>
              <small>{{ relativeTime(item.created_at) }}</small>
            </div>
            <i v-if="!item.is_read" class="read-dot" aria-label="읽지 않은 알림"></i>
          </button>
        </div>
      </section>
    </div>
  </section>
</template>

<style scoped>
.notification-page {
  width: min(100%, 900px);
  margin: 0 auto;
}

.read-all-button {
  border: 2px solid var(--color-ink);
  border-radius: 999px;
  background: var(--color-paper);
  color: var(--color-ink);
  padding: 9px 14px;
  font-size: 12px;
  font-weight: 900;
}

.read-all-button:hover {
  background: var(--color-money-light);
}

.timeline {
  display: grid;
  gap: 24px;
}

.timeline-group {
  position: relative;
  display: grid;
  gap: 12px;
  padding-left: 22px;
}

.timeline-group::before {
  position: absolute;
  top: 42px;
  bottom: 0;
  left: 5px;
  width: 3px;
  border-radius: 999px;
  background: rgba(23, 19, 13, 0.18);
  content: '';
}

.timeline-group h2 {
  margin: 0;
  font-size: 22px;
}

.notification-list {
  display: grid;
  gap: 12px;
}

.notification-card {
  position: relative;
  display: grid;
  grid-template-columns: 106px minmax(0, 1fr) 12px;
  align-items: center;
  gap: 14px;
  width: 100%;
  border: 1px solid rgba(23, 19, 13, 0.18);
  color: var(--color-ink);
  padding: 14px;
  text-align: left;
  transition: transform 0.16s ease, box-shadow 0.16s ease, border-color 0.16s ease;
}

.notification-card::before {
  position: absolute;
  left: -24px;
  width: 13px;
  height: 13px;
  border: 2px solid var(--color-ink);
  border-radius: 50%;
  background: var(--color-gold);
  content: '';
}

.notification-card:hover {
  border-color: var(--color-ink);
  box-shadow: 5px 5px 0 var(--color-ink);
  transform: translateY(-2px);
}

.notification-card.unread {
  border-color: var(--color-ink);
  background: rgba(255, 248, 231, 0.92);
}

.type-badge {
  border: 2px solid var(--color-ink);
  border-radius: 999px;
  background: var(--color-paper);
  padding: 6px 10px;
  text-align: center;
  font-size: 12px;
  font-weight: 900;
}

.notification-card strong,
.notification-card p,
.notification-card small {
  display: block;
  overflow-wrap: anywhere;
}

.notification-card p {
  margin: 3px 0;
  color: var(--color-muted);
  font-size: 14px;
  line-height: 1.45;
}

.notification-card small {
  color: var(--color-muted);
  font-size: 12px;
  font-weight: 900;
}

.read-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: var(--color-red);
  box-shadow: 0 0 0 3px rgba(182, 74, 53, 0.16);
}

.tone-red::before {
  background: var(--color-red);
}

.tone-green::before {
  background: var(--color-money);
}

.tone-blue::before {
  background: var(--color-blue);
}

.tone-gold::before {
  background: var(--color-gold);
}

@media (max-width: 560px) {
  .notification-card {
    grid-template-columns: 1fr 12px;
  }

  .type-badge {
    width: fit-content;
  }
}
</style>
