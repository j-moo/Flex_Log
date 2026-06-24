import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import {
  getNotifications,
  getUnreadNotificationCount,
  markAllNotificationsRead,
  markNotificationRead,
} from '../api/notifications'


export const useNotificationStore = defineStore('notifications', () => {
  const items = ref([])
  const unreadCount = ref(0)
  const isLoading = ref(false)
  const errorMessage = ref('')

  const hasUnread = computed(() => unreadCount.value > 0)

  const syncUnreadCountFromItems = () => {
    unreadCount.value = items.value.filter((item) => !item.is_read).length
  }

  const fetchNotifications = async () => {
    isLoading.value = true
    errorMessage.value = ''
    try {
      const response = await getNotifications()
      items.value = response.data
      syncUnreadCountFromItems()
      return response.data
    } catch (error) {
      errorMessage.value = '알림을 불러오지 못했습니다.'
      throw error
    } finally {
      isLoading.value = false
    }
  }

  const fetchUnreadCount = async () => {
    try {
      const response = await getUnreadNotificationCount()
      unreadCount.value = Number(response.data.unread_count || 0)
      return unreadCount.value
    } catch {
      unreadCount.value = 0
      return 0
    }
  }

  const markAsRead = async (id) => {
    const previous = items.value.find((item) => item.id === id)
    const wasUnread = previous && !previous.is_read
    const response = await markNotificationRead(id)
    items.value = items.value.map((item) => (item.id === id ? response.data : item))
    if (wasUnread) unreadCount.value = Math.max(0, unreadCount.value - 1)
    return response.data
  }

  const markAllAsRead = async () => {
    await markAllNotificationsRead()
    items.value = items.value.map((item) => ({ ...item, is_read: true }))
    unreadCount.value = 0
  }

  const clear = () => {
    items.value = []
    unreadCount.value = 0
    errorMessage.value = ''
  }

  return {
    items,
    unreadCount,
    hasUnread,
    isLoading,
    errorMessage,
    fetchNotifications,
    fetchUnreadCount,
    markAsRead,
    markAllAsRead,
    clear,
  }
})
