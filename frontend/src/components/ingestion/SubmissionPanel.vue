<script setup lang="ts">
import { computed } from 'vue'
import type { DataSourceType, JobStatus, ProcessingMode } from '@/types/ingestion'
import { Upload, Connection, Check } from '@element-plus/icons-vue'

const props = defineProps<{
  sourceType: DataSourceType
  fileName?: string
  mysqlSourceName?: string
  rulesCount: number
  loading?: boolean
  submittedJobId?: string | null
  jobStatus?: JobStatus
  jobMode?: ProcessingMode
}>()

const emit = defineEmits<{
  submit: []
  viewJobs: []
}>()

const summaryItems = computed(() => {
  const items: Array<{ label: string; value: string }> = []

  if (props.sourceType === 'FILE') {
    items.push({ label: '数据源类型', value: '文件上传' })
    if (props.fileName) {
      items.push({ label: '文件名', value: props.fileName })
    }
  } else {
    items.push({ label: '数据源类型', value: 'MySQL 数据库' })
    if (props.mysqlSourceName) {
      items.push({ label: '数据源名称', value: props.mysqlSourceName })
    }
  }

  items.push({ label: '清洗规则数量', value: `${props.rulesCount} 条` })

  return items
})

const isSubmitted = computed(() => !!props.submittedJobId)

const statusTag = computed(() => {
  switch (props.jobStatus) {
    case 'PENDING':
      return { type: 'info' as const, text: '等待中' }
    case 'RUNNING':
      return { type: 'warning' as const, text: '处理中' }
    case 'COMPLETED':
      return { type: 'success' as const, text: '已完成' }
    case 'FAILED':
      return { type: 'danger' as const, text: '失败' }
    default:
      return null
  }
})

function handleSubmit() {
  emit('submit')
}

function handleViewJobs() {
  emit('viewJobs')
}
</script>

<template>
  <div class="submission-panel">
    <el-card shadow="never">
      <template #header>
        <div class="panel-header">
          <el-icon v-if="sourceType === 'FILE'"><Upload /></el-icon>
          <el-icon v-else><Connection /></el-icon>
          <span>提交确认</span>
        </div>
      </template>

      <!-- 摘要信息 -->
      <el-descriptions :column="1" border size="small">
        <el-descriptions-item
          v-for="item in summaryItems"
          :key="item.label"
          :label="item.label"
        >
          {{ item.value }}
        </el-descriptions-item>
      </el-descriptions>

      <!-- 提交按钮 -->
      <div class="actions">
        <template v-if="!isSubmitted">
          <el-button
            type="primary"
            size="large"
            :loading="loading"
            @click="handleSubmit"
          >
            <el-icon><Check /></el-icon>
            确认提交
          </el-button>
        </template>

        <template v-else>
          <el-result
            :icon="jobStatus === 'COMPLETED' ? 'success' : jobStatus === 'FAILED' ? 'error' : 'info'"
            :title="jobStatus === 'COMPLETED' ? '处理完成' : jobStatus === 'FAILED' ? '处理失败' : '已提交'"
          >
            <template #sub-title>
              <div class="job-info">
                <p>任务 ID: {{ submittedJobId }}</p>
                <p v-if="jobMode">
                  处理模式:
                  <el-tag size="small" :type="jobMode === 'SYNC' ? 'success' : 'warning'">
                    {{ jobMode === 'SYNC' ? '同步' : '异步' }}
                  </el-tag>
                </p>
                <p v-if="statusTag">
                  状态: <el-tag size="small" :type="statusTag.type">{{ statusTag.text }}</el-tag>
                </p>
              </div>
            </template>
            <template #extra>
              <el-button type="primary" @click="handleViewJobs">
                查看任务列表
              </el-button>
            </template>
          </el-result>
        </template>
      </div>
    </el-card>
  </div>
</template>

<style scoped lang="scss">
.submission-panel {
  .panel-header {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 600;
  }

  .actions {
    margin-top: 24px;
    text-align: center;
  }

  .job-info {
    p {
      margin: 8px 0;
    }
  }
}
</style>
