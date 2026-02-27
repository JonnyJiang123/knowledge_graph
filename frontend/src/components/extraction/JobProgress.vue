<template>
  <div class="job-progress">
    <div class="progress-header">
      <span class="job-type">{{ jobType }}</span>
      <el-tag :type="statusType">{{ statusText }}</el-tag>
    </div>

    <el-progress
      :percentage="progress.percentage"
      :status="progressStatus"
      :stroke-width="16"
    />

    <div class="progress-info">
      <span>{{ progress.processed }} / {{ progress.total }}</span>
      <span v-if="progress.estimatedRemaining">
        预计剩余: {{ formatTime(progress.estimatedRemaining) }}
      </span>
    </div>

    <div class="stages">
      <div
        v-for="stage in stages"
        :key="stage.name"
        class="stage-item"
        :class="`status-${stage.status}`"
      >
        <el-icon v-if="stage.status === 'completed'"><CircleCheck /></el-icon>
        <el-icon v-else-if="stage.status === 'running'"><Loading /></el-icon>
        <el-icon v-else><MoreFilled /></el-icon>
        <span>{{ stage.name }}</span>
      </div>
    </div>

    <div v-if="error" class="error-message">
      <el-alert :title="error" type="error" show-icon />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { CircleCheck, Loading, MoreFilled } from '@element-plus/icons-vue'

const props = defineProps<{
  jobType: string
  progress: {
    percentage: number
    processed: number
    total: number
    estimatedRemaining?: number
  }
  status: string  // pending, running, completed, failed
  stages: Array<{
    name: string
    status: string  // pending, running, completed
  }>
  error?: string
}>()

const statusType = computed(() => {
  const map: Record<string, string> = {
    'pending': 'info',
    'running': 'warning',
    'completed': 'success',
    'failed': 'danger'
  }
  return map[props.status] || 'info'
})

const statusText = computed(() => {
  const map: Record<string, string> = {
    'pending': '待处理',
    'running': '运行中',
    'completed': '已完成',
    'failed': '失败'
  }
  return map[props.status] || props.status
})

const progressStatus = computed(() => {
  if (props.status === 'failed') return 'exception'
  if (props.status === 'completed') return 'success'
  return ''
})

const formatTime = (seconds: number) => {
  const mins = Math.floor(seconds / 60)
  const secs = seconds % 60
  if (mins > 0) {
    return `${mins}分${secs}秒`
  }
  return `${secs}秒`
}
</script>

<style scoped>
.job-progress {
  padding: 16px;
  background: #f5f7fa;
  border-radius: 8px;
}
.progress-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}
.job-type {
  font-weight: 600;
}
.progress-info {
  display: flex;
  justify-content: space-between;
  margin-top: 8px;
  font-size: 12px;
  color: #909399;
}
.stages {
  display: flex;
  gap: 16px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e4e7ed;
}
.stage-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
}
.stage-item.status-completed {
  color: #67c23a;
}
.stage-item.status-running {
  color: #e6a23c;
}
.stage-item.status-pending {
  color: #909399;
}
.error-message {
  margin-top: 16px;
}
</style>
