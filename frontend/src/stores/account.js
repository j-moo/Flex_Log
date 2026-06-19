import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import {
  getMe,
  login as loginRequest,
  refreshAccessToken,
  signup as signupRequest,
} from '@/api/accounts'


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
      return response.data.access
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
      fetchMe,
      refreshAccessToken: refreshAccessTokenAction,
      logout,
    }
  },
  {
    persist: true,
  },
)
