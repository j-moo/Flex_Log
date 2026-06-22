<script setup>
import { formatRate } from '../../utils/format'
defineProps({ item: { type: Object, required: true } })
</script>
<template>
  <article class="recommend-card">
    <header><span>{{ item.product_type === 'saving' ? '적금' : '예금' }}</span><strong>{{ formatRate(item.max_interest_rate || item.interest_rate) }}</strong></header>
    <p class="bank">{{ item.bank_name || '추천 상품' }}</p><h3>{{ item.product_name || item.title }}</h3>
    <p class="reason">{{ item.reason || item.description }}</p>
    <footer><span>{{ item.save_trm || '-' }}개월</span><RouterLink :to="{ name:'finance-recommend' }">자세히</RouterLink></footer>
  </article>
</template>
<style scoped>
.recommend-card{display:grid;min-width:245px;gap:6px;border:1px solid var(--border);border-radius:14px;background:#fff;padding:15px}.recommend-card header{display:flex;align-items:center;justify-content:space-between}.recommend-card header span{border-radius:999px;background:var(--accent-soft);color:var(--accent);padding:4px 8px;font-size:10px;font-weight:800}.recommend-card header strong{color:var(--accent);font-size:20px}.bank{margin:7px 0 0;color:var(--muted);font-size:11px}.recommend-card h3{margin:0;font-size:15px}.reason{display:-webkit-box;min-height:39px;overflow:hidden;margin:4px 0;color:#5f6670;font-size:12px;line-height:1.5;-webkit-box-orient:vertical;-webkit-line-clamp:2}.recommend-card footer{display:flex;justify-content:space-between;border-top:1px solid var(--border);padding-top:10px;color:var(--muted);font-size:11px}.recommend-card footer a{color:var(--accent);font-weight:800}
</style>
