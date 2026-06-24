<script setup>
import { computed, onMounted, reactive, ref } from 'vue'

import api from '../api/client'
import ConfirmDialog from '../components/common/ConfirmDialog.vue'
import { formatAmount, formatNumber } from '../utils/format'


const holdings = ref([])
const selectedId = ref(null)
const isLoading = ref(false)
const errorMessage = ref('')
const removeTarget = ref(null)
const isRemoving = ref(false)
const form = reactive({
  symbol: '',
  name: '',
  quantity: '',
  average_price: '',
  current_price: '',
  memo: '',
})

const selectedHolding = computed(() =>
  holdings.value.find((item) => item.id === selectedId.value) || holdings.value[0] || null,
)

const totals = computed(() => {
  return holdings.value.reduce((acc, item) => {
    acc.invested += Number(item.invested_amount || 0)
    acc.valuation += Number(item.valuation_amount || 0)
    acc.profit += Number(item.profit_loss || 0)
    return acc
  }, { invested: 0, valuation: 0, profit: 0 })
})

const totalProfitRate = computed(() => {
  if (!totals.value.invested) return 0
  return (totals.value.profit / totals.value.invested) * 100
})

const resetForm = () => {
  selectedId.value = null
  Object.assign(form, {
    symbol: '',
    name: '',
    quantity: '',
    average_price: '',
    current_price: '',
    memo: '',
  })
}

const editHolding = (holding) => {
  selectedId.value = holding.id
  Object.assign(form, {
    symbol: holding.symbol,
    name: holding.name,
    quantity: holding.quantity,
    average_price: holding.average_price,
    current_price: holding.current_price,
    memo: holding.memo || '',
  })
}

const loadHoldings = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const response = await api.get('/api/v1/finance/stocks/')
    holdings.value = response.data
  } catch {
    errorMessage.value = '보유 주식 정보를 불러오지 못했습니다.'
  } finally {
    isLoading.value = false
  }
}

const submit = async () => {
  errorMessage.value = ''
  const payload = { ...form, symbol: form.symbol.toUpperCase() }
  try {
    if (selectedId.value) {
      await api.patch(`/api/v1/finance/stocks/${selectedId.value}/`, payload)
    } else {
      await api.post('/api/v1/finance/stocks/', payload)
    }
    resetForm()
    await loadHoldings()
  } catch (error) {
    errorMessage.value = Object.values(error.response?.data || {}).flat().join(' ') || '보유 주식 저장에 실패했습니다.'
  }
}

const removeHolding = (holding) => {
  removeTarget.value = holding
}

const closeRemoveConfirm = () => {
  if (isRemoving.value) return
  removeTarget.value = null
}

const confirmRemoveHolding = async () => {
  if (!removeTarget.value) return
  isRemoving.value = true
  errorMessage.value = ''
  try {
    await api.delete(`/api/v1/finance/stocks/${removeTarget.value.id}/`)
    if (selectedId.value === removeTarget.value.id) resetForm()
    removeTarget.value = null
    await loadHoldings()
  } catch {
    errorMessage.value = '보유 주식 삭제에 실패했습니다.'
  } finally {
    isRemoving.value = false
  }
}

onMounted(loadHoldings)
</script>

<template>
  <section>
    <div class="section-head">
      <div>
        <h1>보유 주식 현황</h1>
        <p>직접 입력한 보유 종목을 기준으로 평가금액과 손익률을 확인합니다.</p>
      </div>
      <RouterLink class="btn btn-outline-secondary" :to="{ name: 'analysis' }">AI 분석</RouterLink>
    </div>

    <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>

    <div class="row g-4">
      <div class="col-12 col-lg-4">
        <form class="surface p-3" @submit.prevent="submit">
          <h2 class="h5 mb-3">{{ selectedId ? '보유 종목 수정' : '보유 종목 추가' }}</h2>
          <div class="d-grid gap-3">
            <div>
              <label for="symbol" class="form-label">종목 코드</label>
              <input id="symbol" v-model.trim="form.symbol" class="form-control text-uppercase" maxlength="20" required>
            </div>
            <div>
              <label for="name" class="form-label">종목명</label>
              <input id="name" v-model.trim="form.name" class="form-control" maxlength="100" required>
            </div>
            <div>
              <label for="quantity" class="form-label">보유 수량</label>
              <input id="quantity" v-model="form.quantity" class="form-control" type="number" min="1" step="1" required>
            </div>
            <div>
              <label for="average-price" class="form-label">평균 매입가</label>
              <input id="average-price" v-model="form.average_price" class="form-control" type="number" min="0" step="0.01" required>
            </div>
            <div>
              <label for="current-price" class="form-label">현재가</label>
              <input id="current-price" v-model="form.current_price" class="form-control" type="number" min="0" step="0.01" required>
            </div>
            <div>
              <label for="memo" class="form-label">메모</label>
              <textarea id="memo" v-model="form.memo" class="form-control" rows="3"></textarea>
            </div>
          </div>
          <div class="d-flex gap-2 mt-3">
            <button class="btn btn-primary">{{ selectedId ? '수정' : '추가' }}</button>
            <button v-if="selectedId" class="btn btn-outline-secondary" type="button" @click="resetForm">취소</button>
          </div>
        </form>
      </div>

      <div class="col-12 col-lg-8">
        <div class="row g-3 mb-3">
          <div class="col-12 col-md-4">
            <div class="surface p-3 h-100">
              <p class="text-secondary mb-1">투입 금액</p>
              <div class="summary-value">{{ formatAmount(totals.invested) }}</div>
            </div>
          </div>
          <div class="col-12 col-md-4">
            <div class="surface p-3 h-100">
              <p class="text-secondary mb-1">평가 금액</p>
              <div class="summary-value">{{ formatAmount(totals.valuation) }}</div>
            </div>
          </div>
          <div class="col-12 col-md-4">
            <div class="surface p-3 h-100">
              <p class="text-secondary mb-1">평가 손익</p>
              <div class="summary-value" :class="totals.profit >= 0 ? 'text-success' : 'text-danger'">
                {{ formatAmount(totals.profit) }}
              </div>
              <div class="small text-secondary">{{ totalProfitRate.toFixed(2) }}%</div>
            </div>
          </div>
        </div>

        <div v-if="isLoading" class="alert alert-secondary">불러오는 중입니다.</div>
        <div v-else-if="!holdings.length" class="surface grid-empty">보유 주식 정보가 없습니다.</div>
        <div v-else class="row g-3">
          <div class="col-12 col-xl-5">
            <div class="surface">
              <div class="p-3 border-bottom"><h2 class="h5 mb-0">종목 목록</h2></div>
              <div class="list-group list-group-flush">
                <button
                  v-for="holding in holdings"
                  :key="holding.id"
                  class="list-group-item list-group-item-action"
                  type="button"
                  @click="selectedId = holding.id"
                >
                  <div class="d-flex justify-content-between gap-2">
                    <div>
                      <strong>{{ holding.symbol }}</strong>
                      <div class="small text-secondary">{{ holding.name }}</div>
                    </div>
                    <strong :class="Number(holding.profit_loss) >= 0 ? 'text-success' : 'text-danger'">
                      {{ Number(holding.profit_rate).toFixed(2) }}%
                    </strong>
                  </div>
                </button>
              </div>
            </div>
          </div>

          <div class="col-12 col-xl-7">
            <div class="surface p-3 h-100" v-if="selectedHolding">
              <div class="d-flex justify-content-between gap-3 mb-3">
                <div>
                  <h2 class="h4 mb-1">{{ selectedHolding.symbol }}</h2>
                  <p class="text-secondary mb-0">{{ selectedHolding.name }}</p>
                </div>
                <div class="text-end">
                  <strong :class="Number(selectedHolding.profit_loss) >= 0 ? 'text-success' : 'text-danger'">
                    {{ Number(selectedHolding.profit_rate).toFixed(2) }}%
                  </strong>
                  <div class="small text-secondary">{{ formatAmount(selectedHolding.profit_loss) }}</div>
                </div>
              </div>

              <div class="stock-bars mb-3">
                <div>
                  <span>투입</span>
                  <div><i :style="{ width: '70%' }"></i></div>
                  <strong>{{ formatAmount(selectedHolding.invested_amount) }}</strong>
                </div>
                <div>
                  <span>평가</span>
                  <div><i :style="{ width: `${Math.min(Math.max(Number(selectedHolding.valuation_amount) / Math.max(Number(selectedHolding.invested_amount), 1) * 70, 6), 100)}%` }"></i></div>
                  <strong>{{ formatAmount(selectedHolding.valuation_amount) }}</strong>
                </div>
              </div>

              <dl class="row mb-3">
                <dt class="col-5">보유 수량</dt>
                <dd class="col-7">{{ formatNumber(selectedHolding.quantity, 0) }}</dd>
                <dt class="col-5">평균 단가</dt>
                <dd class="col-7">{{ formatAmount(selectedHolding.average_price) }}</dd>
                <dt class="col-5">현재가</dt>
                <dd class="col-7">{{ formatAmount(selectedHolding.current_price) }}</dd>
              </dl>

              <p v-if="selectedHolding.memo" class="content-preline text-secondary">{{ selectedHolding.memo }}</p>
              <div class="d-flex gap-2">
                <button class="btn btn-outline-primary btn-sm" type="button" @click="editHolding(selectedHolding)">수정</button>
                <button class="btn btn-outline-danger btn-sm" type="button" @click="removeHolding(selectedHolding)">삭제</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <ConfirmDialog
      :open="Boolean(removeTarget)"
      title="보유 주식 삭제"
      :message="`${removeTarget?.symbol || '선택한 종목'} 보유 정보를 삭제할까요?`"
      detail="전체 보유 수량이 삭제됩니다."
      confirm-text="삭제"
      :loading="isRemoving"
      @close="closeRemoveConfirm"
      @confirm="confirmRemoveHolding"
    />
  </section>
</template>

<style scoped>
.stock-bars {
  display: grid;
  gap: 12px;
}

.stock-bars > div {
  display: grid;
  grid-template-columns: 52px 1fr auto;
  align-items: center;
  gap: 10px;
}

.stock-bars div div {
  height: 12px;
  overflow: hidden;
  border-radius: 999px;
  background: #e8eef3;
}

.stock-bars i {
  display: block;
  height: 100%;
  border-radius: inherit;
  background: #2f6b5e;
}
</style>
