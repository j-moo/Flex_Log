import { ref } from 'vue'
import { defineStore } from 'pinia'

import {
  getMyProfile,
  updateMyProfile,
} from '@/api/profiles'


export const useProfileStore = defineStore(
  'profile',
  () => {
    // ====================
    // state
    // ====================

    const profile = ref(null)


    // ====================
    // actions
    // ====================


    // 내 프로필 조회
    const fetchProfile = async () => {
      const response = await getMyProfile()

      profile.value = response.data

      return response.data
    }


    // 내 프로필 수정
    const updateProfile = async (payload) => {
      const response = await updateMyProfile(payload)

      profile.value = response.data

      return response.data
    }


    // 상태 초기화
    const clearProfile = () => {
      profile.value = null
    }


    return {
      profile,

      fetchProfile,
      updateProfile,
      clearProfile,
    }
  },

  {
    persist: true,
  }
)