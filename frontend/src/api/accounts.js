import api from './client'


export const signup = (payload) => {
  return api.post('/api/v1/accounts/signup/', payload)
}


export const login = (payload) => {
  return api.post('/api/v1/accounts/login/', payload)
}


export const getMe = () => {
  return api.get('/api/v1/accounts/me/')
}


export const refreshAccessToken = (refresh) => {
  return api.post('/api/v1/accounts/token/refresh/', { refresh })
}


export const logout = (refresh) => {
  return api.post('/api/v1/accounts/logout/', { refresh })
}
