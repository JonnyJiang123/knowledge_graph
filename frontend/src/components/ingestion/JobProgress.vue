<script setup lang="ts">
import { computed } from 'vue'
import type { IngestionJob } from '@/types/ingestion'
import { Check, Close, Loading, Clock } from '@element-plus/icons-vue'

const props = defineProps<{
  job: IngestionJob
}>()

const statusConfig = computed(() => {
  switch (props.job.status) {
    case 'PENDING':
      return {
        type: 'info' as const,
        icon: Clock,
        text: '等待中',
        progressStatus: undefined,
      }
    case 'RUNNING':
      return {
        type: 'warning' as const,
        icon: Loading,
        text: '处理中',
        progressStatus: undefined,
      }
    case 'COMPLETED':
      return {
        type: 'success' as const,
        icon: Check,
        text: '已完成',
        progressStatus: 'success' as const,
      }
    case 'FAILED':
      return {
        type: 'danger' as const,
        icon: Close,
        text: '失败',
        progressStatus: 'exception' as const,
      }
    default:
      return {
        type: 'info' as const,
        icon: Clock,
        text: '未知',
        progressStatus: undefined,
      }
  }
})

const progressPercent = computed(() => {
  if (props.job.status === 'COMPLETED') return 100
  if (props.job.status === 'FAILED') return props.job.progress || 0
  return props.job.progress || 0
})

const modeLabel = computed(() =>
  props.job.mode === 'SYNC' ? '同步' : '异步',
)

const rowsInfo = computed(() => {
  if (props.job.totalRows && props.job.processedRows !== undefined) {
    return `${props.job.processedRows} / ${props.job.totalRows}`
  }
  if (props.job.totalRows) {
    return `共 ${props.job.totalRows} 行`
  }
  return null
})
</script>

<template>
  <div class="job-progress">
    <div class="job-header">
      <el-tag :type="statusConfig.type" size="small">
        <el-icon class="status-icon" :class="{ spinning: job.status === 'RUNNING' }">
          <component :is="statusConfig.icon" />
        </el-icon>
        {{ statusConfig.text }}
      </el-tag>
      <el-tag type="info" size="small" effect="plain">
        {{ modeLabel }}
      </el-tag>
    </div>

    <el-progress
      :percentage="progressPercent"
      :status="statusConfig.progressStatus"
      :stroke-width="10"
    />

    <div v-if="rowsInfo" class="rows-info">
      <el-text type="info" size="small">行数: {{ rowsInfo }}</el-text>
    </div>

    <div v-if="job.errorMessage" class="error-message">
      <el-alert
        type="error"
        :title="job.errorMessage"
        :closable="false"
        show-icon
      />
    </div>
  </div>
</template>

<style scoped lang="scss">
.job-progress {
  .job-header {
    display: flex;
    gap: 8px;
    margin-bottom: 12px;
  }

  .status-icon {
    margin-right: 4px;

    &.spinning {
      animation: spin 1s linear infinite;
    }
  }

  .rows-info {
    margin-top: 8px;
  }

  .error-message {
    margin-top: 12px;
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}
</style>
