<script setup>
import { computed, onMounted } from 'vue'

import { useAnalysisStore } from '../stores/analysis'
import { formatAmount, formatDate } from '../utils/format'


const analysisStore = useAnalysisStore()

const result = computed(() => analysisStore.latest)
const categoryItems = computed(() => result.value?.category_items || [])
const riskLabel = computed(() => {
  if (result.value?.risk_level === 'high') return '높음'
  if (result.value?.risk_level === 'medium') return '보통'
  if (result.value?.risk_level === 'low') return '낮음'
  return '-'
})
const riskClass = computed(() => {
  if (result.value?.risk_level === 'low') return 'text-success'
  if (result.value?.risk_level === 'high') return 'text-danger'
  return 'text-warning'
})

const analyze = async () => {
  await analysisStore.analyzeCurrentMonth()
}

onMounted(async () => {
  await Promise.all([
    analysisStore.fetchLatest(),
    analysisStore.fetchHistory(),
  ])
})
</script>

<template>
  <section>
    <div class="section-head">
      <div>
        <h1>월별 소비 AI 분석</h1>
        <p>이번 달 소비 로그를 바탕으로 소비 패턴과 절약 포인트를 분석합니다.</p>
      </div>
      <div class="d-flex flex-wrap gap-2">
        <button class="btn btn-primary" type="button" :disabled="analysisStore.isLoading" @click="analyze">
          {{ analysisStore.isLoading ? '분석 중...' : 'AI 분석하기' }}
        </button>
        <RouterLink class="btn btn-outline-secondary" :to="{ name: 'finance-hub', query: { tab: 'recommend' } }">금융상품 추천</RouterLink>
      </div>
    </div>

    <div v-if="analysisStore.errorMessage" class="alert alert-danger">
      {{ analysisStore.errorMessage }}
    </div>

    <div v-if="!result" class="surface grid-empty">
      <div>
        <p class="fw-bold mb-1">아직 분석 결과가 없습니다.</p>
        <p class="mb-0">소비 로그를 작성한 뒤 AI 분석하기 버튼을 눌러 주세요.</p>
      </div>
    </div>

    <template v-else>
      <div class="row g-3 mb-4">
        <div class="col-12 col-md-3">
          <div class="surface p-3 h-100">
            <p class="text-secondary mb-1">총 소비 금액</p>
            <div class="summary-value">{{ formatAmount(result.total_amount) }}</div>
          </div>
        </div>
        <div class="col-12 col-md-3">
          <div class="surface p-3 h-100">
            <p class="text-secondary mb-1">소비 기록 수</p>
            <div class="summary-value">{{ result.log_count }}건</div>
          </div>
        </div>
        <div class="col-12 col-md-3">
          <div class="surface p-3 h-100">
            <p class="text-secondary mb-1">평균 소비 금액</p>
            <div class="summary-value">{{ formatAmount(result.average_amount) }}</div>
          </div>
        </div>
        <div class="col-12 col-md-3">
          <div class="surface p-3 h-100">
            <p class="text-secondary mb-1">위험도</p>
            <div class="summary-value" :class="riskClass">{{ riskLabel }}</div>
          </div>
        </div>
      </div>

      <div class="row g-4">
        <div class="col-12 col-lg-6">
          <article class="surface p-3 h-100">
            <h2 class="h5 mb-3">카테고리별 소비</h2>
            <div v-if="!categoryItems.length" class="text-secondary">카테고리별 소비 데이터가 없습니다.</div>
            <div v-for="item in categoryItems" :key="item.name" class="border-top py-3">
              <div class="d-flex justify-content-between gap-3">
                <div>
                  <strong>{{ item.name }}</strong>
                  <div class="small text-secondary">{{ item.count }}건 · {{ item.ratio }}%</div>
                </div>
                <strong>{{ formatAmount(item.total) }}</strong>
              </div>
              <div class="progress mt-2" role="progressbar" :aria-valuenow="item.ratio" aria-valuemin="0" aria-valuemax="100">
                <div class="progress-bar bg-success" :style="{ width: `${Math.min(item.ratio, 100)}%` }"></div>
              </div>
            </div>
          </article>
        </div>

        <div class="col-12 col-lg-6">
          <div class="d-grid gap-3">
            <article class="surface p-3">
              <h2 class="h5">소비 요약</h2>
              <p class="mb-0">{{ result.summary }}</p>
            </article>
            <article class="surface p-3">
              <h2 class="h5">주요 문제점</h2>
              <p class="mb-0">{{ result.problem }}</p>
            </article>
            <article class="surface p-3">
              <h2 class="h5">개선 피드백</h2>
              <p class="mb-0">{{ result.feedback }}</p>
            </article>
            <article class="surface p-3">
              <h2 class="h5">절약 팁</h2>
              <p class="mb-0">{{ result.saving_tip }}</p>
            </article>
          </div>
        </div>
      </div>

      <article class="surface mt-4">
        <div class="p-3 border-bottom">
          <h2 class="h5 mb-0">분석 기록</h2>
        </div>
        <div class="list-group list-group-flush">
          <div v-if="!analysisStore.history.length" class="list-group-item text-secondary">분석 기록이 없습니다.</div>
          <div v-for="item in analysisStore.history" :key="item.id" class="list-group-item d-flex justify-content-between gap-3">
            <div>
              <strong>{{ item.year }}년 {{ item.month }}월</strong>
              <div class="small text-secondary">{{ formatDate(item.created_at) }}</div>
            </div>
            <strong>{{ formatAmount(item.total_amount) }}</strong>
          </div>
        </div>
      </article>
    </template>
  </section>
</template>
