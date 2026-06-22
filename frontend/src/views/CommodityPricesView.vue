<script setup>
import { createChart, LineSeries } from 'lightweight-charts'
import { nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'

import { getCommodityPrices } from '../api/financial'

const selectedCode = ref('GOLD')
const filters = reactive({ start: '', end: '' })
const commodity = ref(null)
const prices = ref([])
const chartContainer = ref(null)
const isLoading = ref(false)
const errorMessage = ref('')
let chart = null
let line = null
let resizeObserver = null

const setupChart = () => {
  if (chart || !chartContainer.value) return
  chart = createChart(chartContainer.value, {
    height: 360,
    layout: {
      background: { color: '#fff8e7' },
      textColor: '#6f644f',
      attributionLogo: false,
    },
    grid: {
      vertLines: { color: 'rgba(23, 19, 13, 0.08)' },
      horzLines: { color: 'rgba(23, 19, 13, 0.08)' },
    },
    timeScale: { borderColor: 'rgba(23, 19, 13, 0.25)' },
    rightPriceScale: { borderColor: 'rgba(23, 19, 13, 0.25)' },
  })
  line = chart.addSeries(LineSeries, {
    color: selectedCode.value === 'GOLD' ? '#d8a526' : '#7f936b',
    lineWidth: 3,
  })
  resizeObserver = new ResizeObserver(([entry]) => chart.applyOptions({ width: entry.contentRect.width }))
  resizeObserver.observe(chartContainer.value)
}

const drawChart = () => {
  if (!line) return
  line.applyOptions({ color: selectedCode.value === 'GOLD' ? '#d8a526' : '#7f936b' })
  line.setData(prices.value.map((item) => ({ time: item.price_date, value: Number(item.close_price) })))
  chart.timeScale().fitContent()
}

const loadPrices = async () => {
  errorMessage.value = ''
  if (filters.start && filters.end && filters.start > filters.end) {
    errorMessage.value = '시작일은 종료일보다 늦을 수 없습니다.'
    return
  }
  isLoading.value = true
  try {
    const response = await getCommodityPrices(selectedCode.value, {
      ...(filters.start && { start: filters.start }),
      ...(filters.end && { end: filters.end }),
    })
    commodity.value = response.data.commodity
    prices.value = response.data.prices
    await nextTick()
    setupChart()
    drawChart()
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '시세를 불러오지 못했습니다.'
  } finally {
    isLoading.value = false
  }
}

watch(selectedCode, loadPrices)
onMounted(loadPrices)
onBeforeUnmount(() => {
  resizeObserver?.disconnect()
  chart?.remove()
})
</script>

<template>
  <section class="commodity-page page-shell">
    <div class="section-head">
      <div>
        <h1>현물상품</h1>
        <p>금과 은의 USD / troy oz 기준 일별 종가를 확인합니다.</p>
      </div>
    </div>

    <div class="asset-tabs">
      <button :class="{ active: selectedCode === 'GOLD' }" type="button" @click="selectedCode = 'GOLD'">
        <span>Au</span>
        금
      </button>
      <button :class="{ active: selectedCode === 'SILVER' }" type="button" @click="selectedCode = 'SILVER'">
        <span>Ag</span>
        은
      </button>
    </div>

    <form class="filter-card glass-panel" @submit.prevent="loadPrices">
      <label>
        시작일
        <input v-model="filters.start" class="form-control" type="date">
      </label>
      <label>
        종료일
        <input v-model="filters.end" class="form-control" type="date">
      </label>
      <button class="vintage-button" type="submit">기간 적용</button>
    </form>

    <p v-if="errorMessage" class="state-card error">{{ errorMessage }}</p>

    <article class="chart-card vintage-card">
      <header>
        <div class="asset-avatar">{{ selectedCode === 'GOLD' ? 'Au' : 'Ag' }}</div>
        <div>
          <strong>{{ commodity?.name || selectedCode }}</strong>
          <small>{{ prices.length }}개 데이터</small>
        </div>
      </header>

      <div v-if="isLoading" class="grid-empty">시세를 불러오는 중입니다.</div>
      <div v-else-if="!prices.length" class="grid-empty">선택한 기간에 데이터가 없습니다.</div>
      <div v-show="prices.length" ref="chartContainer" class="chart"></div>

      <footer v-if="prices.length">
        <strong>최근 종가 ${{ Number(prices.at(-1)?.close_price).toLocaleString() }}</strong>
        <span>{{ prices[0]?.price_date }} ~ {{ prices.at(-1)?.price_date }}</span>
      </footer>
    </article>
  </section>
</template>

<style scoped>
.commodity-page {
  display: grid;
  gap: 18px;
}

.asset-tabs {
  display: flex;
  gap: 14px;
}

.asset-tabs button {
  display: grid;
  justify-items: center;
  gap: 7px;
  border: 0;
  background: transparent;
  color: var(--color-muted);
  font-weight: 900;
}

.asset-tabs span {
  display: grid;
  width: 74px;
  height: 74px;
  place-items: center;
  border: 3px solid var(--color-ink);
  border-radius: 50%;
  background: var(--color-paper);
  box-shadow: 4px 4px 0 var(--color-ink);
  color: var(--color-ink);
  font-size: 23px;
}

.asset-tabs button.active span {
  background: var(--color-gold);
}

.filter-card {
  display: grid;
  grid-template-columns: 1fr 1fr auto;
  align-items: end;
  gap: 12px;
  padding: 16px;
}

label {
  display: grid;
  gap: 6px;
  color: var(--color-muted);
  font-weight: 900;
}

.chart-card {
  overflow: hidden;
}

.chart-card header {
  display: flex;
  align-items: center;
  gap: 12px;
  border-bottom: 2px solid var(--color-ink);
  padding: 14px;
}

.chart-card header div:nth-child(2) {
  display: grid;
}

.chart-card small {
  color: var(--color-muted);
}

.asset-avatar {
  display: grid;
  width: 42px;
  height: 42px;
  place-items: center;
  border: 2px solid var(--color-ink);
  border-radius: 50%;
  background: var(--color-money);
  color: var(--color-paper);
  font-weight: 900;
}

.chart {
  width: 100%;
  height: 360px;
}

.chart-card footer {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  border-top: 2px solid rgba(23, 19, 13, 0.14);
  padding: 16px;
}

.chart-card footer span {
  color: var(--color-muted);
}

@media (max-width: 640px) {
  .filter-card,
  .chart-card footer {
    grid-template-columns: 1fr;
    flex-direction: column;
  }
}
</style>
