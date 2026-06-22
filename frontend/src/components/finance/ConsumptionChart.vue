<script setup>
import { computed } from 'vue'
import { formatAmount } from '../../utils/format'
const props = defineProps({ items: { type: Array, default: () => [] }, total: { type: Number, default: 0 } })
const colors = ['#4f8cff','#86aefc','#b7cffd','#d8e5ff','#8b96a8','#c8cdd5']
const normalized = computed(() => props.items.slice(0,6).map((item,index) => ({ ...item, value: Number(item.total ?? item.amount ?? 0), ratio: Number(item.ratio || 0), color: colors[index] })))
const pieStyle = computed(() => {
  if (!normalized.value.length) return { background: '#eef1f5' }
  let cursor = 0
  const stops = normalized.value.map((item) => { const start=cursor; cursor+=item.ratio; return `${item.color} ${start}% ${cursor}%` })
  return { background: `conic-gradient(${stops.join(',')})` }
})
</script>

<template>
  <article class="chart-card finance-card">
    <div class="card-title"><div><span>MONTHLY SPEND</span><h2>월별 소비 분석</h2></div><strong>{{ formatAmount(total) }}</strong></div>
    <div v-if="normalized.length" class="chart-body">
      <div class="pie" :style="pieStyle"><div><strong>{{ normalized.length }}</strong><small>categories</small></div></div>
      <div class="bars">
        <div v-for="item in normalized" :key="item.name" class="bar-item"><div><span><i :style="{ background:item.color }"></i>{{ item.name }}</span><b>{{ item.ratio.toFixed(1) }}%</b></div><div class="track"><i :style="{ width:`${Math.min(item.ratio,100)}%`, background:item.color }"></i></div></div>
      </div>
    </div>
    <div v-else class="finance-empty">소비 기록을 작성하면 카테고리 분석이 표시됩니다.</div>
  </article>
</template>

<style scoped>
.finance-card{border:1px solid var(--border);border-radius:14px;background:#fff;padding:17px}.card-title{display:flex;align-items:flex-start;justify-content:space-between;gap:12px;margin-bottom:15px}.card-title span{color:var(--accent);font-size:9px;font-weight:850;letter-spacing:.13em}.card-title h2{margin:3px 0 0;font-size:17px}.card-title>strong{font-size:15px}.finance-empty{display:grid;min-height:150px;place-content:center;color:var(--muted);font-size:12px;text-align:center}
.chart-body{display:grid;grid-template-columns:170px 1fr;align-items:center;gap:25px;padding:8px 0}.pie{display:grid;width:150px;height:150px;place-items:center;border-radius:50%}.pie>div{display:grid;width:88px;height:88px;place-content:center;border-radius:50%;background:white;text-align:center}.pie strong{font-size:22px}.pie small{color:var(--muted);font-size:10px}.bars{display:grid;gap:12px}.bar-item>div:first-child{display:flex;justify-content:space-between;gap:10px;font-size:12px}.bar-item span{display:flex;align-items:center;gap:7px}.bar-item span i{width:8px;height:8px;border-radius:50%}.track{height:7px;overflow:hidden;border-radius:10px;background:#eff1f4}.track i{display:block;height:100%;border-radius:10px}@media(max-width:570px){.chart-body{grid-template-columns:1fr}.pie{margin:auto}}
</style>
