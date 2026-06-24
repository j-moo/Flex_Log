<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import api from '../api/client'
import { getSubscriptions, joinProduct as requestJoinProduct } from '../api/financial'
import { formatRate } from '../utils/format'

const router = useRouter()
const products = ref([])
const selectedProduct = ref(null)
const subscriptions = ref([])
const isLoading = ref(false)
const isRecommending = ref(false)
const errorMessage = ref('')
const actionMessage = ref('')
const joiningOptionId = ref(null)
const productPage = ref(1)
const PRODUCT_PAGE_SIZE = 6

const filters = reactive({
  type: '',
  bank: '',
  term: '',
  min_rate: '',
})

const productTypeLabel = (type) => (type === 'deposit' ? '정기예금' : '정기적금')
const formatLimit = (value) => (!value ? '한도 없음' : `${Number(value).toLocaleString('ko-KR')}원`)
const bestOption = (product) => product.best_option || product.options?.[0] || null
const hasFilters = computed(() => Object.values(filters).some((value) => String(value || '').trim() !== ''))
const activeOptionIds = computed(() =>
  new Set(subscriptions.value.filter((item) => item.status === 'active').map((item) => item.option.id)),
)
const productPageCount = computed(() => Math.max(1, Math.ceil(products.value.length / PRODUCT_PAGE_SIZE)))
const pagedProducts = computed(() => {
  const start = (productPage.value - 1) * PRODUCT_PAGE_SIZE
  return products.value.slice(start, start + PRODUCT_PAGE_SIZE)
})
const requestParams = computed(() => {
  const params = {}
  Object.entries(filters).forEach(([key, value]) => {
    if (String(value || '').trim()) params[key] = value
  })
  return params
})

const fetchProducts = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const response = await api.get('/api/v1/finance/products/', { params: requestParams.value })
    products.value = response.data
    productPage.value = 1
    selectedProduct.value = pagedProducts.value[0] || null
  } catch {
    errorMessage.value = '금융상품 목록을 불러오지 못했습니다.'
  } finally {
    isLoading.value = false
  }
}

const clearFilters = () => {
  filters.type = ''
  filters.bank = ''
  filters.term = ''
  filters.min_rate = ''
  fetchProducts()
}

const setProductPage = (page) => {
  productPage.value = Math.min(Math.max(1, page), productPageCount.value)
  selectedProduct.value = pagedProducts.value[0] || null
}

const fetchSubscriptions = async () => {
  subscriptions.value = (await getSubscriptions()).data
}

const requestRecommendation = async () => {
  isRecommending.value = true
  errorMessage.value = ''
  try {
    await router.push({ name: 'finance-recommend', query: { auto: '1', t: Date.now() } })
  } catch {
    errorMessage.value = 'AI 예적금 추천을 생성하지 못했습니다.'
  } finally {
    isRecommending.value = false
  }
}

const subscribe = async (option) => {
  joiningOptionId.value = option.id
  actionMessage.value = ''
  try {
    await requestJoinProduct(option.id)
    await fetchSubscriptions()
    actionMessage.value = `${selectedProduct.value.fin_prdt_nm} ${option.save_trm}개월 상품에 가입했습니다.`
  } catch (error) {
    actionMessage.value = error.response?.data?.detail || '상품 가입에 실패했습니다.'
  } finally {
    joiningOptionId.value = null
  }
}

onMounted(() => Promise.all([fetchProducts(), fetchSubscriptions()]))
</script>

<template>
  <section class="products-page page-shell">
    <div class="section-head">
      <div>
        <h1>예적금 비교</h1>
        <p>예금과 적금 상품을 비교하고, AI 추천 결과 페이지에서 바로 가입할 수 있습니다.</p>
      </div>
      <button class="vintage-button" type="button" :disabled="isRecommending" @click="requestRecommendation">
        {{ isRecommending ? 'AI 분석중...' : 'AI 추천' }}
      </button>
    </div>

    <form class="filter-card glass-panel" @submit.prevent="fetchProducts">
      <select v-model="filters.type" class="form-select" aria-label="상품 유형">
        <option value="">전체</option>
        <option value="deposit">정기예금</option>
        <option value="saving">정기적금</option>
      </select>
      <input v-model.trim="filters.bank" class="form-control" type="search" placeholder="은행명">
      <input v-model.trim="filters.term" class="form-control" type="number" min="1" placeholder="기간(개월)">
      <input v-model.trim="filters.min_rate" class="form-control" type="number" min="0" step="0.1" placeholder="최소 금리">
      <button class="vintage-button" type="submit" :disabled="isLoading">조회</button>
      <button v-if="hasFilters" class="ghost-button" type="button" @click="clearFilters">초기화</button>
    </form>

    <p v-if="errorMessage" class="state-card error">{{ errorMessage }}</p>
    <p v-if="actionMessage" class="notice-card">{{ actionMessage }}</p>
    <div v-if="isLoading" class="state-card">상품을 불러오는 중입니다.</div>
    <div v-else-if="!products.length" class="state-card">조회된 금융상품이 없습니다.</div>

    <div v-else class="product-layout">
      <div class="product-list">
        <article
          v-for="product in pagedProducts"
          :key="product.id"
          class="product-row vintage-card"
          :class="{ active: selectedProduct?.id === product.id }"
          @click="selectedProduct = product"
        >
          <div>
            <span class="vintage-badge">{{ productTypeLabel(product.product_type) }}</span>
            <h2>{{ product.fin_prdt_nm }}</h2>
            <p>{{ product.kor_co_nm }}</p>
          </div>
          <strong>{{ formatRate(product.best_rate) }}</strong>
          <div class="product-meta">
            <span>{{ bestOption(product)?.save_trm || '-' }}개월</span>
            <span>기본 {{ formatRate(bestOption(product)?.intr_rate) }}</span>
            <span>최고 {{ formatRate(bestOption(product)?.intr_rate2) }}</span>
          </div>
        </article>

        <nav v-if="productPageCount > 1" class="product-pagination" aria-label="상품 페이지">
          <button type="button" :disabled="productPage <= 1" @click="setProductPage(productPage - 1)">이전</button>
          <button
            v-for="page in productPageCount"
            :key="page"
            type="button"
            :class="{ active: productPage === page }"
            @click="setProductPage(page)"
          >
            {{ page }}
          </button>
          <button type="button" :disabled="productPage >= productPageCount" @click="setProductPage(productPage + 1)">다음</button>
        </nav>
      </div>

      <aside class="product-detail glass-panel">
        <template v-if="selectedProduct">
          <span class="vintage-badge">{{ productTypeLabel(selectedProduct.product_type) }}</span>
          <h2>{{ selectedProduct.fin_prdt_nm }}</h2>
          <p>{{ selectedProduct.kor_co_nm }}</p>

          <div class="detail-stats">
            <div>
              <span>최고 금리</span>
              <strong>{{ formatRate(selectedProduct.best_rate) }}</strong>
            </div>
            <div>
              <span>최대 한도</span>
              <strong>{{ formatLimit(selectedProduct.max_limit) }}</strong>
            </div>
          </div>

          <dl>
            <dt>가입 방법</dt>
            <dd>{{ selectedProduct.join_way || '-' }}</dd>
            <dt>우대 조건</dt>
            <dd>{{ selectedProduct.spcl_cnd || '-' }}</dd>
            <dt>만기 후 이자율</dt>
            <dd>{{ selectedProduct.mtrt_int || '-' }}</dd>
          </dl>

          <div class="option-table">
            <article v-for="option in selectedProduct.options" :key="option.id">
              <span>{{ option.save_trm || '-' }}개월</span>
              <strong>{{ formatRate(option.intr_rate2 || option.intr_rate) }}</strong>
              <small>{{ option.intr_rate_type_nm || option.rsrv_type_nm || '-' }}</small>
              <button
                type="button"
                :disabled="activeOptionIds.has(option.id) || joiningOptionId === option.id"
                @click="subscribe(option)"
              >
                {{ activeOptionIds.has(option.id) ? '가입 중' : '가입' }}
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

.filter-card {
  display: grid;
  grid-template-columns: 150px 1fr 150px 150px auto auto;
  gap: 10px;
  padding: 14px;
}

.ghost-button {
  border: 2px solid var(--color-ink);
  border-radius: 999px;
  background: var(--color-paper);
  color: var(--color-ink);
  padding: 8px 14px;
  font-weight: 900;
}

.notice-card {
  border: 2px solid var(--color-ink);
  border-radius: 16px;
  background: var(--color-money-light);
  margin: 0;
  padding: 12px 14px;
  font-weight: 900;
}

.product-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.08fr) minmax(340px, 0.92fr);
  gap: 18px;
  align-items: start;
}

.product-list {
  display: grid;
  gap: 14px;
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
  border: 2px solid var(--color-ink);
  border-radius: 999px;
  background: var(--color-paper);
  color: var(--color-ink);
  padding: 7px 11px;
  font-size: 12px;
  font-weight: 900;
}

.product-pagination button.active {
  background: var(--color-gold);
  box-shadow: 3px 3px 0 var(--color-ink);
}

.product-pagination button:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.product-row {
  display: grid;
  gap: 12px;
  padding: 18px;
  cursor: pointer;
  transition: transform 0.16s ease;
}

.product-row:hover,
.product-row.active {
  transform: translateY(-2px);
}

.product-row h2,
.product-detail h2 {
  margin: 0;
  font-size: 21px;
}

.product-row p,
.product-detail p,
dd {
  margin: 0;
  color: var(--color-muted);
}

.product-row > strong {
  color: var(--color-dark-gold);
  font-size: 26px;
}

.product-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.product-meta span {
  border-radius: 999px;
  background: rgba(200, 210, 170, 0.42);
  padding: 5px 9px;
  font-size: 12px;
  font-weight: 900;
}

.product-detail {
  position: sticky;
  top: 158px;
  display: grid;
  gap: 14px;
  padding: 20px;
}

.detail-stats {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.detail-stats div {
  border: 2px solid rgba(23, 19, 13, 0.16);
  border-radius: 16px;
  background: rgba(255, 248, 231, 0.64);
  padding: 12px;
}

.detail-stats span,
dt {
  color: var(--color-muted);
  font-size: 12px;
  font-weight: 900;
}

dl {
  display: grid;
  gap: 6px;
  margin: 0;
}

.option-table {
  display: grid;
  gap: 8px;
}

.option-table article {
  display: grid;
  grid-template-columns: 70px 80px 1fr auto;
  align-items: center;
  gap: 8px;
  border-top: 1px solid rgba(23, 19, 13, 0.16);
  padding-top: 9px;
}

.option-table button {
  border: 2px solid var(--color-ink);
  border-radius: 999px;
  background: var(--color-gold);
  padding: 6px 10px;
  font-weight: 900;
}

@media (max-width: 1000px) {
  .filter-card,
  .product-layout {
    grid-template-columns: 1fr;
  }

  .product-detail {
    position: static;
  }
}
</style>
