<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute } from 'vue-router'

import api from '../api/client'
import { getExpenses } from '../api/expenses'
import FeedCard from '../components/feed/FeedCard.vue'
import { formatAmount } from '../utils/format'

const route = useRoute()
const logs = ref([])
const analysis = ref(null)
const isLoading = ref(true)
const errorMessage = ref('')

const dateKey = computed(() => route.params.date)
const dayLogs = computed(() => logs.value.filter((log) => log.created_at?.slice(0, 10) === dateKey.value))
const totalAmount = computed(() => dayLogs.value.reduce((sum, log) => sum + Number(log.amount || 0), 0))
const hasFlex = computed(() => dayLogs.value.length || analysis.value)

const displayDate = computed(() => {
  const date = new Date(`${dateKey.value}T00:00:00`)
  return new Intl.DateTimeFormat('ko-KR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    weekday: 'long',
  }).format(date)
})

onMounted(async () => {
  isLoading.value = true
  try {
    const [logsResult, analysisResult] = await Promise.allSettled([
      getExpenses(),
      api.get('/api/v1/analysis/monthly/latest/'),
    ])
    if (logsResult.status === 'fulfilled') logs.value = logsResult.value.data
    if (analysisResult.status === 'fulfilled') {
      const latest = analysisResult.value.data
      const target = new Date(`${dateKey.value}T00:00:00`)
      if (latest.year === target.getFullYear() && latest.month === target.getMonth() + 1) {
        analysis.value = latest
      }
    }
  } catch {
    errorMessage.value = '해당 날짜 정보를 불러오지 못했습니다.'
  } finally {
    isLoading.value = false
  }
})
</script>

<template>
  <section class="day-page page-shell">
    <div class="section-head">
      <div>
        <h1>{{ displayDate }}</h1>
        <p>이날의 소비 피드와 연결된 AI 분석을 확인합니다.</p>
      </div>
      <RouterLink class="btn btn-outline-dark" :to="{ name: 'finance-hub', query: { tab: 'my' } }">달력으로</RouterLink>
    </div>

    <p v-if="errorMessage" class="state-card error">{{ errorMessage }}</p>
    <p v-else-if="isLoading" class="state-card">이날의 Flex를 찾는 중입니다.</p>

    <template v-else-if="hasFlex">
      <section class="day-summary vintage-card">
        <span>DAY FLEX</span>
        <strong>{{ formatAmount(totalAmount) }}</strong>
        <p>{{ dayLogs.length }}개의 소비 기록이 있습니다.</p>
      </section>

      <section v-if="analysis" class="day-analysis glass-panel">
        <h2>소비 AI 분석</h2>
        <p><strong>요약</strong>{{ analysis.summary }}</p>
        <p><strong>피드백</strong>{{ analysis.feedback }}</p>
        <p><strong>개선 포인트</strong>{{ analysis.saving_tip }}</p>
      </section>

      <div v-if="dayLogs.length" class="day-feed">
        <FeedCard v-for="log in dayLogs" :key="log.id" :log="log" />
      </div>
    </template>

    <div v-else class="state-card empty-flex">
      <strong>이날의 Flex는 없었다...</strong>
      <p>지갑도 쉬고, 기록도 쉬어간 날입니다.</p>
      <RouterLink class="vintage-button" :to="{ name: 'log-create' }">이날의 기억 남기기</RouterLink>
    </div>
  </section>
</template>

<style scoped>
.day-page {
  width: min(100%, 760px);
  margin: 0 auto;
}

.day-summary {
  display: grid;
  gap: 8px;
  padding: 20px;
}

.day-summary span {
  color: var(--color-dark-gold);
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0.12em;
}

.day-summary strong {
  font-size: 34px;
}

.day-summary p {
  margin: 0;
  color: var(--color-muted);
}

.day-analysis {
  display: grid;
  gap: 10px;
  padding: 18px;
}

.day-analysis h2 {
  margin: 0;
  font-size: 23px;
}

.day-analysis p {
  display: grid;
  gap: 4px;
  margin: 0;
  color: var(--color-muted);
}

.day-analysis strong {
  color: var(--color-ink);
}

.day-feed {
  display: grid;
  gap: 20px;
}
</style>
