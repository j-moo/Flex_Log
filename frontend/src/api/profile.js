import api from './client'


export const getMyProfile = () => {
  return api.get('/api/v1/profiles/me/')
}


export const updateMyProfile = (payload) => {
  return api.patch('/api/v1/profiles/me/', payload)
}


export const getProfile = (userId) => {
  return api.get(`/api/v1/profiles/${userId}/`)
}
