import { ref } from 'vue'
import { defineStore } from 'pinia'

import api from '../api/client'


export const useAnalysisStore = defineStore('analysis', () => {
  const latest = ref(null)
  const history = ref([])
  const isLoading = ref(false)
  const errorMessage = ref('')

  const fetchLatest = async () => {
    errorMessage.value = ''
    try {
      const response = await api.get('/api/v1/analysis/monthly/latest/')
      latest.value = response.data
      return response.data
    } catch (error) {
      if (error.response?.status === 404) {
        latest.value = null
        return null
      }
      errorMessage.value = '최신 분석 결과를 불러오지 못했습니다.'
      throw error
    }
  }

  const fetchHistory = async () => {
    const response = await api.get('/api/v1/analysis/monthly/history/')
    history.value = response.data
    return response.data
  }

  const analyzeCurrentMonth = async (monthlyIncome = 0) => {
    const today = new Date()
    const payload = {
      year: today.getFullYear(),
      month: today.getMonth() + 1,
      monthly_income: Math.max(0, Math.round(Number(monthlyIncome || 0))),
    }

    isLoading.value = true
    errorMessage.value = ''
    try {
      const response = await api.post('/api/v1/analysis/monthly/', payload)
      latest.value = response.data
      await fetchHistory()
      return response.data
    } catch (error) {
      errorMessage.value = 'AI 분석 요청에 실패했습니다.'
      throw error
    } finally {
      isLoading.value = false
    }
  }

  return {
    latest,
    history,
    isLoading,
    errorMessage,
    fetchLatest,
    fetchHistory,
    analyzeCurrentMonth,
  }
})
