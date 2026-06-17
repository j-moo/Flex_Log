<script setup>
import { computed, onMounted, reactive, ref } from 'vue'

import api from '../api/client'


const products = ref([])
const isLoading = ref(false)
const errorMessage = ref('')
const selectedProduct = ref(null)

const filters = reactive({
  type: '',
  bank: '',
  term: '',
  min_rate: '',
})

const productTypeLabel = (type) => (type === 'deposit' ? '정기예금' : '정기적금')
const formatRate = (rate) => (rate === null || rate === undefined ? '-' : `${Number(rate).toFixed(2)}%`)
const formatLimit = (value) => {
  if (!value) return '제한 없음'
  return `${Number(value).toLocaleString('ko-KR')}원`
}

const bestOption = (product) => product.best_option || product.options?.[0] || null

const hasFilters = computed(() =>
  Object.values(filters).some((value) => String(value || '').trim() !== ''),
)

const requestParams = computed(() => {
  const params = {}
  for (const [key, value] of Object.entries(filters)) {
    if (String(value || '').trim() !== '') params[key] = value
  }
  return params
})

const fetchProducts = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const response = await api.get('/api/v1/finance/products/', {
      params: requestParams.value,
    })
    products.value = response.data
    if (selectedProduct.value) {
      selectedProduct.value = products.value.find((item) => item.id === selectedProduct.value.id) || null
    }
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

onMounted(fetchProducts)
</script>

<template>
  <section class="finance-page">
    <div class="finance-header">
      <div>
        <h1>금융상품</h1>
        <p>DB에 로드된 정기예금과 정기적금 상품을 조회합니다.</p>
      </div>
      <RouterLink class="finance-action" :to="{ name: 'finance-recommend' }">AI 추천</RouterLink>
    </div>

    <form class="filter-bar" @submit.prevent="fetchProducts">
      <select v-model="filters.type" aria-label="상품 유형">
        <option value="">전체</option>
        <option value="deposit">정기예금</option>
        <option value="saving">정기적금</option>
      </select>
      <input v-model.trim="filters.bank" type="search" placeholder="은행명" aria-label="은행명 검색">
      <input v-model.trim="filters.term" type="number" min="1" placeholder="기간(개월)" aria-label="저축 기간">
      <input v-model.trim="filters.min_rate" type="number" min="0" step="0.1" placeholder="최소 금리" aria-label="최소 금리">
      <button type="submit" :disabled="isLoading">조회</button>
      <button v-if="hasFilters" class="secondary" type="button" @click="clearFilters">초기화</button>
    </form>

    <div v-if="errorMessage" class="finance-alert">{{ errorMessage }}</div>
    <div v-if="isLoading" class="finance-empty">불러오는 중입니다.</div>
    <div v-else-if="!products.length" class="finance-empty">조회된 금융상품이 없습니다.</div>

    <div v-else class="product-layout">
      <div class="product-list">
        <article
          v-for="product in products"
          :key="product.id"
          class="product-card"
          :class="{ active: selectedProduct?.id === product.id }"
          @click="selectedProduct = product"
        >
          <div class="product-card-top">
            <span>{{ productTypeLabel(product.product_type) }}</span>
            <strong>{{ formatRate(product.best_rate) }}</strong>
          </div>
          <h2>{{ product.fin_prdt_nm }}</h2>
          <p>{{ product.kor_co_nm }}</p>
          <div class="product-meta">
            <span>{{ bestOption(product)?.save_trm || '-' }}개월</span>
            <span>기본 {{ formatRate(bestOption(product)?.intr_rate) }}</span>
            <span>최고 {{ formatRate(bestOption(product)?.intr_rate2) }}</span>
          </div>
        </article>
      </div>

      <aside class="detail-panel">
        <template v-if="selectedProduct">
          <div class="detail-heading">
            <span>{{ productTypeLabel(selectedProduct.product_type) }}</span>
            <h2>{{ selectedProduct.fin_prdt_nm }}</h2>
            <p>{{ selectedProduct.kor_co_nm }}</p>
          </div>

          <div class="rate-grid">
            <div>
              <span>최고 금리</span>
              <strong>{{ formatRate(selectedProduct.best_rate) }}</strong>
            </div>
            <div>
              <span>최대 한도</span>
              <strong>{{ formatLimit(selectedProduct.max_limit) }}</strong>
            </div>
          </div>

          <div class="detail-section">
            <h3>가입 방법</h3>
            <p>{{ selectedProduct.join_way || '-' }}</p>
          </div>
          <div class="detail-section">
            <h3>우대 조건</h3>
            <p>{{ selectedProduct.spcl_cnd || '-' }}</p>
          </div>
          <div class="detail-section">
            <h3>만기 후 이자율</h3>
            <p>{{ selectedProduct.mtrt_int || '-' }}</p>
          </div>

          <div class="option-table">
            <div class="option-row head">
              <span>기간</span>
              <span>기본</span>
              <span>최고</span>
              <span>방식</span>
            </div>
            <div v-for="option in selectedProduct.options" :key="option.id" class="option-row">
              <span>{{ option.save_trm || '-' }}개월</span>
              <span>{{ formatRate(option.intr_rate) }}</span>
              <span>{{ formatRate(option.intr_rate2) }}</span>
              <span>{{ option.intr_rate_type_nm || option.rsrv_type_nm || '-' }}</span>
            </div>
          </div>
        </template>
        <div v-else class="detail-placeholder">
          상품을 선택하면 상세 조건을 확인할 수 있습니다.
        </div>
      </aside>
    </div>
  </section>
</template>

<style scoped>
.finance-page {
  min-height: calc(100vh - 120px);
  margin: -28px calc(50% - 50vw) -48px;
  padding: 32px max(20px, calc(50vw - 560px)) 56px;
  background: #0b0e11;
  color: #eaecef;
}

.finance-header {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20px;
  margin-bottom: 20px;
}

.finance-header h1 {
  margin: 0 0 8px;
  font-size: 28px;
  font-weight: 800;
}

.finance-header p,
.product-card p,
.detail-heading p,
.detail-section p,
.detail-placeholder {
  color: #707a8a;
}

.finance-action,
.filter-bar button {
  min-height: 42px;
  padding: 0 16px;
  border: 0;
  border-radius: 8px;
  background: #fcd535;
  color: #0b0e11;
  font-weight: 800;
}

.filter-bar {
  display: grid;
  grid-template-columns: 140px 1fr 140px 140px auto auto;
  gap: 10px;
  margin-bottom: 16px;
}

.filter-bar input,
.filter-bar select {
  min-height: 42px;
  width: 100%;
  border: 1px solid #2b3139;
  border-radius: 8px;
  background: #1e2329;
  color: #eaecef;
  padding: 0 12px;
}

.filter-bar .secondary {
  background: #2b3139;
  color: #eaecef;
}

.finance-alert,
.finance-empty {
  padding: 16px;
  border: 1px solid #2b3139;
  border-radius: 8px;
  background: #1e2329;
}

.finance-alert {
  border-color: #f6465d;
  color: #f6465d;
}

.product-layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 380px;
  gap: 16px;
}

.product-list {
  display: grid;
  gap: 12px;
}

.product-card,
.detail-panel {
  border: 1px solid #2b3139;
  border-radius: 8px;
  background: #1e2329;
}

.product-card {
  display: grid;
  gap: 8px;
  padding: 16px;
  cursor: pointer;
}

.product-card.active,
.product-card:hover {
  border-color: #fcd535;
}

.product-card-top,
.product-meta,
.rate-grid,
.option-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.product-card-top span,
.detail-heading span {
  color: #fcd535;
  font-weight: 800;
}

.product-card-top strong,
.rate-grid strong {
  color: #fcd535;
  font-size: 22px;
}

.product-card h2,
.detail-heading h2 {
  margin: 0;
  font-size: 18px;
}

.product-card p,
.detail-heading p,
.detail-section p {
  margin: 0;
  line-height: 1.6;
}

.product-meta {
  flex-wrap: wrap;
  justify-content: flex-start;
}

.product-meta span {
  padding: 5px 8px;
  border-radius: 6px;
  background: #2b3139;
  color: #eaecef;
  font-size: 13px;
}

.detail-panel {
  align-self: start;
  display: grid;
  gap: 16px;
  padding: 18px;
  position: sticky;
  top: 86px;
}

.rate-grid {
  align-items: stretch;
}

.rate-grid > div {
  display: grid;
  gap: 6px;
  width: 100%;
  padding: 14px;
  border-radius: 8px;
  background: #2b3139;
}

.rate-grid span,
.detail-section h3,
.option-row.head {
  color: #707a8a;
}

.detail-section {
  display: grid;
  gap: 8px;
}

.detail-section h3 {
  margin: 0;
  font-size: 14px;
  font-weight: 800;
}

.option-table {
  display: grid;
  border-top: 1px solid #2b3139;
}

.option-row {
  display: grid;
  grid-template-columns: 64px 64px 64px 1fr;
  padding: 10px 0;
  border-bottom: 1px solid #2b3139;
  font-size: 14px;
}

@media (max-width: 980px) {
  .filter-bar,
  .product-layout {
    grid-template-columns: 1fr;
  }

  .detail-panel {
    position: static;
  }
}

@media (max-width: 600px) {
  .finance-page {
    margin-top: -18px;
    padding: 24px 14px 40px;
  }

  .finance-header {
    align-items: stretch;
    flex-direction: column;
  }

  .finance-action {
    display: grid;
    place-items: center;
  }
}
</style>
