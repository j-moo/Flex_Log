import { computed, ref } from 'vue'
import { defineStore } from 'pinia'
import axios from 'axios'
const API_URL = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000'
export const useAccountStore = defineStore('account', () => {
  const accessToken=ref(null); const refreshToken=ref(null); const user=ref(null)
  const isLogin=computed(()=>!!accessToken.value)
  const signUp=async(payload)=>{ const r=await axios.post(`${API_URL}/api/v1/accounts/signup/`, payload); accessToken.value=r.data.access; refreshToken.value=r.data.refresh; user.value=r.data.user; return r.data }
  const logIn=async(payload)=>{ const r=await axios.post(`${API_URL}/api/v1/accounts/login/`, payload); accessToken.value=r.data.access; refreshToken.value=r.data.refresh; await fetchMe(); return r.data }
  const refreshAccessToken=async()=>{ const r=await axios.post(`${API_URL}/api/v1/accounts/token/refresh/`, {refresh: refreshToken.value}); accessToken.value=r.data.access; return r.data.access }
  const fetchMe=async()=>{ if(!accessToken.value) return null; const r=await axios.get(`${API_URL}/api/v1/accounts/me/`, {headers:{Authorization:`Bearer ${accessToken.value}`}}); user.value=r.data; return r.data }
  const clearAuth=()=>{ accessToken.value=null; refreshToken.value=null; user.value=null }
  const logOut=()=>clearAuth()
  return {API_URL, accessToken, refreshToken, user, isLogin, signUp, logIn, refreshAccessToken, fetchMe, clearAuth, logOut}
}, {persist:true})
