<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import api from '../api/client'
import { joinProduct } from '../api/financial'
import { formatDate, formatRate } from '../utils/format'

const route = useRoute()
const latest = ref([])
const history = ref([])
const isLoading = ref(false)
const joiningOptionId = ref(null)
const errorMessage = ref('')
const actionMessage = ref('')

const cautionText = '본 추천은 참고용이며, 실제 가입 전 금융회사 공식 정보를 확인해야 합니다.'
const visibleHistory = computed(() => history.value.slice(0, 10))

const productTypeLabel = (type) => {
  if (type === 'deposit') return '정기예금'
  if (type === 'saving') return '정기적금'
  return '금융상품'
}

const displayTitle = (item) => item.product_name || item.title || '추천 상품'
const displayDescription = (item) => {
  if (item.product_name && item.description?.includes(item.product_name)) {
    return item.description.replace(item.product_name, '').trim()
  }
  return item.description
}

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
  actionMessage.value = ''
  try {
    latest.value = (await api.post('/api/v1/finance/recommend/')).data
    await fetchRecommendations()
  } catch {
    errorMessage.value = 'AI 추천을 불러오지 못했습니다. 소비 분석 데이터가 부족하거나 금융상품 데이터가 없을 수 있습니다.'
  } finally {
    isLoading.value = false
  }
}

const subscribeRecommendation = async (item) => {
  if (!item.option_id) {
    actionMessage.value = '가입 가능한 상품 옵션 정보가 없습니다.'
    return
  }
  joiningOptionId.value = item.option_id
  actionMessage.value = ''
  errorMessage.value = ''
  try {
    await joinProduct(item.option_id)
    actionMessage.value = `${displayTitle(item)} 상품에 가입했습니다.`
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '상품 가입에 실패했습니다.'
  } finally {
    joiningOptionId.value = null
  }
}

onMounted(async () => {
  try {
    if (route.query.auto === '1') await requestRecommendation()
    else await fetchRecommendations()
  } catch {
    errorMessage.value = '추천 결과를 불러오지 못했습니다.'
  }
})
</script>

<template>
  <section class="recommend-page page-shell">
    <div class="section-head">
      <div>
        <h1>AI 예적금 추천</h1>
        <p>소비 분석 결과와 금융상품 데이터를 바탕으로 예적금 추천을 생성합니다.</p>
      </div>
      <button class="vintage-button" type="button" :disabled="isLoading" @click="requestRecommendation">
        {{ isLoading ? 'AI가 분석 중입니다...' : 'AI 추천 다시 받기' }}
      </button>
    </div>

    <p v-if="actionMessage" class="notice-card">{{ actionMessage }}</p>
    <p v-if="errorMessage" class="state-card error">{{ errorMessage }}</p>

    <section v-if="isLoading" class="loading-card vintage-card">
      <span></span>
      <strong>AI가 소비 패턴과 금융상품을 분석 중입니다...</strong>
      <p>최근 소비 분석과 예적금 상품 조건을 함께 확인하고 있습니다.</p>
    </section>

    <div v-if="!latest.length && !isLoading" class="state-card">
      아직 생성된 예적금 추천이 없습니다.
    </div>

    <TransitionGroup v-else name="recommend-list" tag="div" class="recommend-grid">
      <article
        v-for="(item, index) in latest"
        :key="item.id"
        class="recommend-card vintage-card"
        :style="{ '--delay': `${index * 90}ms` }"
      >
        <div class="recommend-top">
          <span class="vintage-badge">{{ productTypeLabel(item.product_type) }}</span>
          <strong>{{ formatRate(item.max_interest_rate || item.interest_rate) }}</strong>
        </div>

        <h2>{{ displayTitle(item) }}</h2>
        <p v-if="displayDescription(item)" class="description">{{ displayDescription(item) }}</p>

        <div class="bank-box">
          <strong>{{ item.bank_name || '은행 정보 없음' }}</strong>
          <small>
            {{ item.save_trm || '-' }}개월 · 기본 {{ formatRate(item.interest_rate) }} · 최고
            {{ formatRate(item.max_interest_rate || item.interest_rate) }}
          </small>
        </div>

        <div class="reason-box">
          <strong>추천 이유</strong>
          <p>{{ item.reason }}</p>
        </div>

        <div class="comment-box">
          <strong>AI 코멘트</strong>
          <p>{{ item.ai_comment || '가입 전 우대조건과 중도해지 조건을 확인하세요.' }}</p>
        </div>

        <button
          class="vintage-button join-button"
          type="button"
          :disabled="!item.option_id || joiningOptionId === item.option_id"
          @click="subscribeRecommendation(item)"
        >
          {{ item.option_id ? (joiningOptionId === item.option_id ? '가입 처리 중' : '상품 가입') : '가입 옵션 없음' }}
        </button>

        <p class="caution">{{ item.caution || cautionText }}</p>
      </article>
    </TransitionGroup>

    <section class="history-panel glass-panel">
      <div class="history-head">
        <h2>추천 이력</h2>
        <span>{{ history.length }}건</span>
      </div>
      <div class="history-list">
        <div v-if="!visibleHistory.length" class="mini-empty">추천 이력이 없습니다.</div>
        <article v-for="item in visibleHistory" :key="`history-${item.id}`">
          <div>
            <strong>{{ displayTitle(item) }}</strong>
            <small>{{ item.bank_name }}</small>
          </div>
          <div>
            <b>{{ formatRate(item.max_interest_rate || item.interest_rate) }}</b>
            <small>{{ formatDate(item.created_at) }}</small>
          </div>
        </article>
      </div>
    </section>
  </section>
</template>

<style scoped>
.recommend-page {
  display: grid;
  gap: 18px;
}

.notice-card {
  border: 2px solid var(--color-ink);
  border-radius: 16px;
  background: var(--color-money-light);
  margin: 0;
  padding: 12px;
  font-weight: 900;
}

.loading-card {
  display: grid;
  justify-items: center;
  gap: 10px;
  padding: 30px;
  text-align: center;
}

.loading-card span {
  width: 44px;
  height: 44px;
  border: 5px solid rgba(23, 19, 13, 0.14);
  border-top-color: var(--color-gold);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

.recommend-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.recommend-card {
  display: grid;
  gap: 12px;
  padding: 18px;
  animation: card-pop 0.42s ease both;
  animation-delay: var(--delay);
}

.recommend-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.recommend-top strong {
  color: var(--color-dark-gold);
  font-size: 25px;
}

.recommend-card h2 {
  margin: 0;
  font-size: 22px;
}

.recommend-card p,
.bank-box small,
.history-list small {
  margin: 0;
  color: var(--color-muted);
}

.bank-box,
.reason-box,
.comment-box,
.caution {
  border-radius: 14px;
  background: rgba(255, 248, 231, 0.7);
  padding: 11px;
}

.bank-box,
.reason-box,
.comment-box {
  display: grid;
  gap: 4px;
}

.comment-box {
  background: rgba(200, 210, 170, 0.32);
}

.join-button {
  justify-self: start;
}

.history-panel {
  padding: 18px;
}

.history-head,
.history-list article {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.history-head h2 {
  margin: 0;
  font-size: 22px;
}

.history-list {
  display: grid;
  gap: 10px;
  margin-top: 14px;
}

.history-list article {
  border: 1px solid rgba(23, 19, 13, 0.16);
  border-radius: 16px;
  background: rgba(255, 248, 231, 0.62);
  padding: 12px;
}

.history-list article > div {
  display: grid;
}

.mini-empty {
  color: var(--color-muted);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@media (max-width: 900px) {
  .recommend-grid {
    grid-template-columns: 1fr;
  }
}
</style>
