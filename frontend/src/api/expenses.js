import api from './client'


// 카테고리 목록 조회
export const getCategories = () => {
  return api.get('/api/v1/expenses/categories/')
}


// 소비 기록 목록 조회
export const getExpenses = () => {
  return api.get('/api/v1/expenses/')
}


// 소비 기록 상세 조회
export const getExpense = (id) => {
  return api.get(`/api/v1/expenses/${id}/`)
}


// 소비 기록 생성
export const createExpense = (payload) => {
  return api.post('/api/v1/expenses/', payload)
}


// 소비 기록 수정
export const updateExpense = (id, payload) => {
  return api.patch(`/api/v1/expenses/${id}/`, payload)
}


// 소비 기록 삭제
export const deleteExpense = (id) => {
  return api.delete(`/api/v1/expenses/${id}/`)
}

export const getFriendFeed = () => {
  return api.get('/api/v1/expenses/feed/')
}
export const toggleExpenseLike = (id) => {
  return api.post(`/api/v1/expenses/${id}/like/`)
}

export const createComment = (id, content) => {
  return api.post(`/api/v1/expenses/${id}/comments/`, {
    content,
  })
}

export const deleteComment = (id) => {
  return api.delete(`/api/v1/expenses/comments/${id}/`)
}