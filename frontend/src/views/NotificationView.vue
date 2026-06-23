<script setup>
const groups = [
  {
    title: '하루',
    items: [
      { type: '좋아요', text: '민지가 오늘의 커피 기록을 좋아합니다.', time: '방금 전', tone: 'red' },
      { type: '댓글', text: '준호가 댓글을 남겼습니다.', time: '12분 전', tone: 'blue' },
    ],
  },
  {
    title: '이번 주',
    items: [
      { type: '친구 요청', text: '서연님이 친구 요청을 보냈습니다.', time: '2일 전', tone: 'green' },
      { type: '주가 변동', text: '삼성전자 mock 현재가가 2.1% 변동했습니다.', time: '3일 전', tone: 'gold' },
    ],
  },
  {
    title: '이번 달',
    items: [
      { type: 'AI 분석', text: '이번 달 소비 AI 분석 결과가 준비되었습니다.', time: '6일 전', tone: 'blue' },
      { type: '상품 추천', text: '소비 패턴 기반 예적금 추천이 갱신되었습니다.', time: '12일 전', tone: 'green' },
    ],
  },
  {
    title: '이전 알림',
    items: [
      { type: '댓글', text: '지난 피드에 새 댓글이 추가되었습니다.', time: '지난달', tone: 'red' },
    ],
  },
]
</script>

<template>
  <section class="notification-page page-shell">
    <div class="section-head">
      <div>
        <h1>알림</h1>
      </div>
    </div>

    <div class="timeline">
      <section v-for="group in groups" :key="group.title" class="timeline-group">
        <h2>{{ group.title }}</h2>
        <div class="notification-list">
          <article
            v-for="item in group.items"
            :key="`${group.title}-${item.text}`"
            class="notification-card glass-panel"
            :class="`tone-${item.tone}`"
          >
            <span>{{ item.type }}</span>
            <div>
              <strong>{{ item.text }}</strong>
              <small>{{ item.time }}</small>
            </div>
          </article>
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
  grid-template-columns: 92px 1fr;
  align-items: center;
  gap: 14px;
  padding: 14px;
  transition: transform 0.16s ease, box-shadow 0.16s ease;
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
  transform: translateY(-2px);
  box-shadow: 5px 5px 0 var(--color-ink);
}

.notification-card > span {
  border: 2px solid var(--color-ink);
  border-radius: 999px;
  background: var(--color-paper);
  padding: 6px 10px;
  text-align: center;
  font-size: 12px;
  font-weight: 900;
}

.notification-card strong {
  display: block;
}

.notification-card small {
  color: var(--color-muted);
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
    grid-template-columns: 1fr;
  }
}
</style>
