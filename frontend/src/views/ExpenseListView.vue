<script setup>
import { onMounted, ref } from 'vue'

import {
  getExpenses,
  deleteExpense,
} from '@/api/expenses'

const expenses = ref([])
const loading = ref(true)
const errorMessage = ref('')

const loadExpenses = async () => {
  loading.value = true
  errorMessage.value = ''

  try {
    const response = await getExpenses()
    expenses.value = response.data
  } catch (error) {
    console.error(error)
    errorMessage.value = '소비 기록을 불러오지 못했습니다.'
  } finally {
    loading.value = false
  }
}

const removeExpense = async (id) => {
  const confirmDelete = confirm(
    '정말 삭제하시겠습니까?'
  )

  if (!confirmDelete) return

  try {
    await deleteExpense(id)

    expenses.value =
      expenses.value.filter(
        expense => expense.id !== id
      )
  } catch (error) {
    console.error(error)
    alert('삭제에 실패했습니다.')
  }
}

onMounted(loadExpenses)
</script>

<template>
  <section>
    <h1>내 소비 기록</h1>

    <p v-if="loading">
      불러오는 중...
    </p>

    <p v-else-if="errorMessage">
      {{ errorMessage }}
    </p>

    <div
      v-else-if="expenses.length"
      v-for="expense in expenses"
      :key="expense.id"
      class="expense-card"
    >
      <h3>
        {{ expense.category_name }}
      </h3>

      <p>
        금액:
        {{ expense.amount.toLocaleString() }}원
      </p>

      <p>
        내용:
        {{ expense.content }}
      </p>

      <p>
        공개 여부:
        {{ expense.is_visible ? '공개' : '비공개' }}
      </p>

      <p>
        작성일:
        {{ expense.created_at.slice(0, 10) }}
      </p>

      <RouterLink
        :to="`/expenses/${expense.id}/edit`"
      >
        수정
      </RouterLink>

      <button
        @click="removeExpense(expense.id)"
      >
        삭제
      </button>
    </div>

    <p v-else>
      아직 등록된 소비 기록이 없습니다.
    </p>
  </section>
</template>

<style scoped>
.expense-card {
  border: 1px solid #ddd;
  margin: 10px 0;
  padding: 15px;
  border-radius: 8px;
}

a {
  margin-right: 10px;
}
</style>