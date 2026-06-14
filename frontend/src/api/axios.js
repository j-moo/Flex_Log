import axios from 'axios'
import { useAccountStore } from '@/stores/account'
const api = axios.create({ baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000' })
api.interceptors.request.use((config) => { const store = useAccountStore(); if (store.accessToken) config.headers.Authorization = `Bearer ${store.accessToken}`; return config })
api.interceptors.response.use((res)=>res, async (err)=>{ const store=useAccountStore(); const req=err.config; if(err.response?.status===401 && store.refreshToken && !req._retry){ req._retry=true; await store.refreshAccessToken(); req.headers.Authorization=`Bearer ${store.accessToken}`; return api(req)} return Promise.reject(err) })
export default api
