<script setup>
import { formatAmount } from '../../utils/format'

defineProps({
  amount: {
    type: Number,
    default: 0,
  },
  message: {
    type: String,
    default: '',
  },
})

defineEmits(['close'])
</script>

<template>
  <section class="wallet-alert" role="status">
    <div>
      <strong>지갑 비상벨 발동!</strong>
      <p>오늘의 소비가 평소보다 빠르게 달리고 있습니다.</p>
      <small>{{ message }} · 오늘 {{ formatAmount(amount) }}</small>
    </div>
    <button type="button" aria-label="지갑 비상벨 닫기" @click="$emit('close')">×</button>
  </section>
</template>

<style scoped>
.wallet-alert {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 14px;
  border: 2px solid var(--color-ink);
  border-radius: 18px;
  background: linear-gradient(135deg, rgba(216, 165, 38, 0.28), rgba(182, 74, 53, 0.14)), var(--color-paper);
  box-shadow: 4px 4px 0 var(--color-ink);
  padding: 14px 16px;
}

.wallet-alert strong {
  color: var(--color-red);
  font-size: 16px;
}

.wallet-alert p,
.wallet-alert small {
  margin: 3px 0 0;
}

.wallet-alert p {
  color: var(--color-ink);
  font-weight: 900;
}

.wallet-alert small {
  color: var(--color-muted);
  font-weight: 900;
}

.wallet-alert button {
  display: grid;
  width: 32px;
  height: 32px;
  flex: 0 0 auto;
  place-items: center;
  border: 2px solid var(--color-ink);
  border-radius: 50%;
  background: var(--color-paper);
  color: var(--color-ink);
  font-size: 20px;
  font-weight: 900;
  line-height: 1;
}
</style>
