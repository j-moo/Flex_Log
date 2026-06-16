<script setup>
import { computed, onMounted } from 'vue'

import { useAnalysisStore } from '../stores/analysis'
import { formatAmount, formatDate } from '../utils/format'


const analysisStore = useAnalysisStore()

const result = computed(() => analysisStore.latest)
const categoryItems = computed(() => result.value?.category_items || [])
const riskClass = computed(() => {
  if (result.value?.risk_level === 'low') return 'risk-low'
  if (result.value?.risk_level === 'high') return 'risk-high'
  return 'risk-medium'
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
  <section class="analysis-page">
    <div class="analysis-header">
      <div>
        <h1>월별 소비 AI 분석</h1>
        <p>이번 달 소비 로그를 바탕으로 소비 패턴과 절약 피드백을 생성합니다.</p>
      </div>
      <button class="analysis-button" type="button" :disabled="analysisStore.isLoading" @click="analyze">
        {{ analysisStore.isLoading ? '분석 중...' : 'AI 분석하기' }}
      </button>
    </div>

    <div v-if="analysisStore.errorMessage" class="analysis-alert">
      {{ analysisStore.errorMessage }}
    </div>

    <div v-if="!result" class="analysis-card empty">
      <strong>아직 분석 결과가 없습니다.</strong>
      <span>소비 로그를 작성한 뒤 AI 분석하기 버튼을 눌러주세요.</span>
    </div>

    <template v-else>
      <div class="metric-grid">
        <article class="analysis-card">
          <span>총 소비 금액</span>
          <strong>{{ formatAmount(result.total_amount) }}</strong>
        </article>
        <article class="analysis-card">
          <span>소비 기록 수</span>
          <strong>{{ result.log_count }}건</strong>
        </article>
        <article class="analysis-card">
          <span>평균 소비 금액</span>
          <strong>{{ formatAmount(result.average_amount) }}</strong>
        </article>
        <article class="analysis-card">
          <span>위험도</span>
          <strong :class="riskClass">{{ result.risk_level }}</strong>
        </article>
      </div>

      <div class="analysis-grid">
        <article class="analysis-card wide">
          <div class="card-title">카테고리별 소비</div>
          <div v-if="!categoryItems.length" class="muted">카테고리별 소비 데이터가 없습니다.</div>
          <div v-for="item in categoryItems" :key="item.name" class="category-row">
            <div>
              <strong>{{ item.name }}</strong>
              <span>{{ item.count }}건</span>
            </div>
            <div class="category-amount">
              <strong>{{ formatAmount(item.total) }}</strong>
              <span>{{ item.ratio }}%</span>
            </div>
          </div>
        </article>

        <article class="analysis-card">
          <div class="card-title">요약</div>
          <p>{{ result.summary }}</p>
        </article>
        <article class="analysis-card">
          <div class="card-title">문제점</div>
          <p>{{ result.problem }}</p>
        </article>
        <article class="analysis-card">
          <div class="card-title">개선 피드백</div>
          <p>{{ result.feedback }}</p>
        </article>
        <article class="analysis-card">
          <div class="card-title">절약 팁</div>
          <p>{{ result.saving_tip }}</p>
        </article>
      </div>

      <article class="analysis-card history-card">
        <div class="card-title">분석 기록</div>
        <div v-if="!analysisStore.history.length" class="muted">분석 기록이 없습니다.</div>
        <div v-for="item in analysisStore.history" :key="item.id" class="history-row">
          <div>
            <strong>{{ item.year }}년 {{ item.month }}월</strong>
            <span>{{ formatDate(item.created_at) }}</span>
          </div>
          <div>
            <span>{{ formatAmount(item.total_amount) }}</span>
            <strong :class="{
              'risk-low': item.risk_level === 'low',
              'risk-medium': item.risk_level === 'medium',
              'risk-high': item.risk_level === 'high',
            }">
              {{ item.risk_level }}
            </strong>
          </div>
        </div>
      </article>
    </template>
  </section>
</template>

<style scoped>
.analysis-page {
  min-height: calc(100vh - 120px);
  margin: -28px calc(50% - 50vw) -48px;
  padding: 32px max(20px, calc(50vw - 560px)) 56px;
  background: #0b0e11;
  color: #eaecef;
}

.analysis-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 24px;
}

.analysis-header h1 {
  margin: 0 0 8px;
  font-size: 28px;
  font-weight: 800;
}

.analysis-header p,
.muted,
.analysis-card span {
  color: #707a8a;
}

.analysis-button {
  min-height: 44px;
  padding: 0 18px;
  border: 0;
  border-radius: 8px;
  background: #fcd535;
  color: #0b0e11;
  font-weight: 800;
}

.analysis-button:disabled {
  opacity: 0.65;
}

.analysis-alert {
  margin-bottom: 16px;
  padding: 14px 16px;
  border: 1px solid #f6465d;
  border-radius: 8px;
  background: rgba(246, 70, 93, 0.12);
  color: #f6465d;
}

.metric-grid,
.analysis-grid {
  display: grid;
  gap: 14px;
}

.metric-grid {
  grid-template-columns: repeat(4, minmax(0, 1fr));
  margin-bottom: 14px;
}

.analysis-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}

.analysis-card {
  padding: 18px;
  border: 1px solid #2b3139;
  border-radius: 8px;
  background: #1e2329;
}

.analysis-card.empty {
  display: grid;
  gap: 8px;
}

.analysis-card > strong {
  display: block;
  margin-top: 8px;
  font-size: 24px;
}

.analysis-card p {
  margin: 0;
  line-height: 1.7;
}

.card-title {
  margin-bottom: 12px;
  color: #fcd535;
  font-weight: 800;
}

.wide {
  grid-column: 1 / -1;
  background: #2b3139;
}

.category-row,
.history-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding-block: 12px;
  border-top: 1px solid #3a414b;
}

.category-row:first-of-type,
.history-row:first-of-type {
  border-top: 0;
}

.category-row > div,
.history-row > div {
  display: grid;
  gap: 4px;
}

.category-amount,
.history-row > div:last-child {
  text-align: right;
}

.history-card {
  margin-top: 14px;
}

.risk-low {
  color: #0ecb81;
}

.risk-medium {
  color: #fcd535;
}

.risk-high {
  color: #f6465d;
}

@media (max-width: 900px) {
  .metric-grid,
  .analysis-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 600px) {
  .analysis-page {
    margin-top: -18px;
    padding: 24px 14px 40px;
  }

  .analysis-header {
    align-items: stretch;
    flex-direction: column;
  }

  .analysis-button {
    width: 100%;
  }

  .category-row,
  .history-row {
    align-items: flex-start;
    flex-direction: column;
  }

  .category-amount,
  .history-row > div:last-child {
    text-align: left;
  }
}
</style>
