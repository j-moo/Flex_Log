<script setup>
import { computed, onMounted, ref } from 'vue'

import api from '../api/client'


const latest = ref([])
const history = ref([])
const isLoading = ref(false)
const errorMessage = ref('')

const productTypeLabel = (type) => {
  if (type === 'deposit') return '정기예금'
  if (type === 'saving') return '정기적금'
  return '-'
}
const formatRate = (rate) => (rate === null || rate === undefined ? '-' : `${Number(rate).toFixed(2)}%`)
const formatDate = (value) => {
  if (!value) return ''
  return new Intl.DateTimeFormat('ko-KR', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(new Date(value))
}

const visibleHistory = computed(() => history.value.slice(0, 10))

const fetchRecommendations = async () => {
  errorMessage.value = ''
  const [latestResponse, historyResponse] = await Promise.all([
    api.get('/api/v1/finance/recommend/latest/'),
    api.get('/api/v1/finance/recommend/history/'),
  ])
  latest.value = latestResponse.data
  history.value = historyResponse.data
}

const requestRecommendation = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const response = await api.post('/api/v1/finance/recommend/')
    latest.value = response.data
    await fetchRecommendations()
  } catch {
    errorMessage.value = 'AI 금융상품 추천을 생성하지 못했습니다.'
  } finally {
    isLoading.value = false
  }
}

onMounted(async () => {
  try {
    await fetchRecommendations()
  } catch {
    errorMessage.value = '추천 결과를 불러오지 못했습니다.'
  }
})
</script>

<template>
  <section class="recommend-page">
    <div class="recommend-header">
      <div>
        <h1>AI 금융상품 추천</h1>
        <p>소비 분석 결과와 DB에 저장된 금융상품 후보를 바탕으로 참고용 추천을 생성합니다.</p>
      </div>
      <div class="header-actions">
        <RouterLink class="ghost-action" :to="{ name: 'finance-products' }">상품 목록</RouterLink>
        <button class="recommend-action" type="button" :disabled="isLoading" @click="requestRecommendation">
          {{ isLoading ? '추천 생성 중' : 'AI 추천 받기' }}
        </button>
      </div>
    </div>

    <div v-if="errorMessage" class="recommend-alert">{{ errorMessage }}</div>

    <div v-if="!latest.length" class="recommend-empty">
      아직 생성된 금융상품 추천이 없습니다.
    </div>

    <div v-else class="recommend-grid">
      <article v-for="item in latest" :key="item.id" class="recommend-card">
        <div class="card-top">
          <span>{{ productTypeLabel(item.product_type) }}</span>
          <strong>{{ formatRate(item.max_interest_rate || item.interest_rate) }}</strong>
        </div>
        <h2>{{ item.title }}</h2>
        <div class="product-line">
          <strong>{{ item.bank_name || '상품 데이터 없음' }}</strong>
          <span>{{ item.product_name || 'fixture 로드가 필요합니다' }}</span>
        </div>
        <div class="rate-strip">
          <span>{{ item.save_trm || '-' }}개월</span>
          <span>기본 {{ formatRate(item.interest_rate) }}</span>
          <span>최고 {{ formatRate(item.max_interest_rate) }}</span>
        </div>
        <p>{{ item.description }}</p>
        <div class="reason-box">
          <strong>추천 이유</strong>
          <span>{{ item.reason }}</span>
        </div>
        <div v-if="item.ai_comment" class="reason-box muted-box">
          <strong>AI 코멘트</strong>
          <span>{{ item.ai_comment }}</span>
        </div>
        <p class="caution">{{ item.caution }}</p>
      </article>
    </div>

    <section class="history-panel">
      <div class="panel-title">
        <h2>추천 이력</h2>
        <span>{{ history.length }}건</span>
      </div>
      <div v-if="!visibleHistory.length" class="history-empty">추천 이력이 없습니다.</div>
      <div v-for="item in visibleHistory" :key="`history-${item.id}`" class="history-row">
        <div>
          <strong>{{ item.title }}</strong>
          <span>{{ item.bank_name }} · {{ item.product_name }}</span>
        </div>
        <div>
          <strong>{{ formatRate(item.max_interest_rate || item.interest_rate) }}</strong>
          <span>{{ formatDate(item.created_at) }}</span>
        </div>
      </div>
    </section>
  </section>
</template>

<style scoped>
.recommend-page {
  min-height: calc(100vh - 120px);
  margin: -28px calc(50% - 50vw) -48px;
  padding: 32px max(20px, calc(50vw - 560px)) 56px;
  background: #0b0e11;
  color: #eaecef;
}

.recommend-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 20px;
}

.recommend-header h1 {
  margin: 0 0 8px;
  font-size: 28px;
  font-weight: 800;
}

.recommend-header p,
.product-line span,
.recommend-card p,
.history-row span,
.history-empty,
.recommend-empty {
  color: #707a8a;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.recommend-action,
.ghost-action {
  display: grid;
  place-items: center;
  min-height: 42px;
  padding: 0 16px;
  border: 0;
  border-radius: 8px;
  font-weight: 800;
}

.recommend-action {
  background: #fcd535;
  color: #0b0e11;
}

.recommend-action:disabled {
  opacity: 0.65;
}

.ghost-action {
  background: #2b3139;
  color: #eaecef;
}

.recommend-alert,
.recommend-empty,
.history-panel {
  padding: 16px;
  border: 1px solid #2b3139;
  border-radius: 8px;
  background: #1e2329;
}

.recommend-alert {
  border-color: #f6465d;
  color: #f6465d;
  margin-bottom: 16px;
}

.recommend-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.recommend-card {
  display: grid;
  gap: 14px;
  padding: 18px;
  border: 1px solid #2b3139;
  border-radius: 8px;
  background: #1e2329;
}

.card-top,
.rate-strip,
.panel-title,
.history-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.card-top span,
.panel-title span,
.rate-strip span {
  color: #fcd535;
  font-weight: 800;
}

.card-top strong {
  color: #fcd535;
  font-size: 24px;
}

.recommend-card h2,
.panel-title h2 {
  margin: 0;
  font-size: 18px;
}

.product-line,
.reason-box,
.history-row > div {
  display: grid;
  gap: 4px;
}

.rate-strip {
  flex-wrap: wrap;
  justify-content: flex-start;
}

.rate-strip span {
  padding: 6px 8px;
  border-radius: 6px;
  background: #2b3139;
}

.recommend-card p {
  margin: 0;
  line-height: 1.7;
}

.reason-box {
  padding: 12px;
  border-radius: 8px;
  background: #2b3139;
}

.reason-box strong {
  color: #fcd535;
}

.muted-box strong {
  color: #eaecef;
}

.caution {
  font-size: 13px;
}

.history-panel {
  display: grid;
  gap: 12px;
  margin-top: 14px;
}

.history-row {
  padding-top: 12px;
  border-top: 1px solid #2b3139;
}

.history-row > div:last-child {
  text-align: right;
}

.history-row > div:last-child strong {
  color: #fcd535;
}

@media (max-width: 1000px) {
  .recommend-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 620px) {
  .recommend-page {
    margin-top: -18px;
    padding: 24px 14px 40px;
  }

  .recommend-header,
  .header-actions,
  .history-row {
    align-items: stretch;
    flex-direction: column;
  }

  .history-row > div:last-child {
    text-align: left;
  }
}
</style>
