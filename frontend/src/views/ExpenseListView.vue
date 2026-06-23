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
    logs.value = (await getExpenses()).data
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
  <section class="logs-page page-shell">
    <div class="section-head">
      <div>
        <h1>내 소비 로그</h1>
        <p>작성한 소비 기록을 관리합니다.</p>
      </div>
      <RouterLink class="vintage-button" :to="{ name: 'log-create' }">로그 작성</RouterLink>
    </div>

    <div v-if="isLoading" class="state-card">불러오는 중입니다.</div>
    <div v-else-if="errorMessage" class="state-card error">{{ errorMessage }}</div>

    <div v-else-if="logs.length" class="log-grid">
      <article v-for="(log, index) in logs" :key="log.id" class="log-card vintage-card stagger-item" :style="{ '--delay': `${index * 60}ms` }">
        <div v-if="log.media" class="media-frame">
          <video v-if="isVideo(log.media)" class="log-media" :src="log.media" controls></video>
          <img v-else class="log-media" :src="log.media" alt="소비 로그 이미지">
          <div v-if="log.overlay_text" class="overlay-text">{{ log.overlay_text }}</div>
        </div>
        <div class="log-body">
          <div class="log-top">
            <span class="vintage-badge">{{ log.category_name }}</span>
            <strong>{{ formatAmount(log.amount) }}</strong>
          </div>
          <h2>{{ log.title || log.product_name || '소비 기록' }}</h2>
          <p v-if="log.merchant">{{ log.merchant }}</p>
          <p v-if="log.content" class="content-preline">{{ log.content }}</p>
          <small>{{ formatDate(log.created_at) }}</small>
          <div class="log-actions">
            <RouterLink :to="{ name: 'log-edit', params: { id: log.id } }">수정</RouterLink>
            <button type="button" @click="removeLog(log)">삭제</button>
          </div>
        </div>
      </article>
    </div>

    <div v-else class="state-card">
      <div>
        <p>아직 작성한 소비 로그가 없습니다.</p>
        <RouterLink class="vintage-button" :to="{ name: 'log-create' }">첫 로그 작성</RouterLink>
      </div>
    </div>
  </section>
</template>

<style scoped>
.logs-page {
  display: grid;
  gap: 18px;
}

.log-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}

.log-card {
  overflow: hidden;
}

.log-body {
  display: grid;
  gap: 8px;
  padding: 14px;
}

.log-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
}

.log-top strong {
  color: var(--color-dark-gold);
}

.log-body h2 {
  margin: 0;
  font-size: 20px;
}

.log-body p,
.log-body small {
  margin: 0;
  color: var(--color-muted);
}

.log-actions {
  display: flex;
  gap: 8px;
}

.log-actions a,
.log-actions button {
  border: 2px solid var(--color-ink);
  border-radius: 999px;
  background: var(--color-paper);
  color: var(--color-ink);
  padding: 7px 11px;
  font-size: 12px;
  font-weight: 900;
}

.log-actions button {
  color: var(--color-red);
}

@media (max-width: 900px) {
  .log-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}

@media (max-width: 560px) {
  .log-grid {
    grid-template-columns: 1fr;
  }
}
</style>
