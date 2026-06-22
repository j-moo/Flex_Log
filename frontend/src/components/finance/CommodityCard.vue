<script setup>
import { computed } from 'vue'
const props = defineProps({ code: String, name: String, prices: { type: Array, default: () => [] } })
const values = computed(() => props.prices.slice(-45).map((item) => Number(item.close_price)))
const points = computed(() => {
  if (!values.value.length) return ''
  const min=Math.min(...values.value), max=Math.max(...values.value), range=max-min||1
  return values.value.map((value,index) => `${(index/(values.value.length-1||1))*300},${92-((value-min)/range)*75}`).join(' ')
})
const latest = computed(() => values.value.at(-1) || 0)
const change = computed(() => values.value.length > 1 ? ((latest.value-values.value[0])/values.value[0])*100 : 0)
</script>
<template>
  <RouterLink class="commodity-mini" :to="{ name:'commodities' }">
    <header><span class="metal">{{ code === 'GOLD' ? 'Au' : 'Ag' }}</span><div><strong>{{ name }}</strong><small>USD / oz</small></div><b>${{ latest.toLocaleString() }}</b></header>
    <svg viewBox="0 0 300 100" preserveAspectRatio="none" aria-label="가격 추이"><defs><linearGradient :id="`fill-${code}`" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4f8cff" stop-opacity=".28"/><stop offset="1" stop-color="#4f8cff" stop-opacity="0"/></linearGradient></defs><polyline :points="points" fill="none" stroke="#4f8cff" stroke-width="3" vector-effect="non-scaling-stroke"/></svg>
    <footer><span>최근 {{ values.length }}개 시세</span><strong :class="change >= 0 ? 'up':'down'">{{ change >= 0 ? '+' : '' }}{{ change.toFixed(2) }}%</strong></footer>
  </RouterLink>
</template>
<style scoped>
.commodity-mini{display:grid;overflow:hidden;border:1px solid var(--border);border-radius:14px;background:white;color:var(--ink);padding:14px}.commodity-mini header{display:grid;grid-template-columns:38px 1fr auto;align-items:center;gap:9px}.metal{display:grid;width:38px;height:38px;place-items:center;border-radius:11px;background:var(--accent-soft);color:var(--accent);font-weight:900}.commodity-mini header div{display:grid}.commodity-mini small{color:var(--muted);font-size:10px}.commodity-mini header>b{font-size:15px}.commodity-mini svg{width:100%;height:92px;margin-top:7px}.commodity-mini footer{display:flex;justify-content:space-between;color:var(--muted);font-size:11px}.commodity-mini footer .up{color:#247a4a}.commodity-mini footer .down{color:#d64747}
</style>
