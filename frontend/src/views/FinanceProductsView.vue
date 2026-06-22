<script setup>
import { computed, onMounted, reactive, ref } from 'vue'

import api from '../api/client'
import { getSubscriptions, joinProduct as requestJoinProduct } from '../api/financial'
import { formatRate } from '../utils/format'


const products = ref([])
const isLoading = ref(false)
const errorMessage = ref('')
const selectedProduct = ref(null)
const subscriptions = ref([])
const actionMessage = ref('')
const joiningOptionId = ref(null)

const filters = reactive({
  type: '',
  bank: '',
  term: '',
  min_rate: '',
})

const productTypeLabel = (type) => (type === 'deposit' ? '정기예금' : '정기적금')
const formatLimit = (value) => {
  if (!value) return '한도 없음'
  return `${Number(value).toLocaleString('ko-KR')}원`
}

const bestOption = (product) => product.best_option || product.options?.[0] || null

const hasFilters = computed(() =>
  Object.values(filters).some((value) => String(value || '').trim() !== ''),
)
const activeOptionIds = computed(() => new Set(
  subscriptions.value.filter((item) => item.status === 'active').map((item) => item.option.id),
))

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
    selectedProduct.value = products.value[0] || null
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

const fetchSubscriptions = async () => {
  subscriptions.value = (await getSubscriptions()).data
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
  } finally { joiningOptionId.value = null }
}

onMounted(() => Promise.all([fetchProducts(), fetchSubscriptions()]))
</script>

<template>
  <section>
    <div class="section-head">
      <div>
        <h1>금융상품</h1>
        <p>DB에 저장된 정기예금과 정기적금 상품을 조회합니다.</p>
      </div>
      <RouterLink class="btn btn-primary" :to="{ name: 'finance-hub', query: { tab: 'recommend' } }">AI 추천</RouterLink>
    </div>

    <form class="surface p-3 mb-4" @submit.prevent="fetchProducts">
      <div class="row g-2">
        <div class="col-12 col-md-2">
          <select v-model="filters.type" class="form-select" aria-label="상품 유형">
            <option value="">전체</option>
            <option value="deposit">정기예금</option>
            <option value="saving">정기적금</option>
          </select>
        </div>
        <div class="col-12 col-md">
          <input v-model.trim="filters.bank" class="form-control" type="search" placeholder="은행명">
        </div>
        <div class="col-6 col-md-2">
          <input v-model.trim="filters.term" class="form-control" type="number" min="1" placeholder="기간(개월)">
        </div>
        <div class="col-6 col-md-2">
          <input v-model.trim="filters.min_rate" class="form-control" type="number" min="0" step="0.1" placeholder="최소 금리">
        </div>
        <div class="col-6 col-md-auto">
          <button class="btn btn-primary w-100" type="submit" :disabled="isLoading">조회</button>
        </div>
        <div v-if="hasFilters" class="col-6 col-md-auto">
          <button class="btn btn-outline-secondary w-100" type="button" @click="clearFilters">초기화</button>
        </div>
      </div>
    </form>

    <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
    <div v-if="actionMessage" class="alert alert-info">{{ actionMessage }}</div>
    <div v-if="isLoading" class="alert alert-secondary">불러오는 중입니다.</div>
    <div v-else-if="!products.length" class="surface grid-empty">조회된 금융상품이 없습니다.</div>

    <div v-else class="row g-4">
      <div class="col-12 col-lg-7">
        <div class="d-grid gap-3">
          <article
            v-for="product in products"
            :key="product.id"
            class="surface p-3 product-row"
            :class="{ active: selectedProduct?.id === product.id }"
            @click="selectedProduct = product"
          >
            <div class="d-flex justify-content-between gap-3">
              <div>
                <span class="badge text-bg-success mb-2">{{ productTypeLabel(product.product_type) }}</span>
                <h2 class="h5 mb-1">{{ product.fin_prdt_nm }}</h2>
                <p class="text-secondary mb-0">{{ product.kor_co_nm }}</p>
              </div>
              <strong class="rate-text">{{ formatRate(product.best_rate) }}</strong>
            </div>
            <div class="d-flex flex-wrap gap-2 mt-3 small">
              <span class="badge text-bg-light border">{{ bestOption(product)?.save_trm || '-' }}개월</span>
              <span class="badge text-bg-light border">기본 {{ formatRate(bestOption(product)?.intr_rate) }}</span>
              <span class="badge text-bg-light border">최고 {{ formatRate(bestOption(product)?.intr_rate2) }}</span>
            </div>
          </article>
        </div>
      </div>

      <aside class="col-12 col-lg-5">
        <div class="surface p-3 sticky-detail">
          <template v-if="selectedProduct">
            <span class="badge text-bg-success mb-2">{{ productTypeLabel(selectedProduct.product_type) }}</span>
            <h2 class="h4">{{ selectedProduct.fin_prdt_nm }}</h2>
            <p class="text-secondary">{{ selectedProduct.kor_co_nm }}</p>

            <div class="row g-2 mb-3">
              <div class="col-6">
                <div class="border rounded-2 p-3">
                  <span class="text-secondary small">최고 금리</span>
                  <strong class="d-block fs-4">{{ formatRate(selectedProduct.best_rate) }}</strong>
                </div>
              </div>
              <div class="col-6">
                <div class="border rounded-2 p-3">
                  <span class="text-secondary small">최대 한도</span>
                  <strong class="d-block fs-6">{{ formatLimit(selectedProduct.max_limit) }}</strong>
                </div>
              </div>
            </div>

            <h3 class="h6">가입 방법</h3>
            <p>{{ selectedProduct.join_way || '-' }}</p>
            <h3 class="h6">우대 조건</h3>
            <p>{{ selectedProduct.spcl_cnd || '-' }}</p>
            <h3 class="h6">만기 후 이자율</h3>
            <p>{{ selectedProduct.mtrt_int || '-' }}</p>

            <div class="table-responsive">
              <table class="table table-sm align-middle mb-0">
                <thead>
                  <tr>
                    <th>기간</th>
                    <th>기본</th>
                    <th>최고</th>
                    <th>방식</th>
                    <th>가입</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="option in selectedProduct.options" :key="option.id">
                    <td>{{ option.save_trm || '-' }}개월</td>
                    <td>{{ formatRate(option.intr_rate) }}</td>
                    <td>{{ formatRate(option.intr_rate2) }}</td>
                    <td>{{ option.intr_rate_type_nm || option.rsrv_type_nm || '-' }}</td>
                    <td>
                      <button
                        class="btn btn-sm"
                        :class="activeOptionIds.has(option.id) ? 'btn-outline-secondary' : 'btn-primary'"
                        type="button"
                        :disabled="activeOptionIds.has(option.id) || joiningOptionId === option.id"
                        @click="subscribe(option)"
                      >
                        {{ activeOptionIds.has(option.id) ? '가입 중' : '가입' }}
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </template>
          <div v-else class="grid-empty">상품을 선택하면 상세 조건을 확인할 수 있습니다.</div>
        </div>
      </aside>
    </div>
  </section>
</template>

<style scoped>
.product-row {
  cursor: pointer;
  transition: border-color 0.15s ease, transform 0.15s ease;
}

.product-row.active,
.product-row:hover {
  border-color: #2f6b5e;
  transform: translateY(-1px);
}

.rate-text {
  color: #2f6b5e;
  font-size: 24px;
}

.sticky-detail {
  position: sticky;
  top: 84px;
}

@media (max-width: 991px) {
  .sticky-detail {
    position: static;
  }
}
</style>
