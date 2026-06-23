<script setup>
import { computed, nextTick, onMounted, ref } from 'vue'

import { getBankRoute, searchNearbyBanks } from '../api/financial'

const query = ref('서울 강남구 테헤란로 212')
const radius = ref(2000)
const result = ref(null)
const selectedBank = ref(null)
const routeInfo = ref(null)
const mapContainer = ref(null)
const isLoading = ref(false)
const isRouteLoading = ref(false)
const errorMessage = ref('')
const mapMessage = ref('')
const routeMessage = ref('')
let map = null
let markers = []
let routePolyline = null
let originMarker = null
let infoWindow = null
let sdkPromise = null


const formatDistance = (meters) => {
  const value = Number(meters || 0)
  return value >= 1000 ? `${(value / 1000).toFixed(1)}km` : `${value.toLocaleString()}m`
}

const formatDuration = (seconds) => `${Math.max(1, Math.round(Number(seconds || 0) / 60)).toLocaleString()}\ubd84`

const routeSummary = computed(() => {
  if (!routeInfo.value) return ''
  const { distance, duration } = routeInfo.value.summary || {}
  return `${formatDistance(distance)} \u00b7 ${formatDuration(duration)}`
})

const escapeHtml = (value) => String(value ?? '').replace(/[&<>"']/g, (char) => ({
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#39;',
}[char]))


const loadKakaoSdk = () => {
  if (window.kakao?.maps) return new Promise((resolve) => window.kakao.maps.load(resolve))
  if (sdkPromise) return sdkPromise
  sdkPromise = new Promise((resolve, reject) => {
    const key = import.meta.env.VITE_KAKAO_JAVASCRIPT_KEY || import.meta.env.VITE_KAKAO_JS_KEY
    if (!key) {
      reject(new Error('VITE_KAKAO_JAVASCRIPT_KEY가 없어 목록만 표시합니다.'))
      return
    }

    const existing = document.querySelector('script[data-kakao-map]')
    if (existing) existing.remove()

    const script = document.createElement('script')
    script.dataset.kakaoMap = 'true'
    script.src = `https://dapi.kakao.com/v2/maps/sdk.js?appkey=${key}&autoload=false`

    const timer = window.setTimeout(
      () => reject(new Error('Kakao 지도 로딩 시간이 초과되었습니다. Web 도메인 설정을 확인하세요.')),
      8000,
    )

    script.onload = () => {
      window.clearTimeout(timer)
      if (!window.kakao?.maps) {
        reject(new Error('Kakao JavaScript 키 또는 Web 도메인 설정을 확인하세요.'))
        return
      }
      window.kakao.maps.load(resolve)
    }

    script.onerror = () => {
      window.clearTimeout(timer)
      reject(new Error('Kakao 지도 SDK를 불러오지 못했습니다. API 키와 Web 도메인을 확인하세요.'))
    }

    document.head.appendChild(script)
  })
  return sdkPromise
}

const clearRoute = () => {
  routePolyline?.setMap(null)
  originMarker?.setMap(null)
  infoWindow?.close()
  routePolyline = null
  originMarker = null
  infoWindow = null
}

const renderMap = async () => {
  if (!result.value || !mapContainer.value) return
  try {
    await loadKakaoSdk()
    mapMessage.value = ''
    clearRoute()
    const center = new window.kakao.maps.LatLng(result.value.center.y, result.value.center.x)
    map = new window.kakao.maps.Map(mapContainer.value, { center, level: 4 })
    markers.forEach((marker) => marker.setMap(null))
    markers = result.value.banks.map((bank) => {
      const marker = new window.kakao.maps.Marker({
        map,
        position: new window.kakao.maps.LatLng(bank.y, bank.x),
        title: bank.name,
      })
      marker.bankId = bank.id
      window.kakao.maps.event.addListener(marker, 'click', () => {
        selectBank(bank, true)
      })
      return marker
    })
  } catch (error) {
    mapMessage.value = error.message
  }
}


const drawRoute = async (route) => {
  if (!route?.path?.length || !mapContainer.value) return
  await loadKakaoSdk()
  if (!map) {
    const center = new window.kakao.maps.LatLng(route.origin.y, route.origin.x)
    map = new window.kakao.maps.Map(mapContainer.value, { center, level: 4 })
  }

  clearRoute()
  const path = route.path.map((point) => new window.kakao.maps.LatLng(point.y, point.x))
  routePolyline = new window.kakao.maps.Polyline({
    path,
    strokeWeight: 6,
    strokeColor: '#2f6b5e',
    strokeOpacity: 0.92,
    strokeStyle: 'solid',
  })
  routePolyline.setMap(map)

  originMarker = new window.kakao.maps.Marker({
    map,
    position: new window.kakao.maps.LatLng(route.origin.y, route.origin.x),
    title: route.origin.name,
  })

  const bounds = new window.kakao.maps.LatLngBounds()
  bounds.extend(new window.kakao.maps.LatLng(route.origin.y, route.origin.x))
  path.forEach((point) => bounds.extend(point))
  map.setBounds(bounds)

  const destinationMarker = markers.find((marker) => marker.bankId === selectedBank.value?.id)
  if (destinationMarker) {
    infoWindow = new window.kakao.maps.InfoWindow({
      content: `<div style="padding:10px 12px;font-size:13px;line-height:1.45;white-space:nowrap;"><strong>${escapeHtml(selectedBank.value.name)}</strong><br>${escapeHtml(routeSummary.value)}</div>`,
    })
    infoWindow.open(map, destinationMarker)
  }
}

const search = async () => {
  if (!query.value.trim()) return
  isLoading.value = true
  errorMessage.value = ''
  routeMessage.value = ''
  routeInfo.value = null
  clearRoute()
  try {
    result.value = (await searchNearbyBanks(query.value.trim(), radius.value)).data
    selectedBank.value = result.value.banks[0] || null
    await nextTick()
    await renderMap()
  } catch (error) {
    errorMessage.value = error.response?.data?.detail || '주변 은행을 검색하지 못했습니다.'
  } finally {
    isLoading.value = false
  }
}


const loadRoute = async (bank = selectedBank.value) => {
  if (!bank) return
  selectedBank.value = bank
  isRouteLoading.value = true
  errorMessage.value = ''
  routeMessage.value = '\uacbd\ub85c\ub97c \ucc3e\ub294 \uc911\uc785\ub2c8\ub2e4.'
  try {
    routeInfo.value = (await getBankRoute(bank)).data
    await nextTick()
    try {
      await drawRoute(routeInfo.value)
      routeMessage.value = `${routeInfo.value.origin.name}\uc5d0\uc11c ${bank.name}\uae4c\uc9c0 \uacbd\ub85c\ub97c \uc9c0\ub3c4\uc5d0 \ud45c\uc2dc\ud588\uc2b5\ub2c8\ub2e4.`
    } catch (error) {
      routeMessage.value = `\uacbd\ub85c \uc815\ubcf4\ub294 \uac00\uc838\uc654\uc9c0\ub9cc \uc9c0\ub3c4 \ud45c\uc2dc\uc5d0 \uc2e4\ud328\ud588\uc2b5\ub2c8\ub2e4. ${error.message}`
    }
  } catch (error) {
    routeInfo.value = null
    clearRoute()
    routeMessage.value = ''
    errorMessage.value = error.response?.data?.detail || '\uc740\ud589\uae4c\uc9c0\uc758 \uacbd\ub85c\ub97c \ucc3e\uc9c0 \ubabb\ud588\uc2b5\ub2c8\ub2e4.'
  } finally {
    isRouteLoading.value = false
  }
}

const selectBank = (bank, shouldLoadRoute = false) => {
  selectedBank.value = bank
  if (map && window.kakao?.maps) map.panTo(new window.kakao.maps.LatLng(bank.y, bank.x))
  if (shouldLoadRoute) {
    loadRoute(bank)
  } else {
    routeInfo.value = null
    routeMessage.value = ''
    clearRoute()
  }
}

onMounted(search)
</script>

<template>
  <section class="bank-page page-shell">
    <div class="section-head">
      <div>
        <h1>은행지도</h1>
        <p>주소나 장소를 입력해 가까운 은행 지점을 찾습니다.</p>
      </div>
    </div>

    <form class="bank-search glass-panel" @submit.prevent="search">
      <input v-model="query" type="search" placeholder="예: 서울 강남구 테헤란로 212" required>
      <select v-model.number="radius">
        <option :value="1000">1km</option>
        <option :value="2000">2km</option>
        <option :value="5000">5km</option>
      </select>
      <button class="vintage-button" type="submit">검색</button>
    </form>

    <p v-if="errorMessage" class="state-card error">{{ errorMessage }}</p>
    <p v-if="routeMessage" class="route-message">{{ routeMessage }}</p>

    <div class="bank-layout">
      <div class="map-card vintage-card">
        <div ref="mapContainer" class="map">
          <div v-if="isLoading" class="grid-empty">위치를 찾는 중입니다.</div>
        </div>
        <p v-if="mapMessage" class="map-message">{{ mapMessage }}</p>
      </div>

      <aside class="bank-list">
        <div v-if="!result?.banks?.length" class="state-card">주변 은행이 없습니다.</div>
        <button
          v-for="bank in result?.banks"
          :key="bank.id"
          class="bank-item glass-panel"
          :class="{ active: selectedBank?.id === bank.id }"
          type="button"
          @click="selectBank(bank)"
        >
          <span class="bank-avatar">B</span>
          <span>
            <strong>{{ bank.name }}</strong>
            <small>{{ bank.road_address || bank.address }}</small>
            <em>{{ bank.distance.toLocaleString() }}m</em>
          </span>
        </button>
      </aside>
    </div>

    <article v-if="selectedBank" class="selected-card vintage-card">
      <div>
        <span class="bank-avatar">B</span>
        <div>
          <strong>{{ selectedBank.name }}</strong>
          <p>{{ selectedBank.road_address || selectedBank.address }}</p>
          <small>{{ selectedBank.phone || '전화번호 정보 없음' }}</small>
        </div>
      </div>
      <div class="selected-actions">
        <div v-if="routeSummary" class="route-summary">
          <span>{{ routeInfo.origin.name }} 출발</span>
          <strong>{{ routeSummary }}</strong>
        </div>
        <button type="button" :disabled="isRouteLoading" @click="loadRoute()">
          {{ isRouteLoading ? '경로 찾는 중' : '경로 찾기' }}
        </button>
        <a :href="selectedBank.place_url" target="_blank" rel="noopener">카카오맵에서 보기</a>
      </div>
    </article>
  </section>
</template>

<style scoped>
.bank-page {
  display: grid;
  gap: 18px;
}

.bank-search {
  display: grid;
  grid-template-columns: 1fr 120px auto;
  gap: 10px;
  padding: 12px;
}

.bank-search input,
.bank-search select {
  width: 100%;
  border: 2px solid rgba(23, 19, 13, 0.2);
  border-radius: 999px;
  background: rgba(255, 248, 231, 0.82);
  padding: 11px 14px;
}

.bank-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.35fr) minmax(300px, 0.65fr);
  gap: 18px;
}

.map-card {
  overflow: hidden;
}

.map {
  height: 480px;
  background:
    radial-gradient(circle at 20% 20%, rgba(216, 165, 38, 0.18), transparent 30%),
    linear-gradient(135deg, #dfe8cf, #f7efd8);
}

.map-message,
.route-message {
  margin: 0;
  border-top: 2px solid var(--color-ink);
  background: rgba(216, 165, 38, 0.18);
  color: var(--color-dark-gold);
  padding: 12px;
  font-weight: 900;
}

.route-message {
  border: 2px solid var(--color-ink);
  border-radius: 16px;
}

.bank-list {
  display: grid;
  align-content: start;
  gap: 10px;
  max-height: 480px;
  overflow: auto;
}

.bank-item {
  display: grid;
  grid-template-columns: 44px 1fr;
  gap: 11px;
  width: 100%;
  border: 2px solid transparent;
  color: var(--color-ink);
  padding: 12px;
  text-align: left;
}

.bank-item.active {
  border-color: var(--color-ink);
  background: rgba(216, 165, 38, 0.2);
}

.bank-item > span:last-child {
  display: grid;
  gap: 3px;
  min-width: 0;
}

.bank-item small {
  overflow: hidden;
  color: var(--color-muted);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.bank-item em {
  color: var(--color-dark-gold);
  font-size: 12px;
  font-style: normal;
  font-weight: 900;
}

.bank-avatar {
  display: grid;
  width: 44px;
  height: 44px;
  place-items: center;
  border: 2px solid var(--color-ink);
  border-radius: 50%;
  background: var(--color-money);
  color: var(--color-paper);
  font-weight: 900;
}

.selected-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 16px;
}

.selected-card > div {
  display: flex;
  align-items: center;
  gap: 12px;
}

.selected-card p {
  margin: 3px 0;
  color: var(--color-muted);
}

.selected-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  flex-wrap: wrap;
  gap: 10px;
}

.route-summary {
  display: grid;
  gap: 2px;
  color: var(--color-muted);
  font-size: 12px;
  font-weight: 900;
  text-align: right;
}

.route-summary strong {
  color: var(--color-ink);
  font-size: 15px;
}

.selected-card button {
  border: 2px solid var(--color-ink);
  border-radius: 999px;
  background: var(--color-gold);
  color: var(--color-ink);
  padding: 9px 13px;
  font-weight: 900;
}

.selected-card button:disabled {
  opacity: 0.56;
  cursor: wait;
}

.selected-card a {
  color: var(--color-dark-gold);
  font-weight: 900;
}

@media (max-width: 820px) {
  .bank-layout,
  .bank-search {
    grid-template-columns: 1fr;
  }

  .bank-list {
    max-height: 360px;
  }

  .selected-card {
    align-items: flex-start;
    flex-direction: column;
  }
}
</style>
