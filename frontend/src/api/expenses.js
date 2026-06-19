import api from './client'


export const getCategories = () => {
  return api.get('/api/v1/expenses/categories/')
}


export const getExpenses = () => {
  return api.get('/api/v1/expenses/')
}


export const getUserExpenses = (userId) => {
  return api.get(`/api/v1/expenses/users/${userId}/`)
}


export const getExpense = (id) => {
  return api.get(`/api/v1/expenses/${id}/`)
}


export const createExpense = (payload) => {
  return api.post('/api/v1/expenses/', payload)
}


export const updateExpense = (id, payload) => {
  return api.patch(`/api/v1/expenses/${id}/`, payload)
}


export const deleteExpense = (id) => {
  return api.delete(`/api/v1/expenses/${id}/`)
}


export const getFriendFeed = () => {
  return api.get('/api/v1/expenses/feed/')
}


export const toggleExpenseLike = (id) => {
  return api.post(`/api/v1/expenses/${id}/like/`)
}


export const getComments = (id) => {
  return api.get(`/api/v1/expenses/${id}/comments/`)
}


export const createComment = (id, content) => {
  return api.post(`/api/v1/expenses/${id}/comments/`, { content })
}


export const deleteComment = (logId, commentId) => {
  return api.delete(`/api/v1/expenses/${logId}/comments/${commentId}/`)
}
