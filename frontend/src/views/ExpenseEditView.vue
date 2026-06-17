<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'

import {
  getCategories,
  getExpense,
  updateExpense,
} from '@/api/expenses'

const route = useRoute()
const router = useRouter()

const categories = ref([])
const imageFile = ref(null)
const imagePreview = ref('')

const form = reactive({
  category: '',
  amount: '',
  content: '',
  is_visible: true,
})

const isLoading = ref(true)
const isSubmitting = ref(false)
const errorMessage = ref('')

const loadCategories = async () => {
  const response = await getCategories()
  categories.value = response.data
}

const loadExpense = async () => {
  try {
    const response = await getExpense(route.params.id)
    const expense = response.data

    form.category = expense.category
    form.amount = expense.amount
    form.content = expense.content
    form.is_visible = expense.is_visible
    imagePreview.value = expense.media || ''
  } catch (error) {
    console.error(error)
    errorMessage.value = '소비 기록을 불러오지 못했습니다.'
  }
}

const selectImage = (event) => {
  const file = event.target.files?.[0] || null
  imageFile.value = file

  if (file) {
    imagePreview.value = URL.createObjectURL(file)
  }
}

const submit = async () => {
  isSubmitting.value = true
  errorMessage.value = ''

  const payload = new FormData()

  payload.append('category', form.category)
  payload.append('amount', form.amount)
  payload.append('content', form.content)
  payload.append('is_visible', form.is_visible)

  if (imageFile.value) {
    payload.append('media', imageFile.value)
  }

  try {
    await updateExpense(route.params.id, payload)

    alert('소비 기록이 수정되었습니다.')
    router.push('/expenses')
  } catch (error) {
    console.error(error)

    const data = error.response?.data

    errorMessage.value = data
      ? Object.values(data).flat().join(' ')
      : '소비 기록 수정 중 오류가 발생했습니다.'
  } finally {
    isSubmitting.value = false
  }
}

onMounted(async () => {
  isLoading.value = true
  await loadCategories()
  await loadExpense()
  isLoading.value = false
})
</script>

<template>
  <section>
    <h1>소비 기록 수정</h1>

    <p v-if="isLoading">
      불러오는 중...
    </p>

    <form v-else @submit.prevent="submit">
      <div>
        <label>카테고리</label>
        <select v-model="form.category" required>
          <option disabled value="">
            카테고리를 선택하세요
          </option>

          <option
            v-for="category in categories"
            :key="category.id"
            :value="category.id"
          >
            {{ category.name }}
          </option>
        </select>
      </div>

      <div>
        <label>금액</label>
        <input
          v-model="form.amount"
          type="number"
          min="0"
          required
        >
      </div>

      <div>
        <label>내용</label>
        <textarea
          v-model="form.content"
          rows="4"
          placeholder="무엇을 구매했나요?"
        ></textarea>
      </div>

      <div>
        <label>
          <input
            v-model="form.is_visible"
            type="checkbox"
          >
          친구에게 공개하기
        </label>
      </div>

      <div v-if="imagePreview">
        <p>현재 미디어</p>
        <img
          v-if="!imagePreview.endsWith('.mp4') && !imagePreview.endsWith('.webm')"
          :src="imagePreview"
          alt="소비 기록 이미지"
          style="max-width: 200px;"
        >
      </div>

      <div>
        <label>사진 / 영상 변경</label>
        <input
          type="file"
          accept="image/*,video/*"
          @change="selectImage"
        >
      </div>

      <button :disabled="isSubmitting">
        {{ isSubmitting ? '수정 중...' : '수정하기' }}
      </button>

      <p v-if="errorMessage">
        {{ errorMessage }}
      </p>
    </form>
  </section>
</template>