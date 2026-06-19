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
  <section>
    <div class="section-head">
      <div>
        <h1>마이페이지</h1>
        <p>내 소비 기록과 분석 흐름을 한곳에서 확인합니다.</p>
      </div>
      <div class="d-flex flex-wrap gap-2">
        <RouterLink class="btn btn-outline-primary" :to="{ name: 'analysis' }">AI 분석</RouterLink>
        <RouterLink class="btn btn-outline-secondary" :to="{ name: 'stocks' }">보유 주식</RouterLink>
      </div>
    </div>

    <div v-if="isLoading" class="alert alert-secondary">불러오는 중입니다.</div>
    <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>

    <div class="row g-3 mb-4">
      <div class="col-12 col-md-3">
        <div class="surface p-3 h-100">
          <p class="text-secondary mb-1">이번 달 소비</p>
          <div class="summary-value">{{ formatAmount(analysis?.total_amount) }}</div>
        </div>
      </div>
      <div class="col-12 col-md-3">
        <div class="surface p-3 h-100">
          <p class="text-secondary mb-1">소비 기록</p>
          <div class="summary-value">{{ analysis?.log_count || 0 }}건</div>
        </div>
      </div>
      <div class="col-12 col-md-3">
        <div class="surface p-3 h-100">
          <p class="text-secondary mb-1">최다 카테고리</p>
          <div class="summary-value">{{ topCategory }}</div>
        </div>
      </div>
      <div class="col-12 col-md-3">
        <div class="surface p-3 h-100">
          <p class="text-secondary mb-1">소비 위험도</p>
          <div class="summary-value">{{ riskLabel }}</div>
        </div>
      </div>
    </div>

    <div class="row g-4">
      <div class="col-12 col-lg-7">
        <div class="surface">
          <div class="p-3 border-bottom d-flex justify-content-between align-items-center">
            <h2 class="h5 mb-0">최근 소비 기록</h2>
            <RouterLink class="btn btn-outline-secondary btn-sm" :to="{ name: 'logs' }">전체 보기</RouterLink>
          </div>
          <div class="list-group list-group-flush">
            <div v-if="!recentLogs.length" class="list-group-item text-secondary">아직 기록이 없습니다.</div>
            <div v-for="log in recentLogs" :key="log.id" class="list-group-item">
              <div class="d-flex justify-content-between gap-3">
                <div>
                  <span class="badge text-bg-light border me-2">{{ log.category_name }}</span>
                  <strong>{{ log.product_name || log.content || '소비 기록' }}</strong>
                  <div class="small text-secondary">{{ formatDate(log.created_at) }}</div>
                </div>
                <strong class="text-nowrap">{{ formatAmount(log.amount) }}</strong>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="col-12 col-lg-5">
        <div class="surface p-3 h-100">
          <h2 class="h5 mb-3">최근 AI 분석</h2>
          <template v-if="aiLatest">
            <p class="fw-bold">{{ aiLatest.summary }}</p>
            <p class="text-secondary">{{ aiLatest.feedback }}</p>
            <RouterLink class="btn btn-primary btn-sm" :to="{ name: 'analysis' }">분석 자세히 보기</RouterLink>
          </template>
          <template v-else>
            <p class="text-secondary">생성된 AI 분석이 없습니다.</p>
            <RouterLink class="btn btn-primary btn-sm" :to="{ name: 'analysis' }">AI 분석 시작</RouterLink>
          </template>
        </div>
      </div>
    </div>
  </section>
</template>
