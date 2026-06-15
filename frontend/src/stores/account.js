import axios from 'axios'
import { computed, ref } from 'vue'
import { defineStore } from 'pinia'


const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'

export const useAccountStore = defineStore(
  'account',
  () => {
    const accessToken = ref(null)
    const refreshToken = ref(null)
    const user = ref(null)

    const isAuthenticated = computed(() => Boolean(accessToken.value))

    const signup = async (payload) => {
      const response = await axios.post(`${API_URL}/api/v1/accounts/signup/`, payload)
      accessToken.value = response.data.access
      refreshToken.value = response.data.refresh
      user.value = response.data.user
      return response.data
    }

    const login = async (payload) => {
      const response = await axios.post(`${API_URL}/api/v1/accounts/login/`, payload)
      accessToken.value = response.data.access
      refreshToken.value = response.data.refresh
      await fetchMe()
      return response.data
    }

    const refreshAccessToken = async () => {
      const response = await axios.post(`${API_URL}/api/v1/accounts/token/refresh/`, {
        refresh: refreshToken.value,
      })
      accessToken.value = response.data.access
      return response.data.access
    }

    const fetchMe = async () => {
      if (!accessToken.value) return null
      const response = await axios.get(`${API_URL}/api/v1/accounts/me/`, {
        headers: { Authorization: `Bearer ${accessToken.value}` },
      })
      user.value = response.data
      return response.data
    }

    const logout = () => {
      accessToken.value = null
      refreshToken.value = null
      user.value = null
    }

    return {
      accessToken,
      refreshToken,
      user,
      isAuthenticated,
      signup,
      login,
      refreshAccessToken,
      fetchMe,
      logout,
    }
  },
  { persist: true },
)
