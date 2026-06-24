import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import {
  getMe,
  login as loginRequest,
  logout as logoutRequest,
  refreshAccessToken,
  signup as signupRequest,
} from '@/api/accounts'


const sessionStorageProvider = {
  getItem: (key) => (typeof window === 'undefined' ? null : window.sessionStorage.getItem(key)),
  setItem: (key, value) => {
    if (typeof window !== 'undefined') window.sessionStorage.setItem(key, value)
  },
  removeItem: (key) => {
    if (typeof window !== 'undefined') window.sessionStorage.removeItem(key)
  },
}


export const useAccountStore = defineStore(
  'account',
  () => {
    const accessToken = ref(null)
    const refreshToken = ref(null)
    const user = ref(null)

    const isAuthenticated = computed(() => Boolean(accessToken.value))

    const setSession = async ({ access, refresh, user: responseUser }) => {
      accessToken.value = access
      refreshToken.value = refresh
      user.value = responseUser || null
      if (!user.value && accessToken.value) {
        await fetchMe()
      }
    }

    const signup = async (payload) => {
      const response = await signupRequest(payload)
      await setSession(response.data)
      return response.data
    }

    const login = async (payload) => {
      const response = await loginRequest(payload)
      await setSession(response.data)
      return response.data
    }

    const fetchMe = async () => {
      const response = await getMe()
      user.value = response.data
      return response.data
    }

    const refreshAccessTokenAction = async () => {
      const response = await refreshAccessToken(refreshToken.value)
      accessToken.value = response.data.access
      if (response.data.refresh) refreshToken.value = response.data.refresh
      return response.data.access
    }

    const clearSession = () => {
      accessToken.value = null
      refreshToken.value = null
      user.value = null
    }

    const logout = async () => {
      const token = refreshToken.value
      try {
        if (token) await logoutRequest(token)
      } finally {
        clearSession()
      }
    }

    return {
      accessToken,
      refreshToken,
      user,
      isAuthenticated,
      signup,
      login,
      fetchMe,
      refreshAccessToken: refreshAccessTokenAction,
      logout,
      clearSession,
    }
  },
  {
    persist: {
      storage: sessionStorageProvider,
    },
  },
)
