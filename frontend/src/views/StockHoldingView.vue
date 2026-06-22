<script setup>
import { createChart, LineSeries } from 'lightweight-charts'
import { computed, nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'

import { createRealtimePrice, getChart, getStocks } from '../api/finance'
import { createStockHolding, deleteStockHolding, getStockHoldings, getStockQuote } from '../api/financial'
import { findStockCandidate, searchStockCandidates } from '../utils/stocks'

const holdings = ref([])
const selectedSymbol = ref('')
const chartContainer = ref(null)
const isLoading = ref(false)
const errorMessage = ref('')
const actionMessage = ref('')
const useMockData = ref(false)
const deletingId = ref(null)
const form = reactive({
  keyword: '',
  quantity: '',
  average_price: '',
  memo: '',
})

let chart = null
let lineSeries = null
let resizeObserver = null
let pollingTimer = null

const suggestions = computed(() => searchStockCandidates(form.keyword).slice(0, 6))
const selectedStock = computed(() =>
  holdings.value.find((stock) => stock.symbol === selectedSymbol.value) || holdings.value[0] || null,
)
const portfolioSummary = computed(() =>
  holdings.value.reduce(
    (summary, stock) => {
      summary.invested += Number(stock.invested_amount || stock.quantity * stock.average_price || 0)
      summary.valuation += Number(stock.valuation_amount || stock.quantity * stock.current_price || 0)
      summary.profit += Number(stock.profit_loss || 0)
      return summary
    },
    { invested: 0, valuation: 0, profit: 0 },
  ),
)
const portfolioProfitRate = computed(() => {
  if (!portfolioSummary.value.invested) return 0
  return (portfolioSummary.value.profit / portfolioSummary.value.invested) * 100
})

const formatCurrency = (value) => `${Math.round(Number(value || 0)).toLocaleString('ko-KR')}원`
const formatQuantity = (value) => Number(value || 0).toLocaleString('ko-KR')
const formatRate = (value) => `${Number(value || 0).toFixed(2)}%`
const toChartTime = (isoTime) => Math.floor(new Date(isoTime).getTime() / 1000)

const normalizeHolding = (stock) => {
  const quantity = Number(stock.quantity || 0)
  const averagePrice = Number(stock.average_price || 0)
  const currentPrice = Number(stock.current_price || 0)
  const invested = Number(stock.invested_amount ?? quantity * averagePrice)
  const valuation = Number(stock.valuation_amount ?? quantity * currentPrice)
  const profit = Number(stock.profit_loss ?? valuation - invested)
  return {
    ...stock,
    quantity,
    average_price: averagePrice,
    current_price: currentPrice,
    invested_amount: invested,
    valuation_amount: valuation,
    profit_loss: profit,
    profit_rate: Number(stock.profit_rate ?? (invested ? (profit / invested) * 100 : 0)),
  }
}

const recalculateStock = (stock, nextPrice) => {
  const valuationAmount = Number(stock.quantity) * nextPrice
  const investedAmount = Number(stock.quantity) * Number(stock.average_price)
  const profitLoss = valuationAmount - investedAmount
  return normalizeHolding({
    ...stock,
    current_price: nextPrice,
    valuation_amount: valuationAmount,
    profit_loss: profitLoss,
    profit_rate: investedAmount ? (profitLoss / investedAmount) * 100 : 0,
  })
}

const setupChart = () => {
  if (!chartContainer.value || chart) return
  chart = createChart(chartContainer.value, {
    height: 440,
    layout: {
      background: { color: '#fff8e7' },
      textColor: '#6f644f',
      fontFamily: 'Noto Sans KR, system-ui, sans-serif',
      attributionLogo: false,
    },
    grid: {
      vertLines: { color: 'rgba(23, 19, 13, 0.08)' },
      horzLines: { color: 'rgba(23, 19, 13, 0.08)' },
    },
    rightPriceScale: { borderColor: 'rgba(23, 19, 13, 0.25)' },
    timeScale: {
      borderColor: 'rgba(23, 19, 13, 0.25)',
      timeVisible: true,
      secondsVisible: false,
    },
  })

  lineSeries = chart.addSeries(LineSeries, {
    color: '#7f936b',
    lineWidth: 3,
    priceFormat: { type: 'price', precision: 0, minMove: 1 },
  })

  resizeObserver = new ResizeObserver((entries) => {
    const width = entries[0]?.contentRect?.width
    if (width) chart.applyOptions({ width })
  })
  resizeObserver.observe(chartContainer.value)
}

const loadChart = async () => {
  if (!selectedStock.value || !lineSeries) return
  try {
    const points = await getChart(selectedStock.value.symbol, '1m')
    lineSeries.setData(points.map((point) => ({ time: toChartTime(point.time), value: point.price })))
  } catch {
    const base = Number(selectedStock.value.current_price || 1000)
    lineSeries.setData(Array.from({ length: 30 }, (_, index) => ({
      time: Math.floor((Date.now() - (29 - index) * 60000) / 1000),
      value: Math.round(base * (0.97 + index * 0.002 + Math.sin(index / 3) * 0.01)),
    })))
  }
  chart.timeScale().fitContent()
}

const applyRealtimeTick = () => {
  if (!holdings.value.length) return
  holdings.value = holdings.value.map((stock) => recalculateStock(stock, createRealtimePrice(stock.current_price)))
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

const loadHoldings = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const response = await getStockHoldings()
    holdings.value = response.data.map(normalizeHolding)
    useMockData.value = false
    if (!holdings.value.length) {
      holdings.value = (await getStocks()).map(normalizeHolding)
      useMockData.value = true
    }
    selectedSymbol.value = holdings.value[0]?.symbol || ''
  } catch {
    holdings.value = (await getStocks()).map(normalizeHolding)
    selectedSymbol.value = holdings.value[0]?.symbol || ''
    useMockData.value = true
  } finally {
    isLoading.value = false
    await nextTick()
    setupChart()
    await loadChart()
    startRealtimeMock()
  }
}

const selectStock = (symbol) => {
  selectedSymbol.value = symbol
}

const chooseSuggestion = (item) => {
  form.keyword = item.name
  if (!form.average_price) form.average_price = String(item.price)
}

const submitHolding = async () => {
  actionMessage.value = ''
  errorMessage.value = ''
  const candidate = findStockCandidate(form.keyword)
  if (!candidate) {
    errorMessage.value = '종목명 또는 종목코드를 후보 목록에서 선택해주세요.'
    return
  }

  let currentPrice = Number(candidate.price || form.average_price || 0)
  try {
    const quote = (await getStockQuote(candidate.symbol)).data
    currentPrice = Number(quote.current_price || quote.price || currentPrice)
  } catch {
    // External quote keys can be absent in local development. Candidate price keeps the flow usable.
  }

  try {
    await createStockHolding({
      symbol: candidate.symbol,
      name: candidate.name,
      quantity: form.quantity,
      average_price: form.average_price || currentPrice,
      current_price: currentPrice,
      memo: form.memo,
    })
    actionMessage.value = `${candidate.name}을 보유 주식에 추가했습니다.`
    Object.assign(form, { keyword: '', quantity: '', average_price: '', memo: '' })
    await loadHoldings()
  } catch (error) {
    errorMessage.value = Object.values(error.response?.data || {}).flat().join(' ') || '보유 주식 추가에 실패했습니다.'
  }
}

const removeHolding = async (stock) => {
  if (!window.confirm(`${stock.name} 보유 정보를 삭제할까요?`)) return
  deletingId.value = stock.id || stock.symbol
  errorMessage.value = ''
  actionMessage.value = ''
  try {
    if (useMockData.value) {
      holdings.value = holdings.value.filter((item) => item.symbol !== stock.symbol)
      selectedSymbol.value = holdings.value[0]?.symbol || ''
    } else {
      await deleteStockHolding(stock.id)
      await loadHoldings()
    }
    actionMessage.value = `${stock.name}을 삭제했습니다.`
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '보유 주식 삭제에 실패했습니다.'
  } finally {
    deletingId.value = null
  }
}

watch(selectedSymbol, loadChart)

onMounted(loadHoldings)

onBeforeUnmount(() => {
  window.clearInterval(pollingTimer)
  resizeObserver?.disconnect()
  chart?.remove()
})
</script>

<template>
  <section class="stock-page page-shell">
    <div class="section-head">
      <div>
        <h1>주식 보유 현황</h1>
        <p>보유 종목을 추가/삭제하고 수익률과 차트를 확인합니다.</p>
      </div>
    </div>

    <p v-if="errorMessage" class="state-card error">{{ errorMessage }}</p>
    <p v-if="actionMessage" class="notice-card">{{ actionMessage }}</p>
    <p v-if="useMockData" class="notice-card">저장된 보유 주식이 없어 예시 데이터로 표시 중입니다.</p>

    <form class="holding-form glass-panel" @submit.prevent="submitHolding">
      <label>
        종목명 또는 코드
        <input v-model.trim="form.keyword" class="form-control" placeholder="예: 삼성전자">
      </label>
      <label>
        수량
        <input v-model="form.quantity" class="form-control" type="number" min="0.0001" step="0.0001" required>
      </label>
      <label>
        평균 매수가
        <input v-model="form.average_price" class="form-control" type="number" min="0" step="1" placeholder="자동 입력 가능">
      </label>
      <label>
        메모
        <input v-model.trim="form.memo" class="form-control" placeholder="선택 입력">
      </label>
      <button class="vintage-button" type="submit">추가</button>

      <div class="suggestions">
        <button v-for="item in suggestions" :key="item.symbol" type="button" @click="chooseSuggestion(item)">
          <strong>{{ item.name }}</strong>
          <span>{{ item.symbol }} · {{ item.market }}</span>
        </button>
      </div>
    </form>

    <div v-if="isLoading" class="state-card">보유 주식 정보를 불러오는 중입니다.</div>

    <template v-else>
      <div class="summary-grid">
        <article class="vintage-card">
          <span>총 매수금액</span>
          <strong>{{ formatCurrency(portfolioSummary.invested) }}</strong>
        </article>
        <article class="vintage-card">
          <span>총 평가금액</span>
          <strong>{{ formatCurrency(portfolioSummary.valuation) }}</strong>
        </article>
        <article class="vintage-card">
          <span>총 수익률</span>
          <strong :class="portfolioSummary.profit >= 0 ? 'positive' : 'negative'">
            {{ formatRate(portfolioProfitRate) }}
          </strong>
        </article>
      </div>

      <div class="stock-layout">
        <aside class="chart-panel glass-panel">
          <div class="chart-header">
            <div>
              <h2>{{ selectedStock?.name || '종목 선택' }}</h2>
              <p>{{ selectedStock?.symbol }}</p>
            </div>
            <div v-if="selectedStock" class="price-block">
              <strong>{{ formatCurrency(selectedStock.current_price) }}</strong>
              <span :class="selectedStock.profit_rate >= 0 ? 'positive' : 'negative'">
                {{ formatRate(selectedStock.profit_rate) }}
              </span>
            </div>
          </div>
          <div ref="chartContainer" class="chart-container"></div>
        </aside>

        <section class="stock-table-wrap vintage-card">
          <div class="table-title">
            <h2>보유 목록</h2>
            <span>5초 mock polling</span>
          </div>

          <div class="stock-list">
            <article
              v-for="stock in holdings"
              :key="stock.symbol"
              class="stock-item"
              :class="{ selected: stock.symbol === selectedStock?.symbol }"
            >
              <button class="stock-select" type="button" @click="selectStock(stock.symbol)">
                <div class="stock-name">
                  <strong>{{ stock.name }}</strong>
                  <small>{{ stock.symbol }}</small>
                </div>
                <div class="stock-metrics">
                  <span>수량 {{ formatQuantity(stock.quantity) }}주</span>
                  <span>현재가 {{ formatCurrency(stock.current_price) }}</span>
                  <b :class="stock.profit_rate >= 0 ? 'positive' : 'negative'">{{ formatRate(stock.profit_rate) }}</b>
                </div>
              </button>
              <button
                class="delete-button"
                type="button"
                :disabled="deletingId === (stock.id || stock.symbol)"
                @click="removeHolding(stock)"
              >
                삭제
              </button>
            </article>
          </div>
        </section>
      </div>
    </template>
  </section>
</template>

<style scoped>
.stock-page {
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

.holding-form {
  display: grid;
  grid-template-columns: 1.1fr 0.6fr 0.8fr 1fr auto;
  gap: 12px;
  padding: 16px;
}

.holding-form label {
  display: grid;
  gap: 6px;
  color: var(--color-muted);
  font-weight: 900;
}

.suggestions {
  grid-column: 1 / -1;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.suggestions button {
  display: inline-grid;
  border: 2px solid rgba(23, 19, 13, 0.18);
  border-radius: 999px;
  background: rgba(255, 248, 231, 0.72);
  color: var(--color-ink);
  padding: 7px 12px;
  text-align: left;
}

.suggestions span {
  color: var(--color-muted);
  font-size: 11px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.summary-grid article {
  display: grid;
  gap: 7px;
  padding: 16px;
}

.summary-grid span {
  color: var(--color-muted);
  font-weight: 900;
}

.summary-grid strong {
  font-size: 25px;
}

.stock-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(360px, 0.65fr);
  gap: 18px;
  align-items: start;
}

.stock-table-wrap,
.chart-panel {
  min-width: 0;
  overflow: hidden;
}

.table-title,
.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  border-bottom: 2px solid var(--color-ink);
  padding: 16px;
}

.table-title h2,
.chart-header h2 {
  margin: 0;
  font-size: 22px;
}

.table-title span,
.chart-header p {
  margin: 0;
  color: var(--color-muted);
  font-weight: 900;
}

.stock-list {
  display: grid;
  gap: 10px;
  padding: 12px;
}

.stock-item {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  align-items: stretch;
  gap: 8px;
  border: 2px solid rgba(23, 19, 13, 0.12);
  border-radius: 18px;
  background: rgba(255, 248, 231, 0.58);
  padding: 8px;
}

.stock-item.selected {
  background: rgba(200, 210, 170, 0.34);
}

.stock-select {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 8px;
  min-width: 0;
  border: 0;
  background: transparent;
  color: var(--color-ink);
  padding: 4px;
  text-align: left;
}

.stock-name {
  display: grid;
  min-width: 0;
}

.stock-name strong,
.stock-name small {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.stock-list small {
  color: var(--color-muted);
}

.stock-metrics {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.stock-metrics span,
.stock-metrics b {
  border-radius: 999px;
  background: rgba(23, 19, 13, 0.07);
  padding: 4px 8px;
  font-size: 12px;
  font-weight: 900;
}

.delete-button {
  align-self: center;
  border: 2px solid var(--color-red);
  border-radius: 999px;
  background: rgba(182, 74, 53, 0.12);
  color: var(--color-red);
  padding: 8px 11px;
  font-size: 12px;
  font-weight: 900;
  white-space: nowrap;
}

.delete-button:disabled {
  opacity: 0.5;
  cursor: wait;
}

.price-block {
  display: grid;
  gap: 4px;
  text-align: right;
}

.price-block strong {
  font-size: 21px;
}

.positive {
  color: var(--color-money);
}

.negative {
  color: var(--color-red);
}

.chart-container {
  width: 100%;
  height: 440px;
}

@media (max-width: 1080px) {
  .holding-form,
  .stock-layout,
  .summary-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 520px) {
  .stock-item {
    grid-template-columns: 1fr;
  }

  .delete-button {
    justify-self: start;
  }
}
</style>
