import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface UserSettings {
  theme: 'light' | 'dark' | 'auto'
  language: 'zh-CN' | 'en-US'
  graphLayout: 'force' | 'hierarchical' | 'circular'
  autoSave: boolean
  notifications: {
    email: boolean
    push: boolean
    desktop: boolean
  }
}

const defaultSettings: UserSettings = {
  theme: 'auto',
  language: 'zh-CN',
  graphLayout: 'force',
  autoSave: true,
  notifications: {
    email: true,
    push: true,
    desktop: true
  }
}

export const useSettingsStore = defineStore('settings', () => {
  // State
  const settings = ref<UserSettings>({ ...defaultSettings })

  // Actions
  const updateSettings = (newSettings: Partial<UserSettings>) => {
    settings.value = { ...settings.value, ...newSettings }
    saveToLocalStorage()
  }

  const resetSettings = () => {
    settings.value = { ...defaultSettings }
    saveToLocalStorage()
  }

  const loadFromLocalStorage = () => {
    try {
      const saved = localStorage.getItem('kg-settings')
      if (saved) {
        settings.value = { ...defaultSettings, ...JSON.parse(saved) }
      }
    } catch {
      // 忽略解析错误
    }
  }

  const saveToLocalStorage = () => {
    try {
      localStorage.setItem('kg-settings', JSON.stringify(settings.value))
    } catch {
      // 忽略保存错误
    }
  }

  // 初始化时加载
  loadFromLocalStorage()

  return {
    settings,
    updateSettings,
    resetSettings,
    loadFromLocalStorage
  }
})
