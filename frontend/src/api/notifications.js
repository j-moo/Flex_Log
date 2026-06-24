import api from './client'


export const getNotifications = () => api.get('/api/v1/notifications/')

export const getUnreadNotificationCount = () => api.get('/api/v1/notifications/unread-count/')

export const markNotificationRead = (id) => api.patch(`/api/v1/notifications/${id}/read/`)

export const markAllNotificationsRead = () => api.post('/api/v1/notifications/read-all/')
