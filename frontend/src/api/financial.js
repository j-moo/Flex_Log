import api from './client'


export const getSubscriptions = () => api.get('/api/v1/finance/subscriptions/')
export const joinProduct = (optionId) => api.post('/api/v1/finance/subscriptions/', { option_id: optionId })
export const cancelProduct = (subscriptionId) => api.post(`/api/v1/finance/subscriptions/${subscriptionId}/cancel/`)

export const getCommodityPrices = (code, params = {}) =>
  api.get(`/api/v1/finance/commodities/${code}/prices/`, { params })

export const searchYoutube = (query) =>
  api.get('/api/v1/finance/youtube/search/', { params: { q: query } })

export const getYoutubeVideo = (videoId) =>
  api.get(`/api/v1/finance/youtube/videos/${videoId}/`)

export const searchNearbyBanks = (query, radius = 2000) =>
  api.get('/api/v1/finance/banks/nearby/', { params: { query, radius } })
