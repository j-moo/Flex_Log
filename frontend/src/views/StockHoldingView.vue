<script setup>
import { createChart, LineSeries } from 'lightweight-charts'
import { computed, nextTick, onBeforeUnmount, onMounted, ref, watch } from 'vue'

import { createRealtimePrice, getChart, getStocks } from '../api/finance'


const stocks = ref([])
const selectedSymbol = ref('')
const chartContainer = ref(null)
const isLoading = ref(false)
const errorMessage = ref('')

let chart = null
let lineSeries = null
let resizeObserver = null
let pollingTimer = null

const selectedStock = computed(() =>
  stocks.value.find((stock) => stock.symbol === selectedSymbol.value) || stocks.value[0] || null,
)

const portfolioSummary = computed(() => {
  return stocks.value.reduce(
    (summary, stock) => {
      summary.invested += stock.invested_amount
      summary.valuation += stock.valuation_amount
      summary.profit += stock.profit_loss
      return summary
    },
    { invested: 0, valuation: 0, profit: 0 },
  )
})

const portfolioProfitRate = computed(() => {
  if (!portfolioSummary.value.invested) return 0
  return (portfolioSummary.value.profit / portfolioSummary.value.invested) * 100
})

const formatCurrency = (value) =>
  `${Math.round(Number(value || 0)).toLocaleString('ko-KR')}원`

const formatQuantity = (value) =>
  Number(value || 0).toLocaleString('ko-KR')

const formatRate = (value) =>
  `${Number(value || 0).toFixed(2)}%`

const toChartTime = (isoTime) => Math.floor(new Date(isoTime).getTime() / 1000)

const recalculateStock = (stock, nextPrice) => {
  const valuationAmount = stock.quantity * nextPrice
  const investedAmount = stock.quantity * stock.average_price
  const profitLoss = valuationAmount - investedAmount

  return {
    ...stock,
    current_price: nextPrice,
    valuation_amount: valuationAmount,
    profit_loss: profitLoss,
    profit_rate: investedAmount ? (profitLoss / investedAmount) * 100 : 0,
  }
}

const setupChart = () => {
  if (!chartContainer.value || chart) return

  chart = createChart(chartContainer.value, {
    height: 320,
    layout: {
      background: { color: '#ffffff' },
      textColor: '#657282',
      fontFamily: 'Inter, Pretendard, system-ui, sans-serif',
      attributionLogo: false,
    },
    grid: {
      vertLines: { color: '#eef2f5' },
      horzLines: { color: '#eef2f5' },
    },
    rightPriceScale: {
      borderColor: '#dde4ea',
    },
    timeScale: {
      borderColor: '#dde4ea',
      timeVisible: true,
      secondsVisible: false,
    },
    crosshair: {
      mode: 1,
    },
  })

  lineSeries = chart.addSeries(LineSeries, {
    color: '#2f6b5e',
    lineWidth: 2,
    priceFormat: {
      type: 'price',
      precision: 0,
      minMove: 1,
    },
  })

  resizeObserver = new ResizeObserver((entries) => {
    const width = entries[0]?.contentRect?.width
    if (width) chart.applyOptions({ width })
  })
  resizeObserver.observe(chartContainer.value)
}

const loadChart = async () => {
  if (!selectedStock.value || !lineSeries) return
  const points = await getChart(selectedStock.value.symbol, '1m')
  lineSeries.setData(points.map((point) => ({
    time: toChartTime(point.time),
    value: point.price,
  })))
  chart.timeScale().fitContent()
}

const applyRealtimeTick = () => {
  stocks.value = stocks.value.map((stock) => {
    const nextPrice = createRealtimePrice(stock.current_price)
    return recalculateStock(stock, nextPrice)
  })

  if (selectedStock.value && lineSeries) {
    const now = new Date()
    now.setSeconds(0, 0)
    lineSeries.update({
      time: Math.floor(now.getTime() / 1000),
      value: selectedStock.value.current_price,
    })
  }
}

const startRealtimeMock = () => {
  window.clearInterval(pollingTimer)
  pollingTimer = window.setInterval(applyRealtimeTick, 5000)
}

const selectStock = (symbol) => {
  selectedSymbol.value = symbol
}

onMounted(async () => {
  isLoading.value = true
  errorMessage.value = ''

  try {
    stocks.value = await getStocks()
    selectedSymbol.value = stocks.value[0]?.symbol || ''

    isLoading.value = false

    await nextTick()
    setupChart()
    await loadChart()
    startRealtimeMock()
  } catch (error) {
    console.error(error)
    errorMessage.value = '보유주식 Mock 데이터를 불러오지 못했습니다.'
    isLoading.value = false
  }
})

watch(selectedSymbol, loadChart)

onBeforeUnmount(() => {
  window.clearInterval(pollingTimer)
  if (resizeObserver) resizeObserver.disconnect()
  if (chart) chart.remove()
})
</script>

<template>
  <section class="stock-page">
    <div class="section-head stock-head">
      <div>
        <h1>보유주식</h1>
        <p>Mock 시세로 현재가와 수익률을 확인하고, 5초마다 갱신되는 차트를 미리 검증합니다.</p>
      </div>
      <RouterLink class="btn btn-outline-secondary" :to="{ name: 'finance-products' }">
        금융상품
      </RouterLink>
    </div>

    <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
    <div v-if="isLoading" class="surface grid-empty">보유주식 정보를 불러오는 중입니다.</div>

    <template v-else>
      <div class="summary-grid">
        <div class="surface summary-card">
          <span>총 매수금액</span>
          <strong>{{ formatCurrency(portfolioSummary.invested) }}</strong>
        </div>
        <div class="surface summary-card">
          <span>총 평가금액</span>
          <strong>{{ formatCurrency(portfolioSummary.valuation) }}</strong>
        </div>
        <div class="surface summary-card">
          <span>총 수익률</span>
          <strong :class="portfolioSummary.profit >= 0 ? 'text-success' : 'text-danger'">
            {{ formatRate(portfolioProfitRate) }}
          </strong>
        </div>
      </div>

      <div class="stock-layout">
        <div class="surface stock-table-wrap">
          <div class="table-title">
            <h2>보유 목록</h2>
            <span>5초 Mock polling</span>
          </div>

          <div class="table-responsive">
            <table class="table stock-table align-middle">
              <thead>
                <tr>
                  <th>종목명</th>
                  <th>종목코드</th>
                  <th class="text-end">보유수량</th>
                  <th class="text-end">평균매수단가</th>
                  <th class="text-end">현재가</th>
                  <th class="text-end">수익률</th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="stock in stocks"
                  :key="stock.symbol"
                  :class="{ selected: stock.symbol === selectedStock?.symbol }"
                  @click="selectStock(stock.symbol)"
                >
                  <td>
                    <strong>{{ stock.name }}</strong>
                  </td>
                  <td>{{ stock.symbol }}</td>
                  <td class="text-end">{{ formatQuantity(stock.quantity) }}</td>
                  <td class="text-end">{{ formatCurrency(stock.average_price) }}</td>
                  <td class="text-end">{{ formatCurrency(stock.current_price) }}</td>
                  <td
                    class="text-end fw-bold"
                    :class="stock.profit_rate >= 0 ? 'text-success' : 'text-danger'"
                  >
                    {{ formatRate(stock.profit_rate) }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <aside class="surface chart-panel">
          <div class="chart-header">
            <div>
              <h2>{{ selectedStock?.name || '종목 선택' }}</h2>
              <p>{{ selectedStock?.symbol }}</p>
            </div>
            <div v-if="selectedStock" class="price-block">
              <strong>{{ formatCurrency(selectedStock.current_price) }}</strong>
              <span :class="selectedStock.profit_rate >= 0 ? 'text-success' : 'text-danger'">
                {{ formatRate(selectedStock.profit_rate) }}
              </span>
            </div>
          </div>
          <div ref="chartContainer" class="chart-container"></div>
        </aside>
      </div>
    </template>
  </section>
</template>

<style scoped>
.stock-page {
  display: grid;
  gap: 18px;
}

.stock-head {
  margin-bottom: 0;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.summary-card {
  display: grid;
  gap: 6px;
  padding: 16px;
}

.summary-card span {
  color: #657282;
  font-size: 13px;
  font-weight: 800;
}

.summary-card strong {
  color: #172033;
  font-size: 24px;
  line-height: 1.2;
}

.stock-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(360px, 0.9fr);
  gap: 16px;
  align-items: start;
}

.stock-table-wrap,
.chart-panel {
  overflow: hidden;
}

.table-title,
.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px;
  border-bottom: 1px solid #dde4ea;
}

.table-title h2,
.chart-header h2 {
  margin: 0;
  color: #172033;
  font-size: 18px;
  font-weight: 850;
}

.table-title span,
.chart-header p {
  margin: 0;
  color: #657282;
  font-size: 13px;
  font-weight: 700;
}

.stock-table {
  margin: 0;
  min-width: 760px;
}

.stock-table thead th {
  border-bottom: 1px solid #dde4ea;
  color: #657282;
  font-size: 13px;
  font-weight: 850;
  white-space: nowrap;
}

.stock-table tbody tr {
  cursor: pointer;
}

.stock-table tbody tr.selected {
  background: #eef6f2;
}

.stock-table tbody td {
  height: 58px;
  white-space: nowrap;
}

.price-block {
  display: grid;
  gap: 4px;
  text-align: right;
}

.price-block strong {
  color: #172033;
  font-size: 20px;
}

.price-block span {
  font-weight: 850;
}

.chart-container {
  width: 100%;
  height: 320px;
}

@media (max-width: 980px) {
  .stock-layout {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 700px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }

  .table-title,
  .chart-header {
    align-items: flex-start;
    flex-direction: column;
  }

  .price-block {
    text-align: left;
  }
}
</style>
