<script setup>
import { computed, onMounted, ref } from 'vue'

import api from '../api/client'
import { getExpenses } from '../api/expenses'
import { formatAmount, formatDate } from '../utils/format'

const analysis = ref(null)
const aiLatest = ref(null)
const logs = ref([])
const isLoading = ref(false)
const errorMessage = ref('')

const topCategory = computed(() => analysis.value?.category_items?.[0]?.name || '-')
const recentLogs = computed(() => logs.value.slice(0, 8))
const riskLabel = computed(() => {
  if (!aiLatest.value) return '분석 전'
  if (aiLatest.value.risk_level === 'high') return '높음'
  if (aiLatest.value.risk_level === 'medium') return '보통'
  return '낮음'
})

const loadDashboard = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const [analysisResponse, logsResponse, aiResponse] = await Promise.allSettled([
      api.get('/api/v1/analysis/monthly/'),
      getExpenses(),
      api.get('/api/v1/analysis/monthly/latest/'),
    ])

    if (analysisResponse.status === 'fulfilled') analysis.value = analysisResponse.value.data
    if (logsResponse.status === 'fulfilled') logs.value = logsResponse.value.data
    if (aiResponse.status === 'fulfilled') aiLatest.value = aiResponse.value.data
  } catch {
    errorMessage.value = '마이페이지 정보를 불러오지 못했습니다.'
  } finally {
    isLoading.value = false
  }
}

onMounted(loadDashboard)
</script>

<template>
  <section class="mypage page-shell">
    <div class="section-head">
      <div>
        <h1>마이페이지</h1>
        <p>내 소비 기록과 분석 흐름을 한눈에 확인합니다.</p>
      </div>
      <div class="quick-links">
        <RouterLink class="btn btn-outline-dark" :to="{ name: 'profile' }">프로필</RouterLink>
        <RouterLink class="btn btn-outline-primary" :to="{ name: 'analysis' }">AI 분석</RouterLink>
        <RouterLink class="btn btn-outline-secondary" :to="{ name: 'finance-hub' }">금융</RouterLink>
      </div>
    </div>

    <div v-if="isLoading" class="state-card">불러오는 중입니다.</div>
    <p v-if="errorMessage" class="state-card error">{{ errorMessage }}</p>

    <div class="summary-grid">
      <article class="vintage-card">
        <span>이번 달 소비</span>
        <strong>{{ formatAmount(analysis?.total_amount) }}</strong>
      </article>
      <article class="vintage-card">
        <span>소비 기록</span>
        <strong>{{ analysis?.log_count || 0 }}건</strong>
      </article>
      <article class="vintage-card">
        <span>최다 카테고리</span>
        <strong>{{ topCategory }}</strong>
      </article>
      <article class="vintage-card">
        <span>소비 위험도</span>
        <strong>{{ riskLabel }}</strong>
      </article>
    </div>

    <div class="dashboard-layout">
      <section class="recent-panel vintage-card">
        <div class="panel-head">
          <h2>최근 소비 기록</h2>
          <RouterLink :to="{ name: 'logs' }">전체 보기</RouterLink>
        </div>
        <div class="recent-list">
          <div v-if="!recentLogs.length" class="mini-empty">아직 기록이 없습니다.</div>
          <article v-for="log in recentLogs" :key="log.id">
            <div>
              <span class="vintage-badge">{{ log.category_name }}</span>
              <strong>{{ log.product_name || log.content || '소비 기록' }}</strong>
              <small>{{ formatDate(log.created_at) }}</small>
            </div>
            <b>{{ formatAmount(log.amount) }}</b>
          </article>
        </div>
      </section>

      <aside class="ai-panel glass-panel">
        <h2>최근 AI 분석</h2>
        <template v-if="aiLatest">
          <p class="highlight">{{ aiLatest.summary }}</p>
          <p>{{ aiLatest.feedback }}</p>
          <RouterLink class="vintage-button" :to="{ name: 'analysis' }">자세히 보기</RouterLink>
        </template>
        <template v-else>
          <p>생성된 AI 분석이 없습니다.</p>
          <RouterLink class="vintage-button" :to="{ name: 'analysis' }">AI 분석 시작</RouterLink>
        </template>
      </aside>
    </div>
  </section>
</template>

<style scoped>
.mypage {
  display: grid;
  gap: 18px;
}

.quick-links {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.quick-links a,
.ai-panel .vintage-button {
  min-width: 104px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.summary-grid article {
  display: grid;
  gap: 7px;
  padding: 16px;
}

.summary-grid span {
  color: var(--color-muted);
  font-weight: 900;
}

.summary-grid strong {
  font-size: 24px;
}

.dashboard-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.25fr) minmax(300px, 0.75fr);
  gap: 18px;
}

.recent-panel,
.ai-panel {
  padding: 18px;
}

.panel-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.panel-head h2,
.ai-panel h2 {
  margin: 0;
  font-size: 23px;
}

.panel-head a {
  color: var(--color-dark-gold);
  font-weight: 900;
}

.recent-list {
  display: grid;
  gap: 10px;
  margin-top: 14px;
}

.recent-list article {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  border-radius: 16px;
  background: rgba(255, 248, 231, 0.72);
  padding: 12px;
}

.recent-list article > div {
  display: grid;
  gap: 4px;
}

.recent-list small,
.mini-empty,
.ai-panel p {
  color: var(--color-muted);
}

.highlight {
  color: var(--color-ink) !important;
  font-weight: 900;
}

@media (max-width: 900px) {
  .summary-grid,
  .dashboard-layout {
    grid-template-columns: 1fr;
  }
}
</style>
