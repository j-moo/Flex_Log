import api from './client'


// 내 프로필 조회
export const getMyProfile = () => {
  return api.get('/api/v1/profiles/me/')
}


// 내 프로필 수정
export const updateMyProfile = (payload) => {
  return api.patch(
    '/api/v1/profiles/me/',
    payload
  )
}