import api from './client'


// 회원가입
export const signup = (payload) => {
  return api.post('/api/v1/accounts/signup/', payload)
}


// 로그인
export const login = (payload) => {
  return api.post('/api/v1/accounts/login/', payload)
}


// 내 정보 조회
export const getMe = () => {
  return api.get('/api/v1/accounts/me/')
}


// access token 재발급
export const refreshAccessToken = (refresh) => {
  return api.post(
    '/api/v1/accounts/token/refresh/',
    {
      refresh: refresh,
    }
  )
}