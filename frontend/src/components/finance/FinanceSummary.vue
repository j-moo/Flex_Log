<script setup>
import { formatAmount } from '../../utils/format'
defineProps({ assetValue: { type: Number, default: 0 }, monthlySpend: { type: Number, default: 0 }, productCount: { type: Number, default: 0 }, stockCount: { type: Number, default: 0 } })
const items = [
  { key: 'asset', label: '총 자산', icon: '₩' },
  { key: 'spend', label: '이번 달 소비', icon: '↘' },
  { key: 'products', label: '가입 상품', icon: '✓' },
  { key: 'stocks', label: '보유 주식', icon: '↗' },
]
</script>

<template>
  <div class="summary-grid">
    <article v-for="item in items" :key="item.key">
      <span class="summary-icon">{{ item.icon }}</span><small>{{ item.label }}</small>
      <strong v-if="item.key === 'asset'">{{ formatAmount(assetValue) }}</strong>
      <strong v-else-if="item.key === 'spend'">{{ formatAmount(monthlySpend) }}</strong>
      <strong v-else-if="item.key === 'products'">{{ productCount }}개</strong>
      <strong v-else>{{ stockCount }}종목</strong>
    </article>
  </div>
</template>

<style scoped>
.summary-grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:10px}.summary-grid article{display:grid;grid-template-columns:32px 1fr;align-items:center;gap:2px 9px;border:1px solid rgba(255,255,255,.86);border-radius:17px;background:rgba(255,255,255,.64);box-shadow:0 12px 32px rgba(76,145,201,.08);padding:14px;backdrop-filter:blur(16px)}.summary-icon{display:grid;grid-row:1/3;width:32px;height:32px;place-items:center;border-radius:10px;background:#e6f4ff;color:#438bd5;font-weight:900}.summary-grid small{color:var(--muted);font-size:11px}.summary-grid strong{overflow:hidden;font-size:15px;text-overflow:ellipsis;white-space:nowrap}@media(max-width:700px){.summary-grid{grid-template-columns:repeat(2,1fr)}}
</style>
