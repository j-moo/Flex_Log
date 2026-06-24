<script setup>
import { computed, onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import { deleteExpense, getExpense } from '../api/expenses'
import ExpenseDeleteConfirmModal from '../components/feed/ExpenseDeleteConfirmModal.vue'
import FeedCard from '../components/feed/FeedCard.vue'

const route = useRoute()
const router = useRouter()
const log = ref(null)
const errorMessage = ref('')
const deleteModalOpen = ref(false)
const deleteErrorMessage = ref('')
const isDeleting = ref(false)

const deleteTargetTitle = computed(() => log.value?.title || log.value?.content || '선택한 게시글')

const openDeleteConfirm = () => {
  deleteModalOpen.value = true
  deleteErrorMessage.value = ''
  errorMessage.value = ''
}

const closeDeleteConfirm = () => {
  if (isDeleting.value) return
  deleteModalOpen.value = false
  deleteErrorMessage.value = ''
}

const confirmDelete = async (confirmation) => {
  if (!log.value) return
  isDeleting.value = true
  deleteErrorMessage.value = ''
  errorMessage.value = ''

  try {
    await deleteExpense(log.value.id, confirmation)
    await router.push({ name: 'profile' })
  } catch (error) {
    deleteErrorMessage.value = error.response?.data?.detail || '게시글 삭제에 실패했습니다.'
  } finally {
    isDeleting.value = false
  }
}

onMounted(async () => {
  try {
    log.value = (await getExpense(route.params.id)).data
  } catch {
    errorMessage.value = '게시물을 불러오지 못했습니다.'
  }
})
</script>

<template>
  <section class="detail-wrap page-shell">
    <p v-if="errorMessage" class="state-card error">{{ errorMessage }}</p>
    <p v-else-if="!log" class="state-card">게시물을 불러오는 중입니다.</p>
    <template v-else>
      <FeedCard :log="log" comments-default-open />
      <div v-if="log.can_edit" class="owner-actions">
        <RouterLink class="vintage-button" :to="{ name: 'log-edit', params: { id: log.id } }">게시물 수정</RouterLink>
        <button class="danger-button" type="button" @click="openDeleteConfirm">삭제</button>
      </div>

      <ExpenseDeleteConfirmModal
        :open="deleteModalOpen"
        :target-title="deleteTargetTitle"
        :is-deleting="isDeleting"
        :error-message="deleteErrorMessage"
        @close="closeDeleteConfirm"
        @confirm="confirmDelete"
      />
    </template>
  </section>
</template>

<style scoped>
.detail-wrap {
  width: min(100%, 650px);
  margin: auto;
}

.owner-actions {
  display: flex;
  gap: 10px;
  justify-content: center;
}

.danger-button {
  border: 2px solid var(--color-ink);
  border-radius: 999px;
  padding: 9px 14px;
  font-weight: 900;
}

.danger-button {
  background: var(--color-red);
  color: var(--color-paper);
}

.danger-button:disabled {
  opacity: 0.48;
  cursor: not-allowed;
}
</style>
