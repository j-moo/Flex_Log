<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'

import { createExpense, getCategories } from '@/api/expenses'


const router = useRouter()

const categories = ref([])
const imageFile = ref(null)

const form = reactive({
  category: '',
  amount: '',
  content: '',
  is_visible: true,
})

const errorMessage = ref('')
const isSubmitting = ref(false)


// 카테고리 불러오기
const loadCategories = async () => {
  try {
    const response = await getCategories()
    categories.value = response.data
  } catch (error) {
    console.error(error)
    errorMessage.value = '카테고리를 불러오지 못했습니다.'
  }
}


// 이미지 선택
const selectImage = (event) => {
  imageFile.value = event.target.files?.[0] || null
}


// 소비 기록 저장
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
    await createExpense(payload)

    alert('소비 기록이 등록되었습니다.')

    router.push('/expenses')

  } catch (error) {
    console.error(error)

    const data = error.response?.data

    errorMessage.value = data
      ? Object.values(data).flat().join(' ')
      : '소비 기록 저장 중 오류가 발생했습니다.'

  } finally {
    isSubmitting.value = false
  }
}


onMounted(() => {
  loadCategories()
})
</script>


<template>
  <section>
    <h1>소비 기록 작성</h1>


    <form @submit.prevent="submit">

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


      <div>
        <label>사진 / 영상</label>
        <input
          type="file"
          accept="image/*,video/*"
          @change="selectImage"
        >
      </div>


      <button :disabled="isSubmitting">
        {{ isSubmitting ? '저장 중...' : '등록하기' }}
      </button>


      <p v-if="errorMessage">
        {{ errorMessage }}
      </p>

    </form>

  </section>
</template>