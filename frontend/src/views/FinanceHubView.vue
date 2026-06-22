<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api/client'
import { getStocks } from '../api/finance'
import { getMyProfile } from '../api/profile'
import FinanceSummary from '../components/finance/FinanceSummary.vue'
import AnalysisView from './AnalysisView.vue'
import CommodityPricesView from './CommodityPricesView.vue'
import FinanceProductsView from './FinanceProductsView.vue'
import FinancialRecommendationView from './FinancialRecommendationView.vue'
import NearbyBanksView from './NearbyBanksView.vue'
import StockHoldingView from './StockHoldingView.vue'
import YoutubeSearchView from './YoutubeSearchView.vue'

const route=useRoute(), router=useRouter()
const tabs=[
  {id:'products',label:'상품비교',component:FinanceProductsView},
  {id:'recommend',label:'금융상품 추천',component:FinancialRecommendationView},
  {id:'insight',label:'AI Insight',component:AnalysisView},
  {id:'commodity',label:'현물 가격',component:CommodityPricesView},
  {id:'stocks',label:'보유주식',component:StockHoldingView},
  {id:'youtube',label:'관심 종목 영상',component:YoutubeSearchView},
  {id:'map',label:'카카오지도',component:NearbyBanksView},
]
const MOCK_PRODUCTS=[
  {id:'mock-1',bank:'카카오뱅크',name:'카카오뱅크 정기예금',term:12,rate:3.4,joined_at:'2026-03-12'},
  {id:'mock-2',bank:'신한은행',name:'신한은행 청년적금',term:24,rate:4.2,joined_at:'2026-04-03'},
  {id:'mock-3',bank:'KB국민은행',name:'국민은행 자유적금',term:12,rate:3.8,joined_at:'2026-05-21'},
]
const activeTab=ref(tabs.some(item=>item.id===route.query.tab)?route.query.tab:'products')
const profile=ref(null), monthly=ref(null), stocks=ref([]), isLoading=ref(true)
const activeComponent=computed(()=>tabs.find(item=>item.id===activeTab.value)?.component||FinanceProductsView)
const realProducts=computed(()=>(profile.value?.joined_products||[]).map(item=>({id:item.id,bank:item.product.kor_co_nm,name:item.product.fin_prdt_nm,term:item.option.save_trm,rate:Number(item.option.intr_rate2||item.option.intr_rate||0),joined_at:item.joined_at,isMock:false})))
const displayedProducts=computed(()=>realProducts.value.length?realProducts.value:MOCK_PRODUCTS)
const assetValue=computed(()=>stocks.value.reduce((sum,item)=>sum+Number(item.valuation_amount||0),0))
const monthlySpend=computed(()=>Number(monthly.value?.total_amount||0))
const chooseTab=(id)=>{activeTab.value=id;router.replace({name:'finance-hub',query:{...route.query,tab:id}})}
watch(()=>route.query.tab,value=>{if(tabs.some(item=>item.id===value))activeTab.value=value})
onMounted(async()=>{const results=await Promise.allSettled([getMyProfile(),api.get('/api/v1/analysis/monthly/'),getStocks()]);if(results[0].status==='fulfilled')profile.value=results[0].value.data;if(results[1].status==='fulfilled')monthly.value=results[1].value.data;if(results[2].status==='fulfilled')stocks.value=results[2].value;isLoading.value=false})
</script>

<template>
  <section class="finance-page">
    <header class="finance-hero glass-panel"><div><span>FLEX FINANCE</span><h1>나의 금융 대시보드</h1><p>상품 비교부터 소비 인사이트, 자산 정보까지 한곳에서 확인하세요.</p></div><div class="hero-orb">₩</div></header>
    <FinanceSummary v-if="!isLoading" :asset-value="assetValue" :monthly-spend="monthlySpend" :product-count="displayedProducts.length" :stock-count="stocks.length" />

    <section class="joined-strip glass-panel"><div class="strip-head"><div><span>MY PRODUCTS</span><h2>가입 금융상품</h2></div><small v-if="!realProducts.length">예시 데이터</small></div><div class="product-scroll"><article v-for="item in displayedProducts" :key="item.id"><span class="bank-icon">{{ item.bank.slice(0,1) }}</span><div><small>{{ item.bank }}</small><strong>{{ item.name }}</strong><p>{{ item.term }}개월 · 가입일 {{ new Date(item.joined_at).toLocaleDateString('ko-KR') }}</p></div><b>{{ item.rate.toFixed(2) }}%</b></article></div></section>

    <nav class="finance-tabs glass-panel" aria-label="금융 기능"><button v-for="tab in tabs" :key="tab.id" :class="{active:activeTab===tab.id}" type="button" @click="chooseTab(tab.id)">{{ tab.label }}</button></nav>
    <div class="tab-panel"><KeepAlive><component :is="activeComponent" /></KeepAlive></div>
  </section>
</template>

<style scoped>
.finance-page{display:grid;gap:18px}.glass-panel{border:1px solid rgba(255,255,255,.84);border-radius:22px;background:rgba(255,255,255,.62);box-shadow:0 15px 45px rgba(77,145,201,.1);backdrop-filter:blur(18px)}.finance-hero{display:flex;align-items:center;justify-content:space-between;min-height:155px;overflow:hidden;padding:24px 28px}.finance-hero span,.strip-head span{color:var(--accent);font-size:10px;font-weight:850;letter-spacing:.15em}.finance-hero h1{margin:5px 0;font-size:27px}.finance-hero p{margin:0;color:var(--muted);font-size:13px}.hero-orb{display:grid;width:90px;height:90px;place-items:center;border:1px solid rgba(255,255,255,.8);border-radius:50%;background:linear-gradient(145deg,rgba(255,255,255,.88),rgba(174,221,255,.56));box-shadow:0 17px 35px rgba(73,150,211,.17),inset 0 1px 1px white;color:#4a91d7;font-size:33px;font-weight:900}.joined-strip{min-width:0;padding:17px}.strip-head{display:flex;align-items:center;justify-content:space-between;margin-bottom:12px}.strip-head h2{margin:2px 0 0;font-size:17px}.strip-head>small{border-radius:99px;background:#edf6ff;color:#4f8cff;padding:4px 8px;font-size:9px}.product-scroll{display:flex;gap:10px;overflow-x:auto;padding:1px 1px 6px}.product-scroll article{display:grid;grid-template-columns:38px minmax(155px,1fr) auto;align-items:center;gap:9px;min-width:285px;border:1px solid rgba(215,234,248,.9);border-radius:15px;background:rgba(255,255,255,.72);padding:12px}.bank-icon{display:grid;width:38px;height:38px;place-items:center;border-radius:12px;background:#e9f5ff;color:#438ad1;font-weight:900}.product-scroll article>div{display:grid;min-width:0}.product-scroll small,.product-scroll p{overflow:hidden;margin:0;color:var(--muted);font-size:9px;text-overflow:ellipsis;white-space:nowrap}.product-scroll strong{overflow:hidden;font-size:12px;text-overflow:ellipsis;white-space:nowrap}.product-scroll b{color:var(--accent);font-size:15px}.finance-tabs{position:sticky;top:76px;z-index:20;display:flex;gap:5px;overflow-x:auto;padding:7px}.finance-tabs button{flex:0 0 auto;margin:0;border:0;border-radius:12px;background:transparent;color:var(--muted);padding:9px 13px;font-size:11px;font-weight:700}.finance-tabs button.active{background:linear-gradient(135deg,#70b9f0,#4f8cff);box-shadow:0 7px 18px rgba(79,140,255,.2);color:#fff}.tab-panel{min-width:0}.tab-panel :deep(>section){width:100%;max-width:none;margin:0}.tab-panel :deep(.section-head h1){font-size:22px}@media(max-width:600px){.finance-hero{min-height:135px;padding:20px}.finance-hero h1{font-size:22px}.finance-hero p{max-width:240px}.hero-orb{width:68px;height:68px}.finance-tabs{top:68px}.product-scroll article{min-width:270px}}
</style>
