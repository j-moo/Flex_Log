<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import api from '../api/client'
import { getStocks } from '../api/finance'
import { getExpenses } from '../api/expenses'
import { getMyProfile } from '../api/profile'
import FinanceSummary from '../components/finance/FinanceSummary.vue'
import { formatAmount } from '../utils/format'
import CommodityPricesView from './CommodityPricesView.vue'
import FinanceProductsView from './FinanceProductsView.vue'
import NearbyBanksView from './NearbyBanksView.vue'
import StockHoldingView from './StockHoldingView.vue'
import YoutubeSearchView from './YoutubeSearchView.vue'

const route = useRoute()
const router = useRouter()

const tabs = [
  { id: 'my', label: 'My' },
  { id: 'products', label: '예적금 비교', component: FinanceProductsView },
  { id: 'commodity', label: '현물상품', component: CommodityPricesView },
  { id: 'stocks', label: '주식 보유 현황', component: StockHoldingView },
  { id: 'stock-search', label: '주식정보검색', component: YoutubeSearchView },
  { id: 'map', label: '은행지도', component: NearbyBanksView },
]

const MOCK_PRODUCTS = [
  { id: 'mock-1', bank: '카카오뱅크', name: '카카오뱅크 정기예금', term: 12, rate: 3.4, joined_at: '2026-03-12' },
  { id: 'mock-2', bank: '신한은행', name: '신한 청년적금', term: 24, rate: 4.2, joined_at: '2026-04-03' },
  { id: 'mock-3', bank: 'KB국민은행', name: '국민 자유적금', term: 12, rate: 3.8, joined_at: '2026-05-21' },
]

const activeTab = ref(tabs.some((item) => item.id === route.query.tab) ? route.query.tab : 'my')
const profile = ref(null)
const monthly = ref(null)
const stocks = ref([])
const logs = ref([])
const isLoading = ref(true)

const today = new Date()
const year = today.getFullYear()
const month = today.getMonth()

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
const assetValue = computed(() => stocks.value.reduce((sum, item) => sum + Number(item.valuation_amount || 0), 0))
const monthlySpend = computed(() => Number(monthly.value?.total_amount || 0))

const monthlyLogs = computed(() =>
  logs.value.filter((log) => {
    const date = new Date(log.created_at)
    return date.getFullYear() === year && date.getMonth() === month
  }),
)

const calendarDays = computed(() => {
  const first = new Date(year, month, 1)
  const lastDate = new Date(year, month + 1, 0).getDate()
  const blanks = Array.from({ length: first.getDay() }, (_, index) => ({ key: `blank-${index}`, blank: true }))
  const days = Array.from({ length: lastDate }, (_, index) => {
    const day = index + 1
    const dateKey = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
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

const chooseTab = (id) => {
  activeTab.value = id
  router.replace({ name: 'finance-hub', query: { ...route.query, tab: id } })
}

watch(
  () => route.query.tab,
  (value) => {
    if (tabs.some((item) => item.id === value)) activeTab.value = value
  },
)

onMounted(async () => {
  const results = await Promise.allSettled([
    getMyProfile(),
    api.get('/api/v1/analysis/monthly/'),
    getStocks(),
    getExpenses(),
  ])
  if (results[0].status === 'fulfilled') profile.value = results[0].value.data
  if (results[1].status === 'fulfilled') monthly.value = results[1].value.data
  if (results[2].status === 'fulfilled') stocks.value = results[2].value
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
        {{ tab.label }}
      </button>
    </nav>

    <Transition name="fade-slide" mode="out-in">
      <section v-if="activeTab === 'my'" key="my" class="my-finance">
        <FinanceSummary
          :asset-value="assetValue"
          :monthly-spend="monthlySpend"
          :product-count="displayedProducts.length"
          :stock-count="stocks.length"
        />

        <section class="calendar-panel vintage-card">
          <div class="calendar-head">
            <div>
              <span>MONTHLY FLEX</span>
              <h1>{{ year }}년 {{ month + 1 }}월 소비 달력</h1>
            </div>
            <RouterLink class="vintage-button" :to="{ name: 'analysis' }">소비 AI 분석</RouterLink>
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

          <div class="product-scroll">
            <article v-for="item in displayedProducts" :key="item.id">
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
          <component :is="activeComponent" />
        </KeepAlive>
      </section>
    </Transition>
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
  gap: 8px;
  overflow-x: auto;
  border: 2px solid var(--color-ink);
  border-radius: 999px;
  background: rgba(255, 248, 231, 0.72);
  padding: 7px;
  box-shadow: var(--shadow-soft);
  backdrop-filter: blur(16px);
}

.finance-tabs button {
  flex: 0 0 auto;
  border: 0;
  border-radius: 999px;
  background: transparent;
  color: var(--color-muted);
  padding: 11px 18px;
  font-weight: 900;
  transition: transform 0.16s ease, background 0.16s ease;
}

.finance-tabs button.active {
  background: var(--color-gold);
  color: var(--color-ink);
  box-shadow: inset 0 0 0 2px var(--color-ink);
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
  font-size: 18px;
}

.day-cell span {
  color: var(--color-dark-gold);
  font-size: 13px;
  font-weight: 900;
}

.day-cell small {
  color: var(--color-muted);
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

.product-scroll {
  display: flex;
  gap: 12px;
  overflow-x: auto;
  padding: 2px 2px 8px;
}

.product-scroll article {
  display: grid;
  grid-template-columns: 42px minmax(155px, 1fr) auto;
  align-items: center;
  gap: 10px;
  min-width: 310px;
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

@media (max-width: 760px) {
  .calendar-weekdays,
  .calendar-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .calendar-head {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
