import axios from 'axios'
import { useAccountStore } from '@/stores/account'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000',
})


/**
 * 요청 전에 access token 자동 추가
 */
api.interceptors.request.use((config) => {
  const account = useAccountStore()

  if (account.accessToken) {
    config.headers.Authorization = `Bearer ${account.accessToken}`
  }

  return config
})


/**
 * access token 만료 시 자동 재발급
 */
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

        request.headers.Authorization =
          `Bearer ${account.accessToken}`

        return api(request)

      } catch (e) {
        account.logout()
      }
    }

    return Promise.reject(error)
  }
)


export default api