<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import ReasoningResults from '@/components/reasoning/ReasoningResults.vue'
import { useReasoningStore } from '@/stores/reasoning'
import type { Alert } from '@/types/reasoning'

const route = useRoute()
const router = useRouter()
const reasoningStore = useReasoningStore()

const jobId = computed(() => route.params.jobId as string)
const ruleId = computed(() => {
  return reasoningStore.currentJob?.ruleId
})

onMounted(async () => {
  if (jobId.value) {
    try {
      await reasoningStore.loadResults(jobId.value)
    } catch (error) {
      ElMessage.error('加载推理结果失败')
    }
  }
})

async function handleRefresh() {
  if (!jobId.value) return
  try {
    await reasoningStore.loadResults(jobId.value)
    ElMessage.success('已刷新')
  } catch (error) {
    ElMessage.error('刷新失败')
  }
}

function handleExport() {
  if (!reasoningStore.currentResults) return

  const results = reasoningStore.currentResults
  const report = {
    jobId: results.jobId,
    status: results.status,
    statistics: results.statistics,
    alerts: results.alerts,
    generatedAt: new Date().toISOString(),
  }

  const blob = new Blob([JSON.stringify(report, null, 2)], {
    type: 'application/json',
  })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = `reasoning-report-${results.jobId}.json`
  link.click()
  URL.revokeObjectURL(url)

  ElMessage.success('报告已导出')
}

async function handleReRun() {
  if (!ruleId.value) {
    ElMessage.warning('无法获取规则信息')
    return
  }

  try {
    await ElMessageBox.confirm(
      '确定要重新运行推理吗？',
      '确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'info',
      }
    )

    const job = await reasoningStore.runReasoning(ruleId.value)
    ElMessage.success('新的推理任务已启动')
    router.replace(`/reasoning/results/${job.jobId}`)
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('启动推理失败')
    }
  }
}

function handleProcessAlert(alert: Alert) {
  ElMessage.success(`处理告警: ${alert.id.slice(0, 8)}...`)
}

function handleIgnoreAlert(alert: Alert) {
  ElMessage.info(`已忽略告警: ${alert.id.slice(0, 8)}...`)
}

function handleClickEntity(entityId: string) {
  router.push(`/graph/query?entity=${entityId}`)
}
</script>

<template>
  <div class="reasoning-results-page">
    <el-card>
      <template #header>
        <div class="results-header">
          <div>
            <h2>推理结果</h2>
            <p class="hint">
              任务ID: {{ jobId }}
              <el-tag
                v-if="reasoningStore.currentResults"
                :type="reasoningStore.currentResults.status === 'completed' ? 'success' : 'info'"
                size="small"
                class="status-tag"
              >
                {{ reasoningStore.currentResults.status }}
              </el-tag>
            </p>
          </div>
          <div class="header-actions">
            <el-button type="primary" :loading="reasoningStore.loading.run" @click="handleReRun">
              <el-icon><RefreshRight /></el-icon>
              重新运行
            </el-button>
            <el-button @click="$router.push('/reasoning/rules')">
              返回规则列表
            </el-button>
          </div>
        </div>
      </template>

      <ReasoningResults
        :result="reasoningStore.currentResults"
        :loading="reasoningStore.loading.results"
        @refresh="handleRefresh"
        @export="handleExport"
        @process:alert="handleProcessAlert"
        @ignore:alert="handleIgnoreAlert"
        @click:entity="handleClickEntity"
      />
    </el-card>
  </div>
</template>

<style scoped>
.reasoning-results-page {
  padding: 24px;
}

.results-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.hint {
  color: var(--el-text-color-secondary);
  margin: 4px 0 0 0;
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-tag {
  text-transform: uppercase;
}

.header-actions {
  display: flex;
  gap: 12px;
}
</style>
