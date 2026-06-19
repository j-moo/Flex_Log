<script setup>
import { onMounted, ref } from 'vue'

import { deleteExpense, getExpenses } from '../api/expenses'
import { formatAmount, formatDate, isVideo } from '../utils/format'


const logs = ref([])
const isLoading = ref(true)
const errorMessage = ref('')

const loadLogs = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const response = await getExpenses()
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
    await deleteExpense(log.id)
    logs.value = logs.value.filter((item) => item.id !== log.id)
  } catch {
    errorMessage.value = '소비 로그를 삭제하지 못했습니다.'
  }
}

onMounted(loadLogs)
</script>

<template>
  <section>
    <div class="section-head">
      <div>
        <h1>내 소비 로그</h1>
        <p>작성한 소비 기록을 관리합니다.</p>
      </div>
      <RouterLink class="btn btn-primary" :to="{ name: 'log-create' }">로그 작성</RouterLink>
    </div>

    <div v-if="isLoading" class="alert alert-secondary">불러오는 중입니다.</div>
    <div v-else-if="errorMessage" class="alert alert-danger">{{ errorMessage }}</div>
    <div v-else-if="logs.length" class="row g-3">
      <div v-for="log in logs" :key="log.id" class="col-12 col-md-6 col-xl-4">
        <article class="surface overflow-hidden h-100">
          <div v-if="log.media" class="media-frame">
            <video v-if="isVideo(log.media)" class="log-media" :src="log.media" controls></video>
            <img v-else class="log-media" :src="log.media" alt="소비 로그 이미지">
            <div v-if="log.overlay_text" class="overlay-text">{{ log.overlay_text }}</div>
          </div>
          <div class="p-3 d-grid gap-2">
            <div class="d-flex justify-content-between gap-2">
              <span class="badge text-bg-light border">{{ log.category_name }}</span>
              <strong>{{ formatAmount(log.amount) }}</strong>
            </div>
            <strong v-if="log.product_name">{{ log.product_name }}</strong>
            <span v-if="log.merchant" class="text-secondary small">{{ log.merchant }}</span>
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
    <div v-else class="surface grid-empty">
      <div>
        <p class="mb-2">아직 작성한 소비 로그가 없습니다.</p>
        <RouterLink class="btn btn-primary btn-sm" :to="{ name: 'log-create' }">첫 로그 작성</RouterLink>
      </div>
    </div>
  </section>
</template>
