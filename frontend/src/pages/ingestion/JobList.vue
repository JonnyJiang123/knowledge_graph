<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useIngestionStore } from '@/stores/ingestion'
import { useProjectStore } from '@/stores/project'
import type { IngestionJob } from '@/types/ingestion'
import JobProgress from '@/components/ingestion/JobProgress.vue'
import { Refresh, Plus, View, Clock } from '@element-plus/icons-vue'

const route = useRoute()
const router = useRouter()
const ingestionStore = useIngestionStore()
const projectStore = useProjectStore()

// 项目 ID
const projectId = computed(() => {
  return (route.query.projectId as string) || projectStore.currentProject?.id || ''
})

// 轮询相关
const pollInterval = ref<number | null>(null)
const POLL_DELAY = 3000 // 3秒轮询

// 初始化加载
onMounted(async () => {
  if (projectId.value) {
    await loadJobs()
    startPolling()
  }
})

// 清理
onUnmounted(() => {
  stopPolling()
})

// 监听项目变化
watch(projectId, async (newId) => {
  if (newId) {
    await loadJobs()
    startPolling()
  } else {
    stopPolling()
  }
})

// 加载任务列表
async function loadJobs() {
  if (!projectId.value) return
  await ingestionStore.fetchJobs(projectId.value)
}

// 启动轮询（仅当有运行中的任务时）
function startPolling() {
  stopPolling()

  const hasRunningJobs = ingestionStore.jobs.some(
    (job) => job.status === 'PENDING' || job.status === 'RUNNING',
  )

  if (hasRunningJobs) {
    pollInterval.value = window.setInterval(async () => {
      // 刷新运行中的任务
      const runningJobs = ingestionStore.jobs.filter(
        (job) => job.status === 'PENDING' || job.status === 'RUNNING',
      )

      await Promise.all(
        runningJobs.map((job) => ingestionStore.refreshJob(job.id)),
      )

      // 检查是否还有运行中的任务
      const stillRunning = ingestionStore.jobs.some(
        (job) => job.status === 'PENDING' || job.status === 'RUNNING',
      )

      if (!stillRunning) {
        stopPolling()
      }
    }, POLL_DELAY)
  }
}

// 停止轮询
function stopPolling() {
  if (pollInterval.value) {
    clearInterval(pollInterval.value)
    pollInterval.value = null
  }
}

// 手动刷新
async function handleRefresh() {
  await loadJobs()
  startPolling()
}

// 跳转到向导
function goToWizard() {
  router.push({ path: '/ingestion/wizard', query: { projectId: projectId.value } })
}

// 格式化时间
function formatTime(dateStr?: string) {
  if (!dateStr) return '-'
  return new Date(dateStr).toLocaleString('zh-CN')
}

// 状态标签配置
function getStatusTag(status: IngestionJob['status']) {
  switch (status) {
    case 'PENDING':
      return { type: 'info' as const, text: '等待中' }
    case 'RUNNING':
      return { type: 'warning' as const, text: '处理中' }
    case 'COMPLETED':
      return { type: 'success' as const, text: '已完成' }
    case 'FAILED':
      return { type: 'danger' as const, text: '失败' }
    default:
      return { type: 'info' as const, text: '未知' }
  }
}

// 是否正在轮询
const isPolling = computed(() => pollInterval.value !== null)
</script>

<template>
  <div class="job-list-page">
    <el-page-header @back="router.back()">
      <template #content>
        <span class="page-title">导入任务列表</span>
      </template>
      <template #extra>
        <el-space>
          <el-tag v-if="isPolling" type="info" effect="plain">
            <el-icon class="spinning"><Clock /></el-icon>
            自动刷新中
          </el-tag>
          <el-button :icon="Refresh" @click="handleRefresh" :loading="ingestionStore.loading.jobs">
            刷新
          </el-button>
          <el-button type="primary" :icon="Plus" @click="goToWizard">
            新建导入
          </el-button>
        </el-space>
      </template>
    </el-page-header>

    <el-card class="jobs-card">
      <template v-if="ingestionStore.loading.jobs && ingestionStore.jobs.length === 0">
        <el-skeleton :rows="5" animated />
      </template>

      <template v-else-if="ingestionStore.jobs.length === 0">
        <el-empty description="暂无导入任务">
          <el-button type="primary" @click="goToWizard">创建第一个导入任务</el-button>
        </el-empty>
      </template>

      <template v-else>
        <el-table :data="ingestionStore.jobs" stripe style="width: 100%">
          <el-table-column prop="id" label="任务 ID" width="200" show-overflow-tooltip>
            <template #default="{ row }">
              <el-text type="info" size="small">{{ row.id }}</el-text>
            </template>
          </el-table-column>

          <el-table-column prop="mode" label="模式" width="100">
            <template #default="{ row }">
              <el-tag size="small" :type="row.mode === 'SYNC' ? 'success' : 'warning'">
                {{ row.mode === 'SYNC' ? '同步' : '异步' }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag size="small" :type="getStatusTag(row.status).type">
                {{ getStatusTag(row.status).text }}
              </el-tag>
            </template>
          </el-table-column>

          <el-table-column label="进度" width="200">
            <template #default="{ row }">
              <JobProgress :job="row" />
            </template>
          </el-table-column>

          <el-table-column prop="totalRows" label="行数" width="120">
            <template #default="{ row }">
              <template v-if="row.processedRows !== undefined && row.totalRows">
                {{ row.processedRows }} / {{ row.totalRows }}
              </template>
              <template v-else-if="row.totalRows">
                {{ row.totalRows }}
              </template>
              <template v-else>-</template>
            </template>
          </el-table-column>

          <el-table-column prop="createdAt" label="创建时间" width="180">
            <template #default="{ row }">
              {{ formatTime(row.createdAt) }}
            </template>
          </el-table-column>

          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ row }">
              <el-button
                v-if="row.resultPath"
                type="primary"
                :icon="View"
                size="small"
                link
              >
                查看结果
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </template>
    </el-card>
  </div>
</template>

<style scoped lang="scss">
.job-list-page {
  padding: 20px;

  .page-title {
    font-size: 18px;
    font-weight: 600;
  }

  .jobs-card {
    margin-top: 20px;
  }

  .spinning {
    animation: spin 1s linear infinite;
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
