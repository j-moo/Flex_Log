<script setup>
import { nextTick, onMounted, ref } from 'vue'
import { searchNearbyBanks } from '../api/financial'

const query = ref('역삼역')
const radius = ref(2000)
const result = ref(null)
const selectedBank = ref(null)
const mapContainer = ref(null)
const isLoading = ref(false)
const errorMessage = ref('')
const mapMessage = ref('')
let map = null
let markers = []
let sdkPromise = null

const loadKakaoSdk = () => {
  if (window.kakao?.maps) return new Promise((resolve) => window.kakao.maps.load(resolve))
  if (sdkPromise) return sdkPromise
  sdkPromise = new Promise((resolve, reject) => {
  const key = import.meta.env.VITE_KAKAO_JS_KEY
  if (!key) { reject(new Error('VITE_KAKAO_JS_KEY가 없어 목록만 표시합니다.')); return }
  const existing = document.querySelector('script[data-kakao-map]')
  if (existing) existing.remove()
  const script = document.createElement('script')
  script.dataset.kakaoMap = 'true'
  script.src = `https://dapi.kakao.com/v2/maps/sdk.js?appkey=${key}&autoload=false`
  const timer = window.setTimeout(() => reject(new Error('Kakao 지도 로딩 시간이 초과되었습니다. Web 도메인 등록을 확인하세요.')), 8000)
  script.onload = () => {
    window.clearTimeout(timer)
    if (!window.kakao?.maps) { reject(new Error('Kakao JavaScript 키 또는 Web 도메인 설정을 확인하세요.')); return }
    window.kakao.maps.load(resolve)
  }
  script.onerror = () => { window.clearTimeout(timer); reject(new Error('Kakao 지도 SDK를 불러오지 못했습니다. API 키와 Web 도메인을 확인하세요.')) }
  document.head.appendChild(script)
  })
  return sdkPromise
}

const renderMap = async () => {
  if (!result.value || !mapContainer.value) return
  try {
    await loadKakaoSdk()
    mapMessage.value = ''
    const center = new window.kakao.maps.LatLng(result.value.center.y, result.value.center.x)
    map = new window.kakao.maps.Map(mapContainer.value, { center, level: 4 })
    markers.forEach((marker) => marker.setMap(null))
    markers = result.value.banks.map((bank) => {
      const marker = new window.kakao.maps.Marker({
        map,
        position: new window.kakao.maps.LatLng(bank.y, bank.x),
        title: bank.name,
      })
      window.kakao.maps.event.addListener(marker, 'click', () => { selectedBank.value = bank })
      return marker
    })
  } catch (error) { mapMessage.value = error.message }
}

const search = async () => {
  if (!query.value.trim()) return
  isLoading.value = true
  errorMessage.value = ''
  try {
    result.value = (await searchNearbyBanks(query.value.trim(), radius.value)).data
    selectedBank.value = result.value.banks[0] || null
    await nextTick(); await renderMap()
  } catch (error) { errorMessage.value = error.response?.data?.detail || '주변 은행을 검색하지 못했습니다.' }
  finally { isLoading.value = false }
}
const selectBank = (bank) => {
  selectedBank.value = bank
  if (map && window.kakao?.maps) map.panTo(new window.kakao.maps.LatLng(bank.y, bank.x))
}
onMounted(search)
</script>

<template>
  <section class="bank-page">
    <div class="section-head"><div><h1>주변 은행</h1><p>주소나 장소를 입력해 가까운 지점을 찾습니다.</p></div><RouterLink class="btn btn-outline-dark" :to="{ name: 'finance-hub' }">금융 홈</RouterLink></div>
    <form class="surface bank-search" @submit.prevent="search"><input v-model="query" type="search" placeholder="예: 역삼역, 서울 강남구 테헤란로 212" required><select v-model.number="radius"><option :value="1000">1km</option><option :value="2000">2km</option><option :value="5000">5km</option></select><button type="submit">검색</button></form>
    <div v-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
    <div class="bank-layout">
      <div class="surface map-card"><div ref="mapContainer" class="map"><div v-if="isLoading" class="grid-empty">위치를 찾는 중입니다.</div></div><p v-if="mapMessage" class="map-message">{{ mapMessage }}</p></div>
      <aside class="bank-list">
        <div v-if="!result?.banks?.length" class="surface grid-empty">주변 은행이 없습니다.</div>
        <button v-for="bank in result?.banks" :key="bank.id" class="surface bank-item" :class="{ active: selectedBank?.id === bank.id }" type="button" @click="selectBank(bank)">
          <span class="bank-avatar">B</span><span><strong>{{ bank.name }}</strong><small>{{ bank.road_address || bank.address }}</small><em>{{ bank.distance.toLocaleString() }}m</em></span>
        </button>
      </aside>
    </div>
    <article v-if="selectedBank" class="surface selected-card"><div><span class="bank-avatar">B</span><div><strong>{{ selectedBank.name }}</strong><p>{{ selectedBank.road_address || selectedBank.address }}</p><small>{{ selectedBank.phone || '전화번호 정보 없음' }}</small></div></div><a :href="selectedBank.place_url" target="_blank" rel="noopener">카카오맵에서 보기</a></article>
  </section>
</template>

<style scoped>
.bank-page{width:min(100%,1040px);margin:auto}.bank-search{display:grid;grid-template-columns:1fr 110px auto;gap:10px;padding:10px;margin-bottom:18px}.bank-search input,.bank-search select{width:100%;max-width:none;margin:0;border:0;padding:10px}.bank-search button{margin:0;border:0;border-radius:8px;background:#0095f6;color:white;padding:0 20px;font-weight:800}.bank-layout{display:grid;grid-template-columns:minmax(0,1.4fr) minmax(300px,.6fr);gap:16px}.map-card{overflow:hidden}.map{height:480px;background:linear-gradient(135deg,#edf3e7,#e8eef5)}.map-message{margin:0;padding:10px;background:#fff8dd;color:#725b00;font-size:13px}.bank-list{display:grid;align-content:start;gap:10px;max-height:480px;overflow:auto}.bank-item{display:grid;grid-template-columns:42px 1fr;gap:10px;width:100%;margin:0;padding:12px;text-align:left;color:#262626}.bank-item>span:last-child{display:grid;gap:3px}.bank-item small{overflow:hidden;color:#737373;text-overflow:ellipsis;white-space:nowrap}.bank-item em{color:#0095f6;font-size:12px;font-style:normal;font-weight:800}.bank-item.active{border-color:#0095f6}.bank-avatar{display:grid;width:42px;height:42px;place-items:center;border-radius:50%;background:linear-gradient(135deg,#833ab4,#fd1d1d,#fcb045);color:white;font-weight:900}.selected-card{display:flex;align-items:center;justify-content:space-between;gap:16px;margin-top:16px;padding:16px}.selected-card>div{display:flex;align-items:center;gap:12px}.selected-card p{margin:3px 0;color:#737373}.selected-card a{color:#0095f6;font-weight:800}@media(max-width:800px){.bank-layout{grid-template-columns:1fr}.bank-list{max-height:360px}.bank-search{grid-template-columns:1fr 90px}.bank-search button{grid-column:1/-1;padding:10px}.selected-card{align-items:flex-start;flex-direction:column}}
</style>
