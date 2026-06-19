<script setup>
import { computed, onMounted, ref } from 'vue'

import api from '../api/client'
import { formatDate, formatRate } from '../utils/format'


const latest = ref([])
const history = ref([])
const isLoading = ref(false)
const errorMessage = ref('')

const productTypeLabel = (type) => {
  if (type === 'deposit') return '정기예금'
  if (type === 'saving') return '정기적금'
  return '-'
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
  <section>
    <div class="section-head">
      <div>
        <h1>AI 금융상품 추천</h1>
        <p>소비 분석 결과와 저장된 금융상품 후보를 바탕으로 참고용 추천을 생성합니다.</p>
      </div>
      <div class="d-flex flex-wrap gap-2">
        <RouterLink class="btn btn-outline-secondary" :to="{ name: 'finance-products' }">상품 목록</RouterLink>
        <button class="btn btn-primary" type="button" :disabled="isLoading" @click="requestRecommendation">
          {{ isLoading ? '추천 생성 중...' : 'AI 추천 받기' }}
        </button>
      </div>
    </div>

    <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>

    <div v-if="!latest.length" class="surface grid-empty">
      아직 생성된 금융상품 추천이 없습니다.
    </div>

    <div v-else class="row g-3">
      <div v-for="item in latest" :key="item.id" class="col-12 col-lg-4">
        <article class="surface p-3 h-100 d-grid gap-3">
          <div class="d-flex justify-content-between gap-3">
            <span class="badge text-bg-success">{{ productTypeLabel(item.product_type) }}</span>
            <strong class="rate-text">{{ formatRate(item.max_interest_rate || item.interest_rate) }}</strong>
          </div>
          <div>
            <h2 class="h5">{{ item.title }}</h2>
            <p class="text-secondary mb-0">{{ item.description }}</p>
          </div>
          <div>
            <strong>{{ item.bank_name || '상품 데이터 없음' }}</strong>
            <div class="text-secondary small">{{ item.product_name || 'fixture 로드가 필요합니다.' }}</div>
          </div>
          <div class="d-flex flex-wrap gap-2 small">
            <span class="badge text-bg-light border">{{ item.save_trm || '-' }}개월</span>
            <span class="badge text-bg-light border">기본 {{ formatRate(item.interest_rate) }}</span>
            <span class="badge text-bg-light border">최고 {{ formatRate(item.max_interest_rate) }}</span>
          </div>
          <div class="border rounded-2 p-3">
            <strong>추천 이유</strong>
            <p class="mb-0 mt-1">{{ item.reason }}</p>
          </div>
          <div v-if="item.ai_comment" class="border rounded-2 p-3 bg-light">
            <strong>AI 코멘트</strong>
            <p class="mb-0 mt-1">{{ item.ai_comment }}</p>
          </div>
          <p class="small text-secondary mb-0">{{ item.caution }}</p>
        </article>
      </div>
    </div>

    <section class="surface mt-4">
      <div class="p-3 border-bottom d-flex justify-content-between">
        <h2 class="h5 mb-0">추천 이력</h2>
        <span class="text-secondary">{{ history.length }}건</span>
      </div>
      <div class="list-group list-group-flush">
        <div v-if="!visibleHistory.length" class="list-group-item text-secondary">추천 이력이 없습니다.</div>
        <div v-for="item in visibleHistory" :key="`history-${item.id}`" class="list-group-item d-flex justify-content-between gap-3">
          <div>
            <strong>{{ item.title }}</strong>
            <div class="small text-secondary">{{ item.bank_name }} · {{ item.product_name }}</div>
          </div>
          <div class="text-end">
            <strong>{{ formatRate(item.max_interest_rate || item.interest_rate) }}</strong>
            <div class="small text-secondary">{{ formatDate(item.created_at) }}</div>
          </div>
        </div>
      </div>
    </section>
  </section>
</template>

<style scoped>
.rate-text {
  color: #2f6b5e;
  font-size: 24px;
}
</style>
