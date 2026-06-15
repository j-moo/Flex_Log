import { ref, computed } from 'vue'
import { defineStore } from 'pinia'

import {
  signup,
  login,
  getMe,
  refreshAccessToken,
} from '@/api/accounts'


export const useAccountStore = defineStore(
  'account',
  () => {

    // ======================
    // state
    // ======================

    const accessToken = ref(null)
    const refreshToken = ref(null)
    const user = ref(null)


    // 로그인 여부
    const isAuthenticated = computed(() => {
      return !!accessToken.value
    })


    // ======================
    // actions
    // ======================


    // 회원가입
    const signupUser = async (payload) => {
      const response = await signup(payload)

      return response.data
    }


    // 로그인
    const loginUser = async (payload) => {
      const response = await login(payload)


      accessToken.value = response.data.access

      refreshToken.value = response.data.refresh


      await fetchMe()


      return response.data
    }


    // 내 정보 조회
    const fetchMe = async () => {
      const response = await getMe()


      user.value = response.data


      return response.data
    }


    // access token 재발급
    const refreshAccessTokenAction = async () => {

      const response =
        await refreshAccessToken(refreshToken.value)


      accessToken.value = response.data.access


      return response.data.access
    }


    // 로그아웃
    const logout = () => {
      accessToken.value = null
      refreshToken.value = null
      user.value = null
    }


    // ======================
    // return
    // ======================

    return {
      accessToken,
      refreshToken,
      user,

      isAuthenticated,

      signupUser,
      loginUser,
      fetchMe,

      // client.js에서 호출
      refreshAccessToken:
        refreshAccessTokenAction,

      logout,
    }
  },

  {
    persist: true,
  }
)