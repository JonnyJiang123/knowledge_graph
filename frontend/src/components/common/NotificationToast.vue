<template>
  <div class="notification-toast">
    <transition-group name="notification">
      <div
        v-for="notification in recentNotifications"
        :key="notification.id"
        class="notification-item"
        :class="`type-${notification.type}`"
        @click="handleClick(notification)"
      >
        <el-icon class="icon">
          <CircleCheck v-if="notification.type === 'success'" />
          <Warning v-else-if="notification.type === 'warning'" />
          <CircleClose v-else-if="notification.type === 'error'" />
          <InfoFilled v-else />
        </el-icon>
        <div class="content">
          <div class="title">{{ notification.title }}</div>
          <div class="message">{{ notification.message }}</div>
        </div>
        <el-icon class="close" @click.stop="closeNotification(notification.id)">
          <Close />
        </el-icon>
      </div>
    </transition-group>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { CircleCheck, Warning, CircleClose, InfoFilled, Close } from '@element-plus/icons-vue'
import { useNotificationStore } from '@/stores/notification'

const notificationStore = useNotificationStore()

const recentNotifications = computed(() => {
  return notificationStore.notifications.slice(0, 5)
})

const handleClick = (notification: any) => {
  notificationStore.markAsRead(notification.id)
}

const closeNotification = (id: string) => {
  notificationStore.removeNotification(id)
}
</script>

<style scoped>
.notification-toast {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  min-width: 300px;
  max-width: 400px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  cursor: pointer;
  transition: all 0.3s;
}

.notification-item:hover {
  transform: translateX(-4px);
}

.notification-item.type-success {
  border-left: 4px solid #67c23a;
}

.notification-item.type-warning {
  border-left: 4px solid #e6a23c;
}

.notification-item.type-error {
  border-left: 4px solid #f56c6c;
}

.notification-item.type-info {
  border-left: 4px solid #909399;
}

.icon {
  font-size: 20px;
}

.type-success .icon {
  color: #67c23a;
}

.type-warning .icon {
  color: #e6a23c;
}

.type-error .icon {
  color: #f56c6c;
}

.type-info .icon {
  color: #909399;
}

.content {
  flex: 1;
}

.title {
  font-weight: 600;
  margin-bottom: 4px;
}

.message {
  font-size: 13px;
  color: #606266;
}

.close {
  cursor: pointer;
  color: #909399;
  transition: color 0.2s;
}

.close:hover {
  color: #606266;
}

/* 动画 */
.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(100%);
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>
