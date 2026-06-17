<script setup>
import { onMounted, ref } from 'vue'

import api from '../api/client'
import { formatAmount, formatDate, isVideo } from '../utils/format'


const logs = ref([])
const isLoading = ref(true)
const errorMessage = ref('')

const loadLogs = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const response = await api.get('/api/v1/expenses/')
    logs.value = response.data
  } catch {
    errorMessage.value = '소비 로그를 불러오지 못했습니다.'
  } finally {
    isLoading.value = false
  }
}

const removeLog = async (log) => {
  if (!window.confirm('이 소비 로그를 삭제할까요?')) return
  try {
    await api.delete(`/api/v1/expenses/${log.id}/`)
    logs.value = logs.value.filter((item) => item.id !== log.id)
  } catch {
    errorMessage.value = '소비 로그를 삭제하지 못했습니다.'
  }
}

onMounted(loadLogs)
</script>

<template>
  <section class="d-grid gap-3">
    <div class="d-flex flex-column flex-sm-row justify-content-between gap-2">
      <div>
        <h1 class="h3 mb-1">내 소비 로그</h1>
        <p class="text-secondary mb-0">작성한 소비 로그 목록입니다.</p>
      </div>
      <RouterLink class="btn btn-primary align-self-start" :to="{ name: 'log-create' }">로그 작성</RouterLink>
    </div>

    <div v-if="isLoading" class="alert alert-secondary">불러오는 중입니다.</div>
    <div v-else-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
    <div v-else-if="logs.length" class="row g-3">
      <div v-for="log in logs" :key="log.id" class="col-12 col-md-6 col-xl-4">
        <article class="card h-100">
          <video v-if="log.media && isVideo(log.media)" class="log-media card-img-top" :src="log.media" controls></video>
          <img v-else-if="log.media" class="log-media card-img-top" :src="log.media" alt="소비 로그 미디어">
          <div class="card-body d-grid gap-2">
            <div class="d-flex justify-content-between gap-2">
              <span class="badge text-bg-light border">{{ log.category_name }}</span>
              <strong>{{ formatAmount(log.amount) }}</strong>
            </div>
            <p v-if="log.content" class="content-preline mb-0">{{ log.content }}</p>
            <p class="small text-secondary mb-0">{{ formatDate(log.created_at) }}</p>
            <div class="d-flex gap-2 flex-wrap">
              <RouterLink class="btn btn-outline-secondary btn-sm" :to="{ name: 'log-edit', params: { id: log.id } }">수정</RouterLink>
              <button class="btn btn-outline-danger btn-sm" type="button" @click="removeLog(log)">삭제</button>
            </div>
          </div>
        </article>
      </div>
    </div>
    <div v-else class="card">
      <div class="card-body text-center py-5">
        <p class="text-secondary">아직 작성한 소비 로그가 없습니다.</p>
        <RouterLink class="btn btn-primary" :to="{ name: 'log-create' }">첫 로그 작성</RouterLink>
      </div>
    </div>
  </section>
</template>
