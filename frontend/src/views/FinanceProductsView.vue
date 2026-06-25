<script setup>
import { computed, onBeforeUnmount, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import api from '../api/client'
import { getSubscriptions, joinProduct as requestJoinProduct } from '../api/financial'
import { formatRate } from '../utils/format'

const DEFAULT_SORT = 'max_rate_desc'
const PRODUCT_PAGE_SIZE = 6
const router = useRouter()

const LEADS = { G: 0, GG: 1, N: 2, D: 3, DD: 4, R: 5, M: 6, B: 7, BB: 8, S: 9, SS: 10, NG: 11, J: 12, JJ: 13, C: 14, K: 15, T: 16, P: 17, H: 18 }
const VOWELS = { A: 0, AE: 1, YA: 2, YAE: 3, EO: 4, E: 5, YEO: 6, YE: 7, O: 8, WA: 9, WAE: 10, OE: 11, YO: 12, U: 13, WEO: 14, WE: 15, WI: 16, YU: 17, EU: 18, YI: 19, I: 20 }
const TAILS = { '': 0, G: 1, GG: 2, GS: 3, N: 4, NJ: 5, NH: 6, D: 7, L: 8, LG: 9, LM: 10, LB: 11, LS: 12, LT: 13, LP: 14, LH: 15, M: 16, B: 17, BS: 18, S: 19, SS: 20, NG: 21, J: 22, C: 23, K: 24, T: 25, P: 26, H: 27 }
const ko = (...parts) => parts.map((part) => {
  if (!part.includes('-')) return part
  const [lead, vowel, tail = ''] = part.split('-')
  if (LEADS[lead] === undefined || VOWELS[vowel] === undefined || TAILS[tail] === undefined) return part
  return String.fromCharCode(0xac00 + ((LEADS[lead] * 21 + VOWELS[vowel]) * 28) + TAILS[tail])
}).join('')

const text = {
  all: ko('J-EO-N', 'C-E'),
  allPeriod: ko('J-EO-N', 'C-E', ' ', 'G-I', 'G-A-N'),
  aiAnalyzing: ko('AI', 'G-A', ' ', 'S-O', 'B-I', ' ', 'P-AE', 'T-EO-N', 'G-WA', ' ', 'G-EU-M', 'NG-YU-NG', 'S-A-NG', 'P-U-M', 'NG-EU-L', ' ', 'B-U-N', 'S-EO-G', ' ', 'J-U-NG', 'NG-I-B', 'N-I', 'D-A', '...'),
  aiButton: ko('N-AE', ' ', 'S-O', 'B-I', 'P-AE', 'T-EO-N', ' ', 'G-I', 'J-U-N', ' ', 'AI', ' ', 'C-U', 'C-EO-N'),
  aiComment: ko('AI', ' ', 'K-O', 'M-E-N', 'T-EU'),
  aiLoading: ko('AI', ' ', 'B-U-N', 'S-EO-G', ' ', 'J-U-NG', '...'),
  aiRecommendation: ko('AI', ' ', 'C-U', 'C-EO-N'),
  aiResultTitle: ko('S-O', 'B-I', 'P-AE', 'T-EO-N', ' ', 'G-I', 'J-U-N', ' ', 'C-U', 'C-EO-N', ' ', 'G-YEO-L', 'G-WA'),
  bankInfoMissing: ko('NG-EU-N', 'H-AE-NG', ' ', 'J-EO-NG', 'B-O', ' ', 'NG-EO-B', 'S-EU-M'),
  bankName: ko('NG-EU-N', 'H-AE-NG', 'M-YEO-NG'),
  bankSearch: ko('NG-EU-N', 'H-AE-NG', 'M-YEO-NG', ' ', 'G-EO-M', 'S-AE-G'),
  base: ko('G-I', 'B-O-N'),
  baseRate: ko('G-I', 'B-O-N', 'G-EU-M', 'R-I'),
  baseRateAsc: ko('G-I', 'B-O-N', 'G-EU-M', 'R-I', ' ', 'N-A-J', 'NG-EU-N', 'S-U-N'),
  baseRateDesc: ko('G-I', 'B-O-N', 'G-EU-M', 'R-I', ' ', 'N-O-P', 'NG-EU-N', 'S-U-N'),
  caution: ko('B-O-N', ' ', 'C-U', 'C-EO-N', 'NG-EU-N', ' ', 'C-A-M', 'G-O', 'NG-YO-NG', 'NG-I', 'M-YEO', ', ', 'S-I-L', 'J-E', ' ', 'G-A', 'NG-I-B', ' ', 'J-EO-N', ' ', 'G-EU-M', 'NG-YU-NG', 'H-OE', 'S-A', ' ', 'G-O-NG', 'S-I-G', ' ', 'J-EO-NG', 'B-O', 'R-EU-L', ' ', 'H-WA-G', 'NG-I-N', 'H-AE', 'NG-YA', ' ', 'H-A-B', 'N-I', 'D-A', '.'),
  clear: ko('C-O', 'G-I', 'H-WA'),
  defaultRecommendationReason: ko('S-O', 'B-I', ' ', 'P-AE', 'T-EO-N', 'G-WA', ' ', 'S-A-NG', 'P-U-M', ' ', 'J-O', 'G-EO-N', 'NG-EU-L', ' ', 'G-I', 'J-U-N', 'NG-EU', 'R-O', ' ', 'S-EO-N', 'B-YEO-L', 'D-OE-N', ' ', 'S-A-NG', 'P-U-M', 'NG-I-B', 'N-I', 'D-A', '.'),
  defaultRecommendationTitle: ko('C-U', 'C-EO-N', ' ', 'S-A-NG', 'P-U-M'),
  deposit: ko('NG-YE', 'G-EU-M'),
  depositFull: ko('J-EO-NG', 'G-I', 'NG-YE', 'G-EU-M'),
  detailActive: ko('S-A-NG', 'S-E', ' ', 'H-WA-G', 'NG-I-N', ' ', 'J-U-NG'),
  emptyProducts: ko('J-O', 'G-EO-N', 'NG-E', ' ', 'M-A-J', 'N-EU-N', ' ', 'G-EU-M', 'NG-YU-NG', 'S-A-NG', 'P-U-M', 'NG-I', ' ', 'NG-EO-B', 'S-EU-B', 'N-I', 'D-A', '.\n', 'P-I-L', 'T-EO', ' ', 'J-O', 'G-EO-N', 'NG-EU-L', ' ', 'J-U-L', 'NG-I', 'G-EO', 'N-A', ' ', 'D-A', 'R-EU-N', ' ', 'NG-EU-N', 'H-AE-NG', 'M-YEO-NG', 'NG-EU-L', ' ', 'G-EO-M', 'S-AE-G', 'H-AE', 'B-O', 'S-E', 'NG-YO', '.'),
  financeProduct: ko('G-EU-M', 'NG-YU-NG', 'S-A-NG', 'P-U-M'),
  highest: ko('C-OE', 'G-O'),
  internet: ko('NG-I-N', 'T-EO', 'N-E-S'),
  join: ko('G-A', 'NG-I-B'),
  joinedProduct: ko('S-A-NG', 'P-U-M', 'NG-E', ' ', 'G-A', 'NG-I-B', 'H-AE-SS', 'S-EU-B', 'N-I', 'D-A', '.'),
  joinFail: ko('S-A-NG', 'P-U-M', ' ', 'G-A', 'NG-I-B', 'NG-E', ' ', 'S-I-L', 'P-AE', 'H-AE-SS', 'S-EU-B', 'N-I', 'D-A', '.'),
  joining: ko('G-A', 'NG-I-B', ' ', 'J-U-NG'),
  joinNow: ko('G-A', 'NG-I-B', 'H-A', 'G-I'),
  joinWay: ko('G-A', 'NG-I-B', ' ', 'B-A-NG', 'B-EO-B'),
  maxLimit: ko('C-OE', 'D-AE', ' ', 'H-A-N', 'D-O'),
  maxRate: ko('C-OE', 'G-O', 'G-EU-M', 'R-I'),
  maxRateAsc: ko('C-OE', 'G-O', 'G-EU-M', 'R-I', ' ', 'N-A-J', 'NG-EU-N', 'S-U-N'),
  maxRateDesc: ko('C-OE', 'G-O', 'G-EU-M', 'R-I', ' ', 'N-O-P', 'NG-EU-N', 'S-U-N'),
  mobile: ko('S-EU', 'M-A', 'T-EU', 'P-O-N'),
  month: ko('G-AE', 'NG-WEO-L'),
  noLimit: ko('H-A-N', 'D-O', ' ', 'NG-EO-B', 'S-EU-M'),
  noSpecialCondition: ko('NG-U', 'D-AE', 'J-O', 'G-EO-N', ' ', 'J-EO-NG', 'B-O', 'G-A', ' ', 'NG-EO-B', 'S-EU-B', 'N-I', 'D-A', '.'),
  offlineBranch: ko('NG-YEO-NG', 'NG-EO-B', 'J-EO-M'),
  pageDescription: ko('J-O', 'G-EO-N', 'NG-E', ' ', 'M-A-J', 'N-EU-N', ' ', 'G-EU-M', 'NG-YU-NG', 'S-A-NG', 'P-U-M', 'NG-EU-L', ' ', 'B-I', 'G-YO', 'H-A', 'S-E', 'NG-YO', '.'),
  pageTitle: ko('NG-YE', 'J-EO-G', 'G-EU-M', ' ', 'B-I', 'G-YO'),
  period: ko('G-I', 'G-A-N'),
  productCountSuffix: ko('G-AE', ' ', 'S-A-NG', 'P-U-M'),
  productFetchError: ko('G-EU-M', 'NG-YU-NG', 'S-A-NG', 'P-U-M', ' ', 'J-EO-NG', 'B-O', 'R-EU-L', ' ', 'B-U-L', 'R-EO', 'NG-O', 'J-I', ' ', 'M-O-S', 'H-AE-SS', 'S-EU-B', 'N-I', 'D-A', '.\n', 'J-A-M', 'S-I', ' ', 'H-U', ' ', 'D-A', 'S-I', ' ', 'S-I', 'D-O', 'H-AE', 'J-U', 'S-E', 'NG-YO', '.'),
  productLoading: ko('S-A-NG', 'P-U-M', 'NG-EU-L', ' ', 'B-U-L', 'R-EO', 'NG-O', 'N-EU-N', ' ', 'J-U-NG', 'NG-I-B', 'N-I', 'D-A', '.'),
  productPage: ko('S-A-NG', 'P-U-M', ' ', 'P-E', 'NG-I', 'J-I'),
  query: ko('J-O', 'H-OE'),
  recommendationFailure: ko('AI', ' ', 'C-U', 'C-EO-N', 'NG-EU-L', ' ', 'B-U-L', 'R-EO', 'NG-O', 'J-I', ' ', 'M-O-S', 'H-AE-SS', 'S-EU-B', 'N-I', 'D-A', '.\n', 'S-O', 'B-I', ' ', 'B-U-N', 'S-EO-G', ' ', 'D-E', 'NG-I', 'T-EO', 'G-A', ' ', 'B-U', 'J-O-G', 'H-A', 'G-EO', 'N-A', ' ', 'G-EU-M', 'NG-YU-NG', 'S-A-NG', 'P-U-M', ' ', 'D-E', 'NG-I', 'T-EO', 'G-A', ' ', 'NG-EO-B', 'S-EU-L', ' ', 'S-U', ' ', 'NG-I-SS', 'S-EU-B', 'N-I', 'D-A', '.'),
  recommendationReason: ko('C-U', 'C-EO-N', ' ', 'NG-I', 'NG-YU'),
  resultSummary: ko('J-O', 'G-EO-N', 'NG-E', ' ', 'M-A-J', 'N-EU-N', ' ', 'NG-YE', 'J-EO-G', 'G-EU-M', ' ', 'S-A-NG', 'P-U-M', 'NG-I-B', 'N-I', 'D-A', '.'),
  saving: ko('J-EO-G', 'G-EU-M'),
  savingFull: ko('J-EO-NG', 'G-I', 'J-EO-G', 'G-EU-M'),
  searchSpecialCondition: ko('NG-U', 'D-AE', 'J-O', 'G-EO-N', ' ', 'B-O', 'G-I'),
  sort: ko('J-EO-NG', 'R-YEO-L'),
  specialCondition: ko('NG-U', 'D-AE', 'J-O', 'G-EO-N'),
  term: ko('J-EO', 'C-U-G', ' ', 'G-I', 'G-A-N'),
  typeGroup: ko('NG-YE', 'G-EU-M', ' ', 'J-EO-G', 'G-EU-M', ' ', 'G-U', 'B-U-N'),
  next: ko('D-A', 'NG-EU-M'),
  previous: ko('NG-I', 'J-EO-N'),
  processing: ko('C-EO', 'R-I', ' ', 'J-U-NG'),
  maturityInterest: ko('M-A-N', 'G-I', ' ', 'H-U', ' ', 'NG-I', 'J-A', 'NG-YU-L'),
  won: ko('NG-WEO-N'),
}

const TYPE_LABELS = {
  deposit: text.depositFull,
  saving: text.savingFull,
}

const products = ref([])
const selectedProduct = ref(null)
const subscriptions = ref([])
const isLoading = ref(false)
const isRecommending = ref(false)
const errorMessage = ref('')
const actionMessage = ref('')
const joiningOptionId = ref(null)
const productPage = ref(1)
let bankSearchTimer = null
let productRequestId = 0

const filters = reactive({
  type: '',
  bank: '',
  term: '',
  sort: DEFAULT_SORT,
  join_way: '',
})

const typeOptions = [
  { label: text.all, value: '' },
  { label: text.deposit, value: 'deposit' },
  { label: text.saving, value: 'saving' },
]

const termOptions = [
  { label: text.allPeriod, value: '' },
  { label: `6${text.month}`, value: '6' },
  { label: `12${text.month}`, value: '12' },
  { label: `24${text.month}`, value: '24' },
  { label: `36${text.month}`, value: '36' },
]

const sortOptions = [
  { label: text.baseRateDesc, value: 'base_rate_desc' },
  { label: text.baseRateAsc, value: 'base_rate_asc' },
  { label: text.maxRateDesc, value: 'max_rate_desc' },
  { label: text.maxRateAsc, value: 'max_rate_asc' },
]

const joinWayOptions = [
  { label: text.all, value: '' },
  { label: text.offlineBranch, value: text.offlineBranch },
  { label: text.internet, value: text.internet },
  { label: text.mobile, value: text.mobile },
]

const hasFilters = computed(() => (
  filters.type !== ''
  || filters.bank.trim() !== ''
  || filters.term !== ''
  || filters.join_way !== ''
  || filters.sort !== DEFAULT_SORT
))

const activeOptionIds = computed(() => new Set(
  subscriptions.value
    .filter((item) => item.status === 'active' && item.option?.id)
    .map((item) => item.option.id),
))

const productPageCount = computed(() => Math.max(1, Math.ceil(products.value.length / PRODUCT_PAGE_SIZE)))
const pagedProducts = computed(() => {
  const start = (productPage.value - 1) * PRODUCT_PAGE_SIZE
  return products.value.slice(start, start + PRODUCT_PAGE_SIZE)
})

const requestParams = computed(() => {
  const params = {}
  Object.entries(filters).forEach(([key, value]) => {
    const normalized = String(value || '').trim()
    if (normalized) params[key] = normalized
  })
  return params
})

const productTypeLabel = (product) => product?.product_type_label || TYPE_LABELS[product?.product_type] || text.financeProduct
const formatLimit = (value) => (!value ? text.noLimit : `${Number(value).toLocaleString('ko-KR')}${text.won}`)
const optionRate = (option) => Number(option?.intr_rate2 ?? option?.intr_rate ?? 0)
const bestOption = (product) => {
  if (product?.best_option) return product.best_option
  const options = [...(product?.options || [])]
  return options.sort((a, b) => optionRate(b) - optionRate(a))[0] || null
}
const displayBaseRate = (product) => product?.base_rate ?? bestOption(product)?.intr_rate
const displayMaxRate = (product) => product?.max_rate ?? bestOption(product)?.intr_rate2 ?? bestOption(product)?.intr_rate
const productTerms = (product) => {
  if (product?.terms?.length) return product.terms
  const terms = new Set((product?.options || []).map((option) => String(option.save_trm || '')).filter(Boolean))
  return [...terms].sort((a, b) => Number(a) - Number(b))
}
const summarizeText = (value) => {
  const normalized = String(value || '').replace(/\s+/g, ' ').trim()
  if (!normalized) return text.noSpecialCondition
  return normalized.length > 96 ? `${normalized.slice(0, 96)}...` : normalized
}
const selectProduct = (product) => {
  selectedProduct.value = product
}

const fetchProducts = async () => {
  const currentRequestId = ++productRequestId
  isLoading.value = true
  errorMessage.value = ''
  try {
    const response = await api.get('/api/v1/finance/products/', { params: requestParams.value })
    if (currentRequestId !== productRequestId) return
    products.value = response.data
    productPage.value = 1
    selectedProduct.value = pagedProducts.value[0] || null
  } catch {
    if (currentRequestId !== productRequestId) return
    products.value = []
    selectedProduct.value = null
    errorMessage.value = text.productFetchError
  } finally {
    if (currentRequestId === productRequestId) isLoading.value = false
  }
}

const fetchSubscriptions = async () => {
  try {
    subscriptions.value = (await getSubscriptions()).data
  } catch {
    subscriptions.value = []
  }
}

const setTypeFilter = (type) => {
  if (filters.type === type) return
  filters.type = type
  fetchProducts()
}

const submitFilters = () => {
  if (bankSearchTimer) window.clearTimeout(bankSearchTimer)
  fetchProducts()
}

const scheduleBankSearch = () => {
  if (bankSearchTimer) window.clearTimeout(bankSearchTimer)
  bankSearchTimer = window.setTimeout(fetchProducts, 420)
}

const clearFilters = () => {
  if (bankSearchTimer) window.clearTimeout(bankSearchTimer)
  filters.type = ''
  filters.bank = ''
  filters.term = ''
  filters.sort = DEFAULT_SORT
  filters.join_way = ''
  fetchProducts()
}

const setProductPage = (page) => {
  productPage.value = Math.min(Math.max(1, page), productPageCount.value)
  selectedProduct.value = pagedProducts.value[0] || null
}

const requestRecommendation = async () => {
  isRecommending.value = true
  try {
    await router.push({ name: 'finance-recommend', query: { auto: '1', t: Date.now() } })
  } catch {
    errorMessage.value = text.recommendationFailure
  } finally {
    isRecommending.value = false
  }
}

const subscribe = async (product, option) => {
  joiningOptionId.value = option.id
  actionMessage.value = ''
  try {
    await requestJoinProduct(option.id)
    await fetchSubscriptions()
    actionMessage.value = `${product.fin_prdt_nm} ${option.save_trm}${text.month} ${text.joinedProduct}`
  } catch (error) {
    actionMessage.value = error.response?.data?.detail || text.joinFail
  } finally {
    joiningOptionId.value = null
  }
}

onMounted(() => Promise.all([fetchProducts(), fetchSubscriptions()]))
onBeforeUnmount(() => {
  if (bankSearchTimer) window.clearTimeout(bankSearchTimer)
})
</script>

<template>
  <section class="products-page page-shell">
    <div class="section-head">
      <div>
        <h1>{{ text.pageTitle }}</h1>
        <p>{{ text.pageDescription }}</p>
      </div>
      <button class="vintage-button ai-button" type="button" :disabled="isRecommending" @click="requestRecommendation">
        {{ isRecommending ? text.aiLoading : text.aiButton }}
      </button>
    </div>

    <form class="filter-panel glass-panel" @submit.prevent="submitFilters">
      <div class="type-toggle" role="group" :aria-label="text.typeGroup">
        <button v-for="option in typeOptions" :key="option.value || 'all'" type="button"
          :class="{ active: filters.type === option.value }" @click="setTypeFilter(option.value)">
          {{ option.label }}
        </button>
      </div>

      <label class="filter-field bank-search">
        <span>{{ text.bankName }}</span>
        <input v-model="filters.bank" class="form-control" type="search" :placeholder="text.bankSearch"
          @input="scheduleBankSearch">
      </label>

      <label class="filter-field">
        <span>{{ text.term }}</span>
        <select v-model="filters.term" class="form-select" @change="fetchProducts">
          <option v-for="option in termOptions" :key="option.value || 'all-term'" :value="option.value">
            {{ option.label }}
          </option>
        </select>
      </label>

      <label class="filter-field">
        <span>{{ text.sort }}</span>
        <select v-model="filters.sort" class="form-select" @change="fetchProducts">
          <option v-for="option in sortOptions" :key="option.value" :value="option.value">
            {{ option.label }}
          </option>
        </select>
      </label>

      <label class="filter-field">
        <span>{{ text.joinWay }}</span>
        <select v-model="filters.join_way" class="form-select" @change="fetchProducts">
          <option v-for="option in joinWayOptions" :key="option.value || 'all-way'" :value="option.value">
            {{ option.label }}
          </option>
        </select>
      </label>

      <div class="filter-actions">
        <button class="vintage-button query-button" type="submit" :disabled="isLoading">{{ text.query }}</button>
        <button v-if="hasFilters" class="ghost-button" type="button" @click="clearFilters">{{ text.clear }}</button>
      </div>
    </form>

    <p v-if="actionMessage" class="notice-card">{{ actionMessage }}</p>
    <p v-if="errorMessage" class="state-card error message-line">{{ errorMessage }}</p>

    <div v-if="isLoading" class="state-card">{{ text.productLoading }}</div>
    <div v-else-if="!products.length && !errorMessage" class="state-card empty-state message-line">
      {{ text.emptyProducts }}
    </div>

    <div v-else-if="products.length" class="product-layout">
      <div class="product-list-wrap">
        <div class="result-summary">
          <strong>{{ products.length.toLocaleString('ko-KR') }}{{ text.productCountSuffix }}</strong>
          <span>{{ text.resultSummary }}</span>
        </div>

        <div class="product-grid">
          <article v-for="product in pagedProducts" :key="product.id" class="product-card vintage-card"
            :class="{ active: selectedProduct?.id === product.id }" @click="selectProduct(product)">
            <div class="card-topline">
              <span class="vintage-badge">{{ productTypeLabel(product) }}</span>
              <span class="bank-name">{{ product.kor_co_nm }}</span>
            </div>

            <h2>{{ product.fin_prdt_nm }}</h2>

            <div class="rate-grid">
              <div>
                <span>{{ text.base }}</span>
                <strong>{{ formatRate(displayBaseRate(product)) }}</strong>
              </div>
              <div class="highlight-rate">
                <span>{{ text.highest }}</span>
                <strong>{{ formatRate(displayMaxRate(product)) }}</strong>
              </div>
            </div>

            <div class="meta-block">
              <span>{{ text.joinWay }}</span>
              <p>{{ product.join_way || '-' }}</p>
            </div>

            <div class="terms-row" :aria-label="text.term">
              <span v-for="term in productTerms(product)" :key="`${product.id}-${term}`">{{ term }}{{ text.month
                }}</span>
            </div>

            <p class="condition-summary">{{ summarizeText(product.spcl_cnd) }}</p>

            <button class="detail-button" type="button" @click.stop="selectProduct(product)">
              {{ selectedProduct?.id === product.id ? text.detailActive : text.searchSpecialCondition }}
            </button>
          </article>
        </div>

        <nav v-if="productPageCount > 1" class="product-pagination" :aria-label="text.productPage">
          <button type="button" :disabled="productPage <= 1" @click="setProductPage(productPage - 1)">{{ text.previous
            }}</button>
          <button v-for="page in productPageCount" :key="page" type="button" :class="{ active: productPage === page }"
            @click="setProductPage(page)">
            {{ page }}
          </button>
          <button type="button" :disabled="productPage >= productPageCount" @click="setProductPage(productPage + 1)">{{
            text.next }}</button>
        </nav>
      </div>

      <aside class="product-detail glass-panel">
        <template v-if="selectedProduct">
          <div class="detail-heading">
            <span class="vintage-badge">{{ productTypeLabel(selectedProduct) }}</span>
            <h2>{{ selectedProduct.fin_prdt_nm }}</h2>
            <p>{{ selectedProduct.kor_co_nm }}</p>
          </div>

          <div class="detail-stats">
            <div>
              <span>{{ text.baseRate }}</span>
              <strong>{{ formatRate(displayBaseRate(selectedProduct)) }}</strong>
            </div>
            <div class="highlight-rate">
              <span>{{ text.maxRate }}</span>
              <strong>{{ formatRate(displayMaxRate(selectedProduct)) }}</strong>
            </div>
            <div>
              <span>{{ text.maxLimit }}</span>
              <strong>{{ formatLimit(selectedProduct.max_limit) }}</strong>
            </div>
          </div>

          <dl class="detail-list">
            <dt>{{ text.joinWay }}</dt>
            <dd>{{ selectedProduct.join_way || '-' }}</dd>
            <dt>{{ text.term }}</dt>
            <dd>{{productTerms(selectedProduct).map((term) => `${term}${text.month}`).join(', ') || '-'}}</dd>
            <dt>{{ text.specialCondition }}</dt>
            <dd>{{ selectedProduct.spcl_cnd || '-' }}</dd>
            <dt>{{ text.maturityInterest }}</dt>
            <dd>{{ selectedProduct.mtrt_int || '-' }}</dd>
          </dl>

          <div class="option-table">
            <article v-for="option in selectedProduct.options" :key="option.id">
              <span>{{ option.save_trm || '-' }}{{ text.month }}</span>
              <strong>{{ text.base }} {{ formatRate(option.intr_rate) }}</strong>
              <strong class="max-option-rate">{{ text.highest }} {{ formatRate(option.intr_rate2 || option.intr_rate)
                }}</strong>
              <small>{{ option.intr_rate_type_nm || option.rsrv_type_nm || '-' }}</small>
              <button type="button" :disabled="activeOptionIds.has(option.id) || joiningOptionId === option.id"
                @click="subscribe(selectedProduct, option)">
                {{ activeOptionIds.has(option.id) ? text.joining : joiningOptionId === option.id ? text.processing :
                text.joinNow }}
              </button>
            </article>
          </div>
        </template>
      </aside>
    </div>
  </section>
</template>

<style scoped>
.products-page {
  display: grid;
  gap: 18px;
}

.filter-panel {
  display: grid;
  grid-template-columns: auto minmax(180px, 1.2fr) minmax(140px, 0.8fr) minmax(170px, 0.9fr) minmax(140px, 0.8fr) auto;
  gap: 12px;
  align-items: end;
  padding: 16px;
}

.type-toggle {
  display: inline-grid;
  grid-template-columns: repeat(3, minmax(58px, 1fr));
  gap: 6px;
  min-height: 42px;
  padding: 4px;
  border: 2px solid var(--color-ink);
  border-radius: 999px;
  background: rgba(255, 248, 231, 0.78);
}

.type-toggle button,
.detail-button,
.ghost-button,
.product-pagination button,
.option-table button {
  border: 2px solid var(--color-ink);
  border-radius: 999px;
  background: var(--color-paper);
  color: var(--color-ink);
  font-weight: 900;
}

.type-toggle button {
  min-height: 32px;
  padding: 5px 10px;
  font-size: 13px;
}

.type-toggle button.active {
  background: var(--color-money-light);
  box-shadow: 2px 2px 0 var(--color-ink);
}

.filter-field {
  display: grid;
  gap: 5px;
}

.filter-field span {
  color: var(--color-muted);
  font-size: 12px;
  font-weight: 900;
}

.filter-field :deep(.form-control),
.filter-field :deep(.form-select),
.filter-field .form-control,
.filter-field .form-select {
  min-height: 42px;
  margin: 0;
}

.filter-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 8px;
}

.filter-actions button {
  margin: 0;
  white-space: nowrap;
}

.query-button {
  min-width: 74px;
}

.ai-button {
  background: var(--color-money-light);
}

.ghost-button {
  min-height: 42px;
  padding: 8px 14px;
}

.notice-card {
  border: 2px solid var(--color-ink);
  border-radius: 16px;
  background: var(--color-money-light);
  margin: 0;
  padding: 12px 14px;
  font-weight: 900;
}

.message-line {
  white-space: pre-line;
}

.recommendation-panel {
  display: grid;
  gap: 14px;
}

.recommendation-head {
  display: flex;
  align-items: end;
  justify-content: space-between;
  gap: 12px;
}

.recommendation-head h2 {
  margin: 8px 0 0;
  font-size: 24px;
}

.ai-badge {
  background: var(--color-gold);
}

.recommendation-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 14px;
}

.recommendation-card,
.product-card {
  display: grid;
  gap: 12px;
  padding: 18px;
}

.recommendation-card {
  background:
    linear-gradient(135deg, rgba(216, 165, 38, 0.18), transparent 46%),
    var(--color-paper);
}

.recommendation-card h3,
.product-card h2,
.product-detail h2 {
  margin: 0;
  font-size: 21px;
  line-height: 1.28;
}

.card-topline {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.bank-name,
.condition-summary,
.reason-box p,
.comment-box p,
.product-detail p,
.detail-list dd,
.caution {
  margin: 0;
  color: var(--color-muted);
}

.type-chip {
  border-radius: 999px;
  background: rgba(200, 210, 170, 0.44);
  padding: 5px 10px;
  font-size: 12px;
  font-weight: 900;
}

.rate-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 10px;
}

.rate-grid.compact {
  grid-template-columns: repeat(3, minmax(0, 1fr));
}

.rate-grid div,
.detail-stats div,
.reason-box,
.comment-box,
.caution,
.meta-block {
  border: 1px solid rgba(23, 19, 13, 0.16);
  border-radius: 14px;
  background: rgba(255, 248, 231, 0.7);
  padding: 10px;
}

.rate-grid span,
.detail-stats span,
.meta-block span,
.detail-list dt,
.reason-box strong,
.comment-box strong {
  color: var(--color-muted);
  font-size: 12px;
  font-weight: 900;
}

.rate-grid strong,
.detail-stats strong {
  display: block;
  margin-top: 3px;
  color: var(--color-ink);
  font-size: 20px;
}

.highlight-rate strong,
.max-option-rate {
  color: var(--color-dark-gold);
}

.terms-row {
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
}

.terms-row span {
  border-radius: 999px;
  background: rgba(127, 147, 107, 0.22);
  padding: 5px 9px;
  font-size: 12px;
  font-weight: 900;
}

.detail-button {
  justify-self: start;
  min-height: 38px;
  padding: 7px 13px;
}

.product-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.12fr) minmax(340px, 0.88fr);
  gap: 18px;
  align-items: start;
}

.product-list-wrap {
  display: grid;
  gap: 14px;
}

.result-summary {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  color: var(--color-muted);
}

.result-summary strong {
  color: var(--color-ink);
  font-size: 18px;
}

.product-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 14px;
}

.product-card {
  cursor: pointer;
  transition: transform 0.16s ease, box-shadow 0.16s ease;
}

.product-card:hover,
.product-card.active {
  transform: translateY(-2px);
}

.product-card.active {
  box-shadow: 3px 3px 0 var(--color-ink);
}

.product-pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-wrap: wrap;
  gap: 8px;
  padding: 4px 0;
}

.product-pagination button {
  min-width: 36px;
  min-height: 36px;
  padding: 7px 11px;
  font-size: 12px;
}

.product-pagination button.active {
  background: var(--color-gold);
  box-shadow: 3px 3px 0 var(--color-ink);
}

.product-pagination button:disabled,
.option-table button:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.product-detail {
  position: sticky;
  top: 158px;
  display: grid;
  gap: 15px;
  padding: 20px;
}

.detail-heading {
  display: grid;
  gap: 7px;
}

.detail-stats {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}

.detail-list {
  display: grid;
  gap: 7px;
  margin: 0;
}

.detail-list dt {
  margin-top: 4px;
}

.option-table {
  display: grid;
  gap: 8px;
}

.option-table article {
  display: grid;
  grid-template-columns: 70px 95px 95px minmax(80px, 1fr) auto;
  align-items: center;
  gap: 8px;
  border-top: 1px solid rgba(23, 19, 13, 0.16);
  padding-top: 9px;
}

.option-table button {
  min-height: 36px;
  padding: 6px 10px;
  background: var(--color-gold);
}

@media (max-width: 1180px) {
  .filter-panel {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }

  .type-toggle,
  .filter-actions {
    grid-column: span 2;
  }

  .filter-actions {
    justify-content: flex-start;
  }
}

@media (max-width: 1000px) {

  .product-layout,
  .product-grid,
  .recommendation-grid {
    grid-template-columns: 1fr;
  }

  .product-detail {
    position: static;
  }
}

@media (max-width: 720px) {

  .filter-panel,
  .type-toggle,
  .filter-actions,
  .detail-stats,
  .rate-grid.compact {
    grid-template-columns: 1fr;
  }

  .type-toggle,
  .filter-actions {
    grid-column: auto;
  }

  .option-table article {
    grid-template-columns: 1fr;
    align-items: start;
  }

  .card-topline,
  .result-summary,
  .recommendation-head {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
