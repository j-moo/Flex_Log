import axios from 'axios'
import { useAccountStore } from '@/stores/account'


const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000',
})


api.interceptors.request.use((config) => {
  const account = useAccountStore()

  if (account.accessToken) {
    config.headers.Authorization = `Bearer ${account.accessToken}`
  }

  return config
})


api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const account = useAccountStore()
    const request = error.config

    if (
      error.response?.status === 401 &&
      account.refreshToken &&
      request &&
      !request._retry
    ) {
      request._retry = true

      try {
        await account.refreshAccessToken()
        request.headers.Authorization = `Bearer ${account.accessToken}`
        return api(request)
      } catch {
        account.logout()
      }
    }

    return Promise.reject(error)
  },
)


export default api
