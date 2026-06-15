<script setup>
import { onMounted, ref } from 'vue'

import api from '../api/client'


const logs = ref([])
const isLoading = ref(true)
const errorMessage = ref('')

const formatAmount = (amount) => `${Number(amount).toLocaleString('ko-KR')}원`
const formatDate = (value) => new Intl.DateTimeFormat('ko-KR', {
  dateStyle: 'medium',
  timeStyle: 'short',
}).format(new Date(value))
const isVideo = (url) => /\.(mp4|webm)(?:\?|$)/i.test(url || '')

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
  <section>
    <div class="section-header">
      <div>
        <h1>내 소비 로그</h1>
        <p class="help">내가 기록한 소비 내역을 확인하고 관리합니다.</p>
      </div>
      <RouterLink class="button" :to="{ name: 'log-create' }">새 로그 작성</RouterLink>
    </div>

    <p v-if="isLoading" class="help">불러오는 중...</p>
    <p v-else-if="errorMessage" class="error">{{ errorMessage }}</p>
    <div v-else-if="logs.length" class="log-grid">
      <article v-for="log in logs" :key="log.id" class="log-card">
        <video v-if="log.media && isVideo(log.media)" class="log-media" :src="log.media" controls></video>
        <img v-else-if="log.media" class="log-media" :src="log.media" alt="소비 로그 미디어">
        <div class="log-body">
          <div class="log-heading">
            <span class="badge">{{ log.category_name }}</span>
            <strong>{{ formatAmount(log.amount) }}</strong>
          </div>
          <p v-if="log.content" class="log-content">{{ log.content }}</p>
          <p class="help">{{ formatDate(log.created_at) }}</p>
          <div class="row-actions">
            <RouterLink class="button secondary" :to="{ name: 'log-edit', params: { id: log.id } }">수정</RouterLink>
            <button class="button danger" type="button" @click="removeLog(log)">삭제</button>
          </div>
        </div>
      </article>
    </div>
    <div v-else class="empty-state">
      <p>아직 작성한 소비 로그가 없습니다.</p>
      <RouterLink class="button" :to="{ name: 'log-create' }">첫 로그 작성</RouterLink>
    </div>
  </section>
</template>
