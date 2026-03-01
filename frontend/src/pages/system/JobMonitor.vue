<template>
  <div class="job-monitor">
    <h2>任务监控</h2>

    <el-row :gutter="20" class="mt-4">
      <el-col :span="6" v-for="stat in jobStats" :key="stat.label">
        <el-statistic :title="stat.label" :value="stat.value">
          <template #suffix>
            <el-tag :type="stat.type" size="small">{{ stat.change }}</el-tag>
          </template>
        </el-statistic>
      </el-col>
    </el-row>

    <el-card class="mt-4">
      <template #header>
        <div class="card-header">
          <span>运行中的任务</span>
          <el-button type="primary" size="small" @click="refreshJobs">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <el-table :data="jobs" v-loading="loading">
        <el-table-column prop="job_id" label="任务ID" width="200" />
        <el-table-column prop="type" label="类型" width="120" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusType(row.status)">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="progress" label="进度" width="200">
          <template #default="{ row }">
            <el-progress
              :percentage="row.progress?.percentage || 0"
              :status="row.status === 'failed' ? 'exception' : ''"
            />
          </template>
        </el-table-column>
        <el-table-column prop="created_at" label="创建时间" width="180" />
        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <el-button link type="primary" @click="viewDetail(row)">详情</el-button>
            <el-button
              v-if="row.status === 'running'"
              link
              type="danger"
              @click="cancelJob(row.job_id)"
            >
              取消
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Refresh } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const loading = ref(false)
const jobs = ref<any[]>([])

const jobStats = ref([
  { label: '运行中', value: 3, change: '+1', type: 'success' as const },
  { label: '待处理', value: 5, change: '-2', type: 'warning' as const },
  { label: '今日完成', value: 45, change: '+12', type: 'success' as const },
  { label: '今日失败', value: 2, change: '+1', type: 'danger' as const }
])

const getStatusType = (status: string): "info" | "warning" | "danger" | "primary" | "success" | undefined => {
  const map: Record<string, "info" | "warning" | "danger" | "primary" | "success"> = {
    'pending': 'info',
    'running': 'warning',
    'completed': 'success',
    'failed': 'danger'
  }
  return map[status] || 'info'
}

const refreshJobs = async () => {
  loading.value = true
  try {
    // 模拟API调用
    jobs.value = [
      {
        job_id: 'job-1',
        type: 'extraction',
        status: 'running',
        progress: { percentage: 45 },
        created_at: '2026-02-27 10:00:00'
      },
      {
        job_id: 'job-2',
        type: 'ingestion',
        status: 'pending',
        progress: { percentage: 0 },
        created_at: '2026-02-27 10:05:00'
      }
    ]
  } finally {
    loading.value = false
  }
}

const viewDetail = (job: any) => {
  // 显示任务详情
  ElMessage.info(`查看任务详情: ${job.job_id}`)
}

const cancelJob = (jobId: string) => {
  ElMessage.warning(`取消任务: ${jobId}`)
}

onMounted(() => {
  refreshJobs()
})
</script>

<style scoped>
.job-monitor {
  padding: 20px;
}
.mt-4 {
  margin-top: 16px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
