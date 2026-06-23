<script setup>
import { formatAmount } from '../../utils/format'

defineProps({
  assetValue: {
    type: Number,
    default: 0,
  },
  monthlySpend: {
    type: Number,
    default: 0,
  },
  productCount: {
    type: Number,
    default: 0,
  },
  stockCount: {
    type: Number,
    default: 0,
  },
  monthlyIncome: {
    type: Number,
    default: 0,
  },
})

const emit = defineEmits(['edit-income'])

const items = [
  { key: 'asset', label: '주식 보유량', tone: 'gold' },
  { key: 'spend', label: '이번 달 소비', tone: 'red' },
  { key: 'products', label: '가입상품', tone: 'green' },
  { key: 'income', label: '월 수입', tone: 'blue' },
]
</script>

<template>
  <div class="finance-summary">
    <article v-for="item in items" :key="item.key" :class="`tone-${item.tone}`">
      <div class="card-head">
        <small>{{ item.label }}</small>
        <button
          v-if="item.key === 'income'"
          class="income-plus"
          type="button"
          aria-label="월 수입 입력"
          @click="emit('edit-income')"
        >
          +
        </button>
      </div>
      <strong v-if="item.key === 'asset'">{{ formatAmount(assetValue) }}</strong>
      <strong v-else-if="item.key === 'spend'">{{ formatAmount(monthlySpend) }}</strong>
      <strong v-else-if="item.key === 'products'">{{ productCount }}개</strong>
      <strong v-else>{{ formatAmount(monthlyIncome) }}</strong>
    </article>
  </div>
</template>

<style scoped>
.finance-summary {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 12px;
}

.finance-summary article {
  display: grid;
  gap: 7px;
  border: 2px solid var(--color-ink);
  border-radius: 20px;
  background: var(--color-paper);
  box-shadow: 4px 4px 0 var(--color-ink);
  padding: 16px;
}

.card-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  min-width: 0;
}

small {
  color: var(--color-muted);
  font-size: 12px;
  font-weight: 900;
}

.income-plus {
  display: grid;
  width: 30px;
  height: 30px;
  flex: 0 0 auto;
  place-items: center;
  border: 2px solid var(--color-ink);
  border-radius: 50%;
  background: var(--color-gold);
  color: var(--color-ink);
  padding: 0;
  font-size: 20px;
  font-weight: 900;
  line-height: 1;
}

strong {
  overflow: hidden;
  font-family: 'Fredoka', 'Gowun Dodum', sans-serif;
  font-size: clamp(20px, 2.4vw, 27px);
  line-height: 1.1;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.tone-gold {
  background: linear-gradient(140deg, #fff8e7, rgba(216, 165, 38, 0.22));
}

.tone-red {
  background: linear-gradient(140deg, #fff8e7, rgba(182, 74, 53, 0.14));
}

.tone-green {
  background: linear-gradient(140deg, #fff8e7, rgba(127, 147, 107, 0.22));
}

.tone-blue {
  background: linear-gradient(140deg, #fff8e7, rgba(64, 111, 159, 0.16));
}

@media (max-width: 840px) {
  .finance-summary {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 480px) {
  .finance-summary {
    grid-template-columns: 1fr;
  }
}
</style>
