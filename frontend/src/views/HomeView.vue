<script setup>
import { computed, onMounted, ref } from 'vue'

import api from '../api/client'
import { useAccountStore } from '../stores/account'
import { formatAmount, formatDate } from '../utils/format'


const account = useAccountStore()
const analysis = ref(null)
const logs = ref([])
const isLoading = ref(false)

const displayName = computed(() => account.user?.name || account.user?.username || '')

const loadDashboard = async () => {
  if (!account.isAuthenticated) return
  isLoading.value = true
  try {
    const [analysisResponse, logsResponse] = await Promise.all([
      api.get('/api/v1/analysis/monthly/'),
      api.get('/api/v1/expenses/'),
    ])
    analysis.value = analysisResponse.data
    logs.value = logsResponse.data.slice(0, 5)
  } finally {
    isLoading.value = false
  }
}

onMounted(loadDashboard)
</script>

<template>
  <section v-if="account.isAuthenticated" class="d-grid gap-4">
    <div class="d-flex flex-column flex-md-row justify-content-between gap-3">
      <div>
        <h1 class="h3 mb-1">{{ displayName }}님의 Flex Log</h1>
        <p class="text-secondary mb-0">오늘 기준 월별 소비와 최근 로그입니다.</p>
      </div>
      <RouterLink class="btn btn-primary align-self-start" :to="{ name: 'log-create' }">소비 로그 작성</RouterLink>
    </div>

    <div v-if="isLoading" class="alert alert-secondary">불러오는 중입니다.</div>

    <div class="row g-3">
      <div class="col-12 col-md-4">
        <div class="card h-100">
          <div class="card-body">
            <p class="text-secondary mb-1">이번 달 소비</p>
            <div class="summary-value">{{ formatAmount(analysis?.total_amount) }}</div>
          </div>
        </div>
      </div>
      <div class="col-12 col-md-4">
        <div class="card h-100">
          <div class="card-body">
            <p class="text-secondary mb-1">로그 수</p>
            <div class="summary-value">{{ analysis?.log_count || 0 }}개</div>
          </div>
        </div>
      </div>
      <div class="col-12 col-md-4">
        <div class="card h-100">
          <div class="card-body">
            <p class="text-secondary mb-1">가장 큰 카테고리</p>
            <div class="summary-value">
              {{ analysis?.category_items?.[0]?.name || '-' }}
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="card-header bg-white d-flex justify-content-between align-items-center">
        <h2 class="h5 mb-0">최근 로그</h2>
        <RouterLink class="btn btn-outline-secondary btn-sm" :to="{ name: 'logs' }">전체 보기</RouterLink>
      </div>
      <div class="list-group list-group-flush">
        <div v-if="!logs.length" class="list-group-item text-secondary">아직 작성한 로그가 없습니다.</div>
        <div v-for="log in logs" :key="log.id" class="list-group-item">
          <div class="d-flex justify-content-between gap-3">
            <div>
              <span class="badge text-bg-light border me-2">{{ log.category_name }}</span>
              <span>{{ log.content || '내용 없음' }}</span>
            </div>
            <div class="text-end flex-shrink-0">
              <strong>{{ formatAmount(log.amount) }}</strong>
              <div class="small text-secondary">{{ formatDate(log.created_at) }}</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </section>

  <section v-else class="auth-card card">
    <div class="card-body p-4">
      <h1 class="h3 mb-3">Flex Log</h1>
      <p class="text-secondary">소비 로그를 작성하려면 로그인하거나 계정을 생성하세요.</p>
      <div class="d-flex gap-2">
        <RouterLink class="btn btn-primary" :to="{ name: 'login' }">로그인</RouterLink>
        <RouterLink class="btn btn-outline-secondary" :to="{ name: 'signup' }">회원가입</RouterLink>
      </div>
    </div>
  </section>
</template>
