<script setup>
import { createChart, LineSeries } from 'lightweight-charts'
import { nextTick, onBeforeUnmount, onMounted, reactive, ref, watch } from 'vue'

import { getCommodityPrices } from '../api/financial'

const selectedCode = ref('GOLD')
const filters = reactive({ start: '', end: '' })
const commodity = ref(null)
const prices = ref([])
const chartContainer = ref(null)
const isLoading = ref(false)
const errorMessage = ref('')
let chart = null
let line = null
let resizeObserver = null

const setupChart = () => {
  if (chart || !chartContainer.value) return
  chart = createChart(chartContainer.value, {
    height: 360,
    layout: { background: { color: '#fff' }, textColor: '#737373', attributionLogo: false },
    grid: { vertLines: { color: '#f2f2f2' }, horzLines: { color: '#f2f2f2' } },
    timeScale: { borderColor: '#dbdbdb' },
    rightPriceScale: { borderColor: '#dbdbdb' },
  })
  line = chart.addSeries(LineSeries, { color: selectedCode.value === 'GOLD' ? '#d49b22' : '#7b8794', lineWidth: 3 })
  resizeObserver = new ResizeObserver(([entry]) => chart.applyOptions({ width: entry.contentRect.width }))
  resizeObserver.observe(chartContainer.value)
}

const drawChart = () => {
  if (!line) return
  line.applyOptions({ color: selectedCode.value === 'GOLD' ? '#d49b22' : '#7b8794' })
  line.setData(prices.value.map((item) => ({ time: item.price_date, value: Number(item.close_price) })))
  chart.timeScale().fitContent()
}

const loadPrices = async () => {
  errorMessage.value = ''
  if (filters.start && filters.end && filters.start > filters.end) {
    errorMessage.value = '시작일은 종료일보다 늦을 수 없습니다.'
    return
  }
  isLoading.value = true
  try {
    const response = await getCommodityPrices(selectedCode.value, {
      ...(filters.start && { start: filters.start }),
      ...(filters.end && { end: filters.end }),
    })
    commodity.value = response.data.commodity
    prices.value = response.data.prices
    await nextTick()
    setupChart()
    drawChart()
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '시세를 불러오지 못했습니다.'
  } finally { isLoading.value = false }
}

watch(selectedCode, loadPrices)
onMounted(loadPrices)
onBeforeUnmount(() => { resizeObserver?.disconnect(); chart?.remove() })
</script>

<template>
  <section class="commodity-page">
    <div class="section-head"><div><h1>금·은 시세</h1><p>USD / troy oz 기준 일별 종가입니다.</p></div><RouterLink class="btn btn-outline-dark" :to="{ name: 'finance-hub' }">금융 홈</RouterLink></div>
    <div class="asset-stories">
      <button :class="{ active: selectedCode === 'GOLD' }" type="button" @click="selectedCode = 'GOLD'"><span>Au</span>금</button>
      <button :class="{ active: selectedCode === 'SILVER' }" type="button" @click="selectedCode = 'SILVER'"><span>Ag</span>은</button>
    </div>
    <form class="surface filter-card" @submit.prevent="loadPrices">
      <label>시작일<input v-model="filters.start" class="form-control" type="date"></label>
      <label>종료일<input v-model="filters.end" class="form-control" type="date"></label>
      <button class="btn btn-dark" type="submit">기간 적용</button>
    </form>
    <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
    <article class="surface chart-post">
      <header><div class="post-avatar">{{ selectedCode === 'GOLD' ? 'Au' : 'Ag' }}</div><div><strong>flex.commodity</strong><small>{{ commodity?.name || selectedCode }} · {{ prices.length }}개 데이터</small></div></header>
      <div v-if="isLoading" class="grid-empty">시세를 불러오는 중입니다.</div>
      <div v-else-if="!prices.length" class="grid-empty">선택한 기간의 데이터가 없습니다.</div>
      <div v-show="prices.length" ref="chartContainer" class="chart"></div>
      <footer v-if="prices.length"><strong>최근 종가 ${{ Number(prices.at(-1)?.close_price).toLocaleString() }}</strong><span>{{ prices[0]?.price_date }} — {{ prices.at(-1)?.price_date }}</span></footer>
    </article>
  </section>
</template>

<style scoped>
.commodity-page { width: min(100%, 860px); margin: auto; }.asset-stories{display:flex;gap:18px;margin-bottom:18px}.asset-stories button{display:grid;justify-items:center;gap:6px;border:0;background:none;color:#737373}.asset-stories button span{display:grid;width:70px;height:70px;place-items:center;border:3px solid #dbdbdb;border-radius:50%;background:white;color:#262626;font-size:22px;font-weight:900}.asset-stories button.active span{border-color:#f04b54}.asset-stories button.active{color:#262626;font-weight:800}.filter-card{display:grid;grid-template-columns:1fr 1fr auto;align-items:end;gap:12px;padding:16px;margin-bottom:18px}.filter-card label{color:#737373;font-size:13px;font-weight:700}.chart-post{overflow:hidden}.chart-post header{display:flex;align-items:center;gap:10px;padding:14px;border-bottom:1px solid #efefef}.chart-post header div:nth-child(2){display:grid}.chart-post small{color:#737373}.post-avatar{display:grid;width:38px;height:38px;place-items:center;border-radius:50%;background:#262626;color:white;font-weight:900}.chart{width:100%;height:360px}.chart-post footer{display:flex;justify-content:space-between;gap:12px;padding:16px;border-top:1px solid #efefef}.chart-post footer span{color:#737373}@media(max-width:640px){.filter-card{grid-template-columns:1fr}.chart-post footer{flex-direction:column}}
</style>
