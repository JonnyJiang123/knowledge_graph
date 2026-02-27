import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export interface Notification {
  id: string
  type: 'success' | 'warning' | 'error' | 'info'
  title: string
  message: string
  read: boolean
  createdAt: Date
}

export const useNotificationStore = defineStore('notification', () => {
  // State
  const notifications = ref<Notification[]>([])
  const unreadCount = computed(() => notifications.value.filter(n => !n.read).length)

  // Actions
  const addNotification = (notification: Omit<Notification, 'id' | 'read' | 'createdAt'>) => {
    const newNotification: Notification = {
      ...notification,
      id: `notif-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      read: false,
      createdAt: new Date()
    }
    notifications.value.unshift(newNotification)

    // 最多保留50条通知
    if (notifications.value.length > 50) {
      notifications.value = notifications.value.slice(0, 50)
    }

    return newNotification.id
  }

  const markAsRead = (id: string) => {
    const notification = notifications.value.find(n => n.id === id)
    if (notification) {
      notification.read = true
    }
  }

  const markAllAsRead = () => {
    notifications.value.forEach(n => n.read = true)
  }

  const removeNotification = (id: string) => {
    const index = notifications.value.findIndex(n => n.id === id)
    if (index > -1) {
      notifications.value.splice(index, 1)
    }
  }

  const clearAll = () => {
    notifications.value = []
  }

  // 快捷方法
  const success = (title: string, message: string) => {
    return addNotification({ type: 'success', title, message })
  }

  const warning = (title: string, message: string) => {
    return addNotification({ type: 'warning', title, message })
  }

  const error = (title: string, message: string) => {
    return addNotification({ type: 'error', title, message })
  }

  const info = (title: string, message: string) => {
    return addNotification({ type: 'info', title, message })
  }

  return {
    notifications,
    unreadCount,
    addNotification,
    markAsRead,
    markAllAsRead,
    removeNotification,
    clearAll,
    success,
    warning,
    error,
    info
  }
})
