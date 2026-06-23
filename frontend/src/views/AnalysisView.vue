<script setup>
import { computed, onBeforeUnmount, onMounted, ref, watch } from 'vue'

import { getExpenses } from '../api/expenses'
import { useAnalysisStore } from '../stores/analysis'
import { formatAmount, formatDate } from '../utils/format'

const analysisStore = useAnalysisStore()

const periods = [
  { id: 'today', label: '오늘 하루', copy: '오늘의 소비 리듬을 점검합니다.' },
  { id: 'month', label: '이번 달', copy: '이번 달 소비 패턴과 개선 포인트를 분석합니다.' },
  { id: 'year', label: '올해', copy: '올해의 소비 방향을 장기 관점으로 정리합니다.' },
]

const activePeriod = ref('month')
const localResult = ref(null)
const logs = ref([])
const typedText = ref('')
const isLocalLoading = ref(false)
let typingTimer = null

const result = computed(() => (activePeriod.value === 'month' ? analysisStore.latest : localResult.value))
const categoryItems = computed(() => result.value?.category_items || [])
const activeCopy = computed(() => periods.find((item) => item.id === activePeriod.value)?.copy || '')
const isLoading = computed(() => analysisStore.isLoading || isLocalLoading.value)
const riskLabel = computed(() => {
  if (result.value?.risk_level === 'high') return '높음'
  if (result.value?.risk_level === 'medium') return '보통'
  if (result.value?.risk_level === 'low') return '낮음'
  return '-'
})
const riskClass = computed(() => {
  if (result.value?.risk_level === 'low') return 'risk-low'
  if (result.value?.risk_level === 'high') return 'risk-high'
  return 'risk-medium'
})
const typingSource = computed(() => {
  if (!result.value) return ''
  return [
    `AI 소비 분석: ${result.value.summary}`,
    `피드백: ${result.value.feedback}`,
    `개선 포인트: ${result.value.saving_tip}`,
    `종합 의견: ${result.value.problem}`,
  ].join('\n\n')
})

const runTyping = () => {
  window.clearInterval(typingTimer)
  typedText.value = ''
  const text = typingSource.value
  let cursor = 0
  typingTimer = window.setInterval(() => {
    typedText.value = text.slice(0, cursor)
    cursor += 1
    if (cursor > text.length) window.clearInterval(typingTimer)
  }, 18)
}

const getPeriodLogs = (period) => {
  const now = new Date()
  return logs.value.filter((log) => {
    const date = new Date(log.created_at)
    if (period === 'today') return date.toDateString() === now.toDateString()
    if (period === 'year') return date.getFullYear() === now.getFullYear()
    return date.getFullYear() === now.getFullYear() && date.getMonth() === now.getMonth()
  })
}

const buildLocalAnalysis = (period) => {
  const periodLogs = getPeriodLogs(period)
  const total = periodLogs.reduce((sum, log) => sum + Number(log.amount || 0), 0)
  const categoryMap = new Map()

  periodLogs.forEach((log) => {
    const name = log.category_name || '기타'
    const current = categoryMap.get(name) || { name, total: 0, count: 0 }
    current.total += Number(log.amount || 0)
    current.count += 1
    categoryMap.set(name, current)
  })

  const category_items = Array.from(categoryMap.values())
    .map((item) => ({
      ...item,
      ratio: total ? Math.round((item.total / total) * 1000) / 10 : 0,
    }))
    .sort((a, b) => b.total - a.total)
  const top = category_items[0]
  const label = period === 'today' ? '오늘' : '올해'
  const risk_level = total >= (period === 'today' ? 100000 : 5000000)
    ? 'high'
    : total >= (period === 'today' ? 50000 : 2400000)
      ? 'medium'
      : 'low'

  if (!periodLogs.length) {
    return {
      total_amount: 0,
      log_count: 0,
      average_amount: 0,
      category_items: [],
      summary: `${label}은 아직 소비 기록이 없습니다.`,
      problem: '분석할 소비 데이터가 부족합니다.',
      feedback: '소비 직후 금액과 카테고리를 짧게 남기면 다음 분석이 더 정확해집니다.',
      saving_tip: '첫 기록부터 시작해도 충분합니다.',
      risk_level: 'low',
    }
  }

  return {
    total_amount: total,
    log_count: periodLogs.length,
    average_amount: Math.round(total / periodLogs.length),
    category_items,
    summary: `${label} 총 ${formatAmount(total)}을 ${periodLogs.length}건 기록했습니다.`,
    problem: top ? `${top.name} 비중이 ${top.ratio}%로 가장 큽니다.` : '뚜렷한 집중 카테고리가 없습니다.',
    feedback: top ? `${top.name} 소비를 먼저 조정하면 전체 흐름이 가장 빠르게 바뀝니다.` : '현재 소비 흐름은 비교적 고르게 분산되어 있습니다.',
    saving_tip: period === 'today'
      ? '오늘 남은 시간에는 같은 카테고리 반복 지출만 한 번 더 확인해보세요.'
      : '월별 고정비와 변동비를 나눠 보면 다음 달 예산 조정이 쉬워집니다.',
    risk_level,
  }
}

const analyze = async () => {
  if (activePeriod.value === 'month') {
    await analysisStore.analyzeCurrentMonth()
  } else {
    isLocalLoading.value = true
    await new Promise((resolve) => window.setTimeout(resolve, 650))
    localResult.value = buildLocalAnalysis(activePeriod.value)
    isLocalLoading.value = false
  }
  runTyping()
}

watch(activePeriod, () => {
  if (activePeriod.value !== 'month') localResult.value = buildLocalAnalysis(activePeriod.value)
  if (typingSource.value) runTyping()
})

watch(typingSource, () => {
  if (typingSource.value) runTyping()
})

onMounted(async () => {
  const [logsResult] = await Promise.allSettled([
    getExpenses(),
    analysisStore.fetchLatest(),
    analysisStore.fetchHistory(),
  ])
  if (logsResult.status === 'fulfilled') logs.value = logsResult.value.data
  if (typingSource.value) runTyping()
})

onBeforeUnmount(() => {
  window.clearInterval(typingTimer)
})
</script>

<template>
  <section class="analysis-page page-shell">
    <header class="analysis-hero glass-panel">
      <div>
        <span>AI INSIGHT</span>
        <h1>소비 AI 분석</h1>
        <p>{{ activeCopy }}</p>
      </div>
      <button class="vintage-button" type="button" :disabled="isLoading" @click="analyze">
        {{ isLoading ? '분석중...' : 'AI 분석 요청' }}
      </button>
    </header>

    <div class="period-tabs">
      <button
        v-for="(period, index) in periods"
        :key="period.id"
        type="button"
        :class="{ active: activePeriod === period.id }"
        :style="{ '--delay': `${index * 110}ms` }"
        @click="activePeriod = period.id"
      >
        <strong>{{ period.label }}</strong>
        <span>{{ period.copy }}</span>
      </button>
    </div>

    <p v-if="analysisStore.errorMessage && activePeriod === 'month'" class="state-card error">
      {{ analysisStore.errorMessage }}
    </p>

    <div v-if="isLoading" class="analyzing-card vintage-card">
      <span class="loader"></span>
      <strong>분석중...</strong>
      <p>선택된 기간의 소비 기록을 정리하고 있습니다.</p>
    </div>

    <div v-else-if="!result" class="state-card">
      <div>
        <strong>아직 분석 결과가 없습니다.</strong>
        <p>기간을 선택한 뒤 AI 분석 요청 버튼을 눌러주세요.</p>
      </div>
    </div>

    <template v-else>
      <div class="summary-grid">
        <article class="vintage-card">
          <span>총 소비 금액</span>
          <strong>{{ formatAmount(result.total_amount) }}</strong>
        </article>
        <article class="vintage-card">
          <span>소비 기록</span>
          <strong>{{ result.log_count }}건</strong>
        </article>
        <article class="vintage-card">
          <span>평균 소비 금액</span>
          <strong>{{ formatAmount(result.average_amount) }}</strong>
        </article>
        <article class="vintage-card">
          <span>위험도</span>
          <strong :class="riskClass">{{ riskLabel }}</strong>
        </article>
      </div>

      <div class="analysis-layout">
        <article class="typing-panel vintage-card">
          <h2>AI 소비 분석</h2>
          <p class="typing-text">{{ typedText }}<span class="cursor">|</span></p>
        </article>

        <aside class="category-panel glass-panel">
          <h2>카테고리 요약</h2>
          <div v-if="!categoryItems.length" class="mini-empty">카테고리 데이터가 없습니다.</div>
          <div v-for="item in categoryItems" :key="item.name" class="category-row">
            <div>
              <strong>{{ item.name }}</strong>
              <small>{{ item.count }}건 · {{ item.ratio }}%</small>
            </div>
            <b>{{ formatAmount(item.total) }}</b>
            <span><i :style="{ width: `${Math.min(item.ratio, 100)}%` }"></i></span>
          </div>
        </aside>
      </div>

      <section v-if="activePeriod === 'month'" class="history-panel glass-panel">
        <div class="history-head">
          <h2>분석 기록</h2>
          <span>{{ analysisStore.history.length }}건</span>
        </div>
        <div class="history-list">
          <div v-if="!analysisStore.history.length" class="mini-empty">분석 기록이 없습니다.</div>
          <article v-for="item in analysisStore.history" :key="item.id">
            <strong>{{ item.year }}년 {{ item.month }}월</strong>
            <small>{{ formatDate(item.created_at) }}</small>
            <b>{{ formatAmount(item.total_amount) }}</b>
          </article>
        </div>
      </section>
    </template>
  </section>
</template>

<style scoped>
.analysis-page {
  display: grid;
  gap: 18px;
}

.analysis-hero {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 18px;
  padding: 24px;
}

.analysis-hero span,
.summary-grid span {
  color: var(--color-dark-gold);
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0.12em;
}

.analysis-hero h1 {
  margin: 5px 0;
  font-size: clamp(34px, 6vw, 56px);
}

.analysis-hero p {
  margin: 0;
  color: var(--color-muted);
}

.period-tabs {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.period-tabs button {
  display: grid;
  gap: 6px;
  min-height: 112px;
  border: 2px solid var(--color-ink);
  border-radius: 24px;
  background: rgba(255, 248, 231, 0.72);
  color: var(--color-ink);
  padding: 18px;
  text-align: left;
  animation: card-pop 0.42s ease both;
  animation-delay: var(--delay);
  transition: transform 0.16s ease, background 0.16s ease;
}

.period-tabs button.active {
  background: var(--color-gold);
  box-shadow: 4px 4px 0 var(--color-ink);
  transform: translateY(-3px);
}

.period-tabs strong {
  font-size: 20px;
}

.period-tabs span {
  color: var(--color-muted);
  font-size: 13px;
}

.analyzing-card {
  display: grid;
  justify-items: center;
  gap: 10px;
  padding: 34px 18px;
  text-align: center;
}

.loader {
  width: 46px;
  height: 46px;
  border: 5px solid rgba(23, 19, 13, 0.16);
  border-top-color: var(--color-gold);
  border-radius: 50%;
  animation: spin 0.9s linear infinite;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.summary-grid article {
  display: grid;
  gap: 8px;
  padding: 16px;
}

.summary-grid strong {
  font-size: 25px;
}

.risk-low {
  color: var(--color-money);
}

.risk-medium {
  color: var(--color-dark-gold);
}

.risk-high {
  color: var(--color-red);
}

.analysis-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.15fr) minmax(300px, 0.85fr);
  gap: 18px;
  align-items: stretch;
}

.typing-panel {
  padding: 22px;
}

.typing-panel h2,
.category-panel h2,
.history-head h2 {
  margin: 0 0 14px;
  font-size: 24px;
}

.typing-text {
  min-height: 250px;
  margin: 0;
  line-height: 1.8;
  white-space: pre-wrap;
}

.cursor {
  color: var(--color-red);
  animation: blink 0.9s step-end infinite;
}

.category-panel,
.history-panel {
  padding: 20px;
}

.category-row {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 7px 12px;
  padding: 12px 0;
  border-top: 1px solid rgba(23, 19, 13, 0.14);
}

.category-row small {
  display: block;
  color: var(--color-muted);
}

.category-row span {
  grid-column: 1 / -1;
  height: 8px;
  overflow: hidden;
  border-radius: 999px;
  background: rgba(23, 19, 13, 0.12);
}

.category-row i {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: var(--color-money);
}

.history-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.history-head span {
  font-weight: 900;
}

.history-list {
  display: grid;
  gap: 10px;
}

.history-list article {
  display: grid;
  grid-template-columns: 1fr auto;
  gap: 2px 12px;
  border: 1px solid rgba(23, 19, 13, 0.14);
  border-radius: 16px;
  background: rgba(255, 248, 231, 0.62);
  padding: 12px;
}

.history-list small {
  color: var(--color-muted);
}

.history-list b {
  grid-row: 1 / 3;
  grid-column: 2;
  align-self: center;
}

.mini-empty {
  color: var(--color-muted);
  padding: 18px 0;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes blink {
  50% {
    opacity: 0;
  }
}

@media (max-width: 900px) {
  .analysis-layout,
  .summary-grid {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 640px) {
  .analysis-hero {
    align-items: stretch;
    flex-direction: column;
  }

  .period-tabs,
  .analysis-layout,
  .summary-grid {
    grid-template-columns: 1fr;
  }
}
</style>
