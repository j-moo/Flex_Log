<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import api from '../api/client'
import { getStockHoldings } from '../api/financial'
import { getExpenses } from '../api/expenses'
import { getMyProfile } from '../api/profile'
import ConfirmDialog from '../components/common/ConfirmDialog.vue'
import FinanceSummary from '../components/finance/FinanceSummary.vue'
import { useAccountStore } from '../stores/account'
import { formatAmount } from '../utils/format'
import CommodityPricesView from './CommodityPricesView.vue'
import FinanceProductsView from './FinanceProductsView.vue'
import NearbyBanksView from './NearbyBanksView.vue'
import StockHoldingView from './StockHoldingView.vue'
import YoutubeSearchView from './YoutubeSearchView.vue'
import { getMonthlyIncome, MONTHLY_INCOME_MAX, setMonthlyIncome, validateMonthlyIncome } from '../utils/monthlyIncome'

const route = useRoute()
const router = useRouter()
const account = useAccountStore()

const tabs = [
  {
    id: 'my',
    label: 'My',
    icon: 'M20 12V8H4v4m16 0v8H4v-8m16 0H4m13-6V4a2 2 0 0 0-2-2H9a2 2 0 0 0-2 2v2',
  },
  {
    id: 'products',
    label: '예적금 비교',
    component: FinanceProductsView,
    icon: 'M4 20V10m5 10V4m6 16v-7m5 7V7',
  },
  {
    id: 'commodity',
    label: '현물상품',
    component: CommodityPricesView,
    icon: 'M6 3h12l4 6-10 12L2 9zM6 3l6 18M18 3l-6 18M2 9h20',
  },
  {
    id: 'stocks',
    label: '주식 보유',
    component: StockHoldingView,
    icon: 'M4 19V5m0 14h16M8 15l3-4 3 2 5-7',
  },
  {
    id: 'stock-search',
    label: '주식 검색',
    component: YoutubeSearchView,
    icon: 'M21 21l-4.35-4.35M10.5 18a7.5 7.5 0 1 1 0-15 7.5 7.5 0 0 1 0 15',
  },
  {
    id: 'map',
    label: '은행지도',
    component: NearbyBanksView,
    icon: 'M12 21s7-5.2 7-11a7 7 0 1 0-14 0c0 5.8 7 11 7 11Zm0-8a3 3 0 1 0 0-6 3 3 0 0 0 0 6',
  },
]

const MOCK_PRODUCTS = [
  { id: 'mock-1', bank: '카카오뱅크', name: '카카오뱅크 정기예금', term: 12, rate: 3.4, joined_at: '2026-03-12' },
  { id: 'mock-2', bank: '신한은행', name: '신한 청년적금', term: 24, rate: 4.2, joined_at: '2026-04-03' },
  { id: 'mock-3', bank: 'KB국민은행', name: '국민 자유적금', term: 12, rate: 3.8, joined_at: '2026-05-21' },
]

const activeTab = ref(tabs.some((item) => item.id === route.query.tab) ? route.query.tab : 'my')
const profile = ref(null)
const currentUserId = computed(() => account.user?.id || profile.value?.user_id || null)
const monthly = ref(null)
const stocks = ref([])
const logs = ref([])
const isLoading = ref(true)
const incomeModalOpen = ref(false)
const monthlyIncome = ref(getMonthlyIncome(currentUserId.value))
const incomeForm = ref('')
const incomeErrorDialog = ref({
  open: false,
  message: '',
})
const joinedProductPage = ref(1)
const JOINED_PRODUCT_PAGE_SIZE = 3
const INCOME_INCREMENT_OPTIONS = [
  { label: '100원', value: 100 },
  { label: '500원', value: 500 },
  { label: '1,000원', value: 1000 },
  { label: '1만원', value: 10000 },
  { label: '5만원', value: 50000 },
]

const today = new Date()
const selectedYear = ref(today.getFullYear())
const selectedMonth = ref(today.getMonth())
const monthOptions = Array.from({ length: 12 }, (_, index) => ({ value: index, label: `${index + 1}월` }))

const activeComponent = computed(() => tabs.find((item) => item.id === activeTab.value)?.component)
const realProducts = computed(() =>
  (profile.value?.joined_products || []).map((item) => ({
    id: item.id,
    bank: item.product.kor_co_nm,
    name: item.product.fin_prdt_nm,
    term: item.option.save_trm,
    rate: Number(item.option.intr_rate2 || item.option.intr_rate || 0),
    joined_at: item.joined_at,
    isMock: false,
  })),
)
const displayedProducts = computed(() => (realProducts.value.length ? realProducts.value : MOCK_PRODUCTS))
const joinedProductPageCount = computed(() =>
  Math.max(1, Math.ceil(displayedProducts.value.length / JOINED_PRODUCT_PAGE_SIZE)),
)
const pagedDisplayedProducts = computed(() => {
  const start = (joinedProductPage.value - 1) * JOINED_PRODUCT_PAGE_SIZE
  return displayedProducts.value.slice(start, start + JOINED_PRODUCT_PAGE_SIZE)
})
const assetValue = computed(() => stocks.value.reduce((sum, item) => sum + Number(item.valuation_amount || 0), 0))

const setStocks = (items = []) => {
  stocks.value = Array.isArray(items) ? items : []
}

const loadStocks = async () => {
  try {
    setStocks((await getStockHoldings()).data)
  } catch {
    setStocks([])
  }
}

const monthlyLogs = computed(() =>
  logs.value.filter((log) => {
    const date = new Date(log.created_at)
    return date.getFullYear() === selectedYear.value && date.getMonth() === selectedMonth.value
  }),
)
const monthlySpend = computed(() => monthlyLogs.value.reduce((sum, log) => sum + Number(log.amount || 0), 0))
const maxDailySpend = computed(() => Math.max(0, ...calendarDays.value.filter((item) => !item.blank).map((item) => item.amount)))

const calendarDays = computed(() => {
  const first = new Date(selectedYear.value, selectedMonth.value, 1)
  const lastDate = new Date(selectedYear.value, selectedMonth.value + 1, 0).getDate()
  const monthKey = `${selectedYear.value}-${String(selectedMonth.value + 1).padStart(2, '0')}`
  const blanks = Array.from({ length: first.getDay() }, (_, index) => ({ key: `${monthKey}-blank-${index}`, blank: true }))
  const days = Array.from({ length: lastDate }, (_, index) => {
    const day = index + 1
    const dateKey = `${monthKey}-${String(day).padStart(2, '0')}`
    const dayLogs = monthlyLogs.value.filter((log) => log.created_at?.slice(0, 10) === dateKey)
    const amount = dayLogs.reduce((sum, log) => sum + Number(log.amount || 0), 0)
    return {
      key: dateKey,
      dateKey,
      day,
      amount,
      count: dayLogs.length,
    }
  })
  return [...blanks, ...days]
})

const changeCalendarMonth = (offset) => {
  const next = new Date(selectedYear.value, selectedMonth.value + offset, 1)
  selectedYear.value = next.getFullYear()
  selectedMonth.value = next.getMonth()
}

const goCurrentMonth = () => {
  selectedYear.value = today.getFullYear()
  selectedMonth.value = today.getMonth()
}

const calendarDayStyle = (item) => {
  if (!item.amount || !maxDailySpend.value) return {}
  const ratio = Math.min(1, item.amount / Math.max(maxDailySpend.value, 100000))
  const lightness = Math.round(96 - ratio * 22)
  const saturation = Math.round(42 + ratio * 28)
  const alpha = 0.24 + ratio * 0.42
  return {
    backgroundColor: `hsla(6, ${saturation}%, ${lightness}%, ${alpha})`,
    borderColor: `hsla(6, ${Math.min(95, saturation + 8)}%, ${Math.max(34, lightness - 18)}%, 0.72)`,
    '--day-text': 'var(--color-ink)',
    '--day-subtext': 'var(--color-muted)',
    '--day-amount': 'var(--color-dark-gold)',
  }
}

const chooseTab = (id) => {
  activeTab.value = id
  router.replace({ name: 'finance-hub', query: { ...route.query, tab: id } })
}

const openIncomeModal = () => {
  incomeForm.value = monthlyIncome.value ? String(monthlyIncome.value) : ''
  incomeModalOpen.value = true
}

const closeIncomeModal = () => {
  incomeModalOpen.value = false
  incomeForm.value = ''
}

const addIncomeAmount = (amount) => {
  const currentAmount = Math.round(Number(incomeForm.value || 0))
  incomeForm.value = String(Math.max(0, currentAmount + amount))
}

const saveIncome = () => {
  const result = validateMonthlyIncome(incomeForm.value)
  if (!result.valid) {
    incomeErrorDialog.value = {
      open: true,
      message: result.message,
    }
    return
  }
  monthlyIncome.value = setMonthlyIncome(result.amount, currentUserId.value)
  closeIncomeModal()
}

const closeIncomeError = () => {
  incomeErrorDialog.value = {
    open: false,
    message: '',
  }
}

watch(
  () => route.query.tab,
  (value) => {
    if (tabs.some((item) => item.id === value)) activeTab.value = value
  },
)

watch(activeTab, (value) => {
  if (value === 'my') loadStocks()
})

watch(currentUserId, (userId) => {
  monthlyIncome.value = getMonthlyIncome(userId)
})

watch(displayedProducts, () => {
  joinedProductPage.value = 1
})

watch(joinedProductPageCount, (pageCount) => {
  if (joinedProductPage.value > pageCount) joinedProductPage.value = pageCount
})

onMounted(async () => {
  const results = await Promise.allSettled([
    getMyProfile(),
    api.get('/api/v1/analysis/monthly/'),
    getStockHoldings(),
    getExpenses(),
  ])
  if (results[0].status === 'fulfilled') profile.value = results[0].value.data
  if (results[1].status === 'fulfilled') monthly.value = results[1].value.data
  if (results[2].status === 'fulfilled') setStocks(results[2].value.data)
  if (results[3].status === 'fulfilled') logs.value = results[3].value.data
  isLoading.value = false
})
</script>

<template>
  <section class="finance-page">
    <nav class="finance-tabs" aria-label="금융 탭">
      <button
        v-for="tab in tabs"
        :key="tab.id"
        type="button"
        :class="{ active: activeTab === tab.id }"
        @click="chooseTab(tab.id)"
      >
        <svg viewBox="0 0 24 24" aria-hidden="true">
          <path :d="tab.icon" />
        </svg>
        <span>{{ tab.label }}</span>
      </button>
    </nav>

    <Transition name="fade-slide" mode="out-in">
      <section v-if="activeTab === 'my'" key="my" class="my-finance">
        <FinanceSummary
          :asset-value="assetValue"
          :monthly-spend="monthlySpend"
          :product-count="displayedProducts.length"
          :stock-count="stocks.length"
          :monthly-income="monthlyIncome"
          @edit-income="openIncomeModal"
        />

        <section class="calendar-panel vintage-card">
          <div class="calendar-head">
            <div>
              <span>MONTHLY FLEX</span>
              <h1>{{ selectedYear }}년 {{ selectedMonth + 1 }}월 소비 달력</h1>
            </div>
            <div class="calendar-tools">
              <button type="button" aria-label="이전 달" @click="changeCalendarMonth(-1)">‹</button>
              <input v-model.number="selectedYear" type="number" min="2000" max="2100" aria-label="연도 선택">
              <select v-model.number="selectedMonth" aria-label="월 선택">
                <option v-for="item in monthOptions" :key="item.value" :value="item.value">{{ item.label }}</option>
              </select>
              <button type="button" aria-label="다음 달" @click="changeCalendarMonth(1)">›</button>
              <button type="button" @click="goCurrentMonth">이번 달</button>
              <RouterLink class="vintage-button" :to="{ name: 'analysis' }">소비 AI 분석</RouterLink>
            </div>
          </div>

          <div class="calendar-weekdays">
            <span v-for="day in ['일', '월', '화', '수', '목', '금', '토']" :key="day">{{ day }}</span>
          </div>

          <div class="calendar-grid">
            <template v-for="item in calendarDays" :key="item.key">
              <span v-if="item.blank" class="calendar-blank"></span>
              <RouterLink
                v-else
                class="day-cell"
                :class="{ active: item.amount > 0 }"
                :style="calendarDayStyle(item)"
                :to="{ name: 'finance-day', params: { date: item.dateKey } }"
              >
                <strong>{{ item.day }}</strong>
                <span>{{ item.amount ? formatAmount(item.amount) : '0원' }}</span>
                <small v-if="item.count">{{ item.count }}건</small>
              </RouterLink>
            </template>
          </div>
        </section>

        <section class="joined-strip glass-panel">
          <div class="strip-head">
            <div>
              <span>MY PRODUCTS</span>
              <h2>가입상품</h2>
            </div>
            <small v-if="!realProducts.length">예시 데이터</small>
          </div>

          <div v-if="joinedProductPageCount > 1" class="product-pager">
            <button
              type="button"
              :disabled="joinedProductPage <= 1"
              aria-label="이전 가입상품"
              @click="joinedProductPage -= 1"
            >
              ‹
            </button>
            <span>{{ joinedProductPage }} / {{ joinedProductPageCount }}</span>
            <button
              type="button"
              :disabled="joinedProductPage >= joinedProductPageCount"
              aria-label="다음 가입상품"
              @click="joinedProductPage += 1"
            >
              ›
            </button>
          </div>

          <div class="product-scroll">
            <article v-for="item in pagedDisplayedProducts" :key="item.id">
              <span class="bank-icon">{{ item.bank.slice(0, 1) }}</span>
              <div>
                <small>{{ item.bank }}</small>
                <strong>{{ item.name }}</strong>
                <p>{{ item.term }}개월 · 가입일 {{ new Date(item.joined_at).toLocaleDateString('ko-KR') }}</p>
              </div>
              <b>{{ item.rate.toFixed(2) }}%</b>
            </article>
          </div>
        </section>
      </section>

      <section v-else :key="activeTab" class="tab-panel">
        <KeepAlive>
          <component :is="activeComponent" @holdings-changed="setStocks" />
        </KeepAlive>
      </section>
    </Transition>

    <Teleport to="body">
      <div v-if="incomeModalOpen" class="income-backdrop" @click.self="closeIncomeModal">
        <form class="income-modal vintage-card" @submit.prevent="saveIncome">
          <header>
            <div>
              <span>MONTHLY INCOME</span>
              <h2>월 수입 입력</h2>
              <p>이번 달 소비 분석과 위험도 평가에 반영됩니다.</p>
            </div>
            <button type="button" aria-label="닫기" @click="closeIncomeModal">×</button>
          </header>
          <label>
            월 수입
            <input
              v-model="incomeForm"
              class="form-control"
              type="number"
              min="0"
              :max="MONTHLY_INCOME_MAX"
              step="1000"
              placeholder="예: 3000000"
              autofocus
            >
          </label>
          <div class="income-quick" aria-label="월 수입 빠른 입력">
            <button
              v-for="option in INCOME_INCREMENT_OPTIONS"
              :key="option.value"
              type="button"
              @click="addIncomeAmount(option.value)"
            >
              +{{ option.label }}
            </button>
          </div>
          <div class="income-actions">
            <button type="button" class="ghost-button" @click="closeIncomeModal">취소</button>
            <button class="vintage-button">저장</button>
          </div>
        </form>
      </div>

      <ConfirmDialog
        :open="incomeErrorDialog.open"
        title="월 수입 확인"
        :message="incomeErrorDialog.message"
        detail="상한을 넘는 큰 숫자는 분석 결과를 왜곡할 수 있어 저장하지 않습니다."
        confirm-text="확인"
        cancel-text="닫기"
        tone="notice"
        @close="closeIncomeError"
        @confirm="closeIncomeError"
      />
    </Teleport>
  </section>
</template>

<style scoped>
.finance-page {
  display: grid;
  gap: 18px;
}

.finance-tabs {
  position: sticky;
  top: 88px;
  z-index: 50;
  display: flex;
  gap: 10px;
  overflow-x: auto;
  border: 2px solid var(--color-ink);
  border-radius: 999px;
  background: rgba(255, 248, 231, 0.72);
  padding: 8px;
  box-shadow: var(--shadow-soft);
  backdrop-filter: blur(16px);
}

.finance-tabs button {
  position: relative;
  display: grid;
  width: 84px;
  min-height: 72px;
  place-items: center;
  flex: 0 0 auto;
  overflow: hidden;
  border: 2px solid transparent;
  border-radius: 999px;
  background: transparent;
  color: var(--color-muted);
  padding: 10px;
  font-weight: 900;
  transition: transform 0.18s ease, background 0.18s ease, border-color 0.18s ease, box-shadow 0.18s ease;
}

.finance-tabs svg {
  width: 29px;
  height: 29px;
  fill: none;
  stroke: currentColor;
  stroke-linecap: round;
  stroke-linejoin: round;
  stroke-width: 2;
  transition: transform 0.18s ease;
}

.finance-tabs span {
  position: absolute;
  right: 8px;
  bottom: 8px;
  left: 8px;
  opacity: 0;
  color: var(--color-ink);
  font-size: 11.5px;
  line-height: 1.05;
  text-align: center;
  transform: translateY(10px);
  transition: opacity 0.18s ease, transform 0.18s ease;
}

.finance-tabs button:hover,
.finance-tabs button.active {
  border-color: var(--color-ink);
  background: var(--color-paper);
  color: var(--color-ink);
  box-shadow: 3px 3px 0 var(--color-ink);
  transform: translateY(-2px);
}

.finance-tabs button:hover svg,
.finance-tabs button.active svg {
  transform: translateY(-8px);
}

.finance-tabs button:hover span,
.finance-tabs button.active span {
  opacity: 1;
  transform: translateY(0);
}

.my-finance {
  display: grid;
  gap: 18px;
}

.calendar-panel {
  display: grid;
  gap: 14px;
  padding: 20px;
}

.calendar-head,
.strip-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.calendar-tools {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 8px;
}

.calendar-tools button,
.calendar-tools input,
.calendar-tools select {
  border: 2px solid var(--color-ink);
  border-radius: 999px;
  background: var(--color-paper);
  color: var(--color-ink);
  padding: 8px 11px;
  font-weight: 900;
}

.calendar-tools input {
  width: 96px;
}

.calendar-tools button {
  min-width: 38px;
}

.calendar-head span,
.strip-head span {
  color: var(--color-dark-gold);
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0.12em;
}

.calendar-head h1,
.strip-head h2 {
  margin: 4px 0 0;
  font-size: 25px;
}

.calendar-weekdays,
.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 8px;
}

.calendar-weekdays span {
  color: var(--color-muted);
  font-size: 12px;
  font-weight: 900;
  text-align: center;
}

.calendar-blank,
.day-cell {
  min-height: 92px;
}

.day-cell {
  display: grid;
  align-content: start;
  gap: 5px;
  border: 2px solid rgba(23, 19, 13, 0.18);
  border-radius: 18px;
  background: rgba(255, 248, 231, 0.72);
  padding: 10px;
  transition: transform 0.18s ease, background 0.18s ease, box-shadow 0.18s ease;
}

.day-cell:hover {
  z-index: 2;
  background: var(--color-paper);
  box-shadow: 5px 5px 0 var(--color-ink);
  transform: scale(1.08);
}

.day-cell.active {
  background: rgba(200, 210, 170, 0.42);
}

.day-cell strong {
  color: var(--day-text, var(--color-ink));
  font-size: 18px;
}

.day-cell span {
  color: var(--day-amount, var(--color-dark-gold));
  font-size: 13px;
  font-weight: 900;
}

.day-cell small {
  color: var(--day-subtext, var(--color-muted));
}

.joined-strip {
  min-width: 0;
  padding: 18px;
}

.strip-head {
  margin-bottom: 14px;
}

.strip-head small {
  border: 2px solid var(--color-ink);
  border-radius: 999px;
  background: var(--color-money-light);
  padding: 4px 9px;
  font-weight: 900;
}

.product-pager {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 8px;
  margin-bottom: 10px;
}

.product-pager button {
  display: grid;
  width: 32px;
  height: 32px;
  place-items: center;
  border: 2px solid var(--color-ink);
  border-radius: 50%;
  background: var(--color-paper);
  color: var(--color-ink);
  padding: 0;
  font-size: 22px;
  font-weight: 900;
  line-height: 1;
}

.product-pager button:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.product-pager span {
  color: var(--color-muted);
  font-size: 12px;
  font-weight: 900;
}

.product-scroll {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(min(100%, 300px), 1fr));
  gap: 12px;
  padding: 2px;
}

.product-scroll article {
  display: grid;
  grid-template-columns: 42px minmax(0, 1fr) auto;
  align-items: center;
  gap: 10px;
  min-width: 0;
  border: 2px solid rgba(23, 19, 13, 0.16);
  border-radius: 18px;
  background: rgba(255, 248, 231, 0.68);
  padding: 13px;
}

.bank-icon {
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

.product-scroll article > div {
  display: grid;
  min-width: 0;
}

.product-scroll small,
.product-scroll p {
  overflow: hidden;
  margin: 0;
  color: var(--color-muted);
  font-size: 12px;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-scroll strong {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-scroll b {
  color: var(--color-dark-gold);
  font-size: 18px;
}

.tab-panel :deep(> section) {
  width: 100%;
  max-width: none;
  margin: 0;
}

.income-backdrop {
  position: fixed;
  inset: 0;
  z-index: 140;
  display: grid;
  place-items: center;
  background: rgba(23, 19, 13, 0.34);
  padding: 18px;
  backdrop-filter: blur(10px);
}

.income-modal {
  display: grid;
  gap: 16px;
  width: min(100%, 440px);
  padding: 20px;
}

.income-modal header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 14px;
}

.income-modal header span {
  color: var(--color-dark-gold);
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0.12em;
}

.income-modal h2,
.income-modal p {
  margin: 0;
}

.income-modal p,
.income-modal label {
  color: var(--color-muted);
}

.income-modal label {
  display: grid;
  gap: 6px;
  font-weight: 900;
}

.income-quick {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.income-quick button {
  border: 2px solid var(--color-ink);
  border-radius: 999px;
  background: rgba(200, 210, 170, 0.48);
  color: var(--color-ink);
  padding: 8px 11px;
  font-size: 12px;
  font-weight: 900;
}

.income-modal header > button,
.ghost-button {
  border: 2px solid var(--color-ink);
  border-radius: 999px;
  background: var(--color-paper);
  color: var(--color-ink);
  font-weight: 900;
}

.income-modal header > button {
  width: 36px;
  height: 36px;
  padding: 0;
  font-size: 24px;
  line-height: 1;
}

.income-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

@media (max-width: 900px) {
  .product-scroll {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 760px) {
  .calendar-weekdays,
  .calendar-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .calendar-head {
    align-items: flex-start;
    flex-direction: column;
  }

  .calendar-tools {
    justify-content: flex-start;
    width: 100%;
  }
}
</style>
