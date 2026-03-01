<script setup lang="ts">
import { computed, ref } from 'vue'
import AlertCard from './AlertCard.vue'
import type { ReasoningResult, Alert, AlertLevel } from '@/types/reasoning'

const props = defineProps<{
  result: ReasoningResult | null
  loading?: boolean
}>()

const emit = defineEmits<{
  (e: 'refresh'): void
  (e: 'export'): void
  (e: 'process:alert', alert: Alert): void
  (e: 'ignore:alert', alert: Alert): void
  (e: 'click:entity', entityId: string): void
}>()

const levelFilter = ref<AlertLevel | 'all'>('all')

const filteredAlerts = computed(() => {
  if (!props.result) return []
  if (levelFilter.value === 'all') return props.result.alerts
  return props.result.alerts.filter((a) => a.level === levelFilter.value)
})

const alertCounts = computed(() => {
  const counts: Record<AlertLevel, number> = {
    LOW: 0,
    MEDIUM: 0,
    HIGH: 0,
    CRITICAL: 0,
  }
  if (props.result) {
    props.result.alerts.forEach((alert) => {
      counts[alert.level]++
    })
  }
  return counts
})

const levelOptions: { value: AlertLevel | 'all'; label: string }[] = [
  { value: 'all', label: '全部' },
  { value: 'CRITICAL', label: '严重' },
  { value: 'HIGH', label: '高' },
  { value: 'MEDIUM', label: '中' },
  { value: 'LOW', label: '低' },
]

// function getStatusTag(status: string) {
//   const tags: Record<string, string> = {
//     pending: 'info',
//     running: 'warning',
//     completed: 'success',
//     failed: 'danger',
//   }
//   return tags[status] ?? 'info'
// }

function getStatusLabel(status: string) {
  const labels: Record<string, string> = {
    pending: '等待中',
    running: '运行中',
    completed: '已完成',
    failed: '失败',
  }
  return labels[status] ?? status
}
</script>

<template>
  <div class="reasoning-results">
    <!-- 统计卡片 -->
    <el-row :gutter="16" class="statistics-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon class="stat-icon" size="32" color="#409EFF">
              <DataAnalysis />
            </el-icon>
            <div class="stat-info">
              <span class="stat-value">{{ result?.statistics.entitiesAnalyzed ?? 0 }}</span>
              <span class="stat-label">分析实体</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon class="stat-icon" size="32" color="#67C23A">
              <Share />
            </el-icon>
            <div class="stat-info">
              <span class="stat-value">{{ result?.statistics.relationsAnalyzed ?? 0 }}</span>
              <span class="stat-label">分析关系</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon class="stat-icon" size="32" color="#E6A23C">
              <Warning />
            </el-icon>
            <div class="stat-info">
              <span class="stat-value">{{ result?.statistics.alertsGenerated ?? 0 }}</span>
              <span class="stat-label">生成告警</span>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <el-icon class="stat-icon" size="32" :color="result ? '#67C23A' : '#909399'">
              <CircleCheck v-if="result?.status === 'completed'" />
              <Loading v-else-if="result?.status === 'running'" />
              <Timer v-else />
            </el-icon>
            <div class="stat-info">
              <span class="stat-value">{{ result ? getStatusLabel(result.status) : '-' }}</span>
              <span class="stat-label">任务状态</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 告警分布 -->
    <el-card v-if="result" class="alert-distribution" shadow="hover">
      <template #header>
        <span>告警分布</span>
      </template>
      <div class="distribution-bars">
        <div class="dist-item">
          <span class="dist-label">严重</span>
          <el-progress
            :percentage="Math.round((alertCounts.CRITICAL / Math.max(result.alerts.length, 1)) * 100)"
            :color="'#FF4D4F'"
            :show-text="false"
          />
          <span class="dist-count">{{ alertCounts.CRITICAL }}</span>
        </div>
        <div class="dist-item">
          <span class="dist-label">高</span>
          <el-progress
            :percentage="Math.round((alertCounts.HIGH / Math.max(result.alerts.length, 1)) * 100)"
            :color="'#F56C6C'"
            :show-text="false"
          />
          <span class="dist-count">{{ alertCounts.HIGH }}</span>
        </div>
        <div class="dist-item">
          <span class="dist-label">中</span>
          <el-progress
            :percentage="Math.round((alertCounts.MEDIUM / Math.max(result.alerts.length, 1)) * 100)"
            :color="'#E6A23C'"
            :show-text="false"
          />
          <span class="dist-count">{{ alertCounts.MEDIUM }}</span>
        </div>
        <div class="dist-item">
          <span class="dist-label">低</span>
          <el-progress
            :percentage="Math.round((alertCounts.LOW / Math.max(result.alerts.length, 1)) * 100)"
            :color="'#909399'"
            :show-text="false"
          />
          <span class="dist-count">{{ alertCounts.LOW }}</span>
        </div>
      </div>
    </el-card>

    <!-- 告警列表 -->
    <el-card class="alerts-section" shadow="hover">
      <template #header>
        <div class="alerts-header">
          <span>告警列表 ({{ filteredAlerts.length }})</span>
          <div class="alerts-actions">
            <el-select v-model="levelFilter" size="small" style="width: 100px">
              <el-option
                v-for="opt in levelOptions"
                :key="opt.value"
                :label="opt.label"
                :value="opt.value"
              />
            </el-select>
            <el-button
              size="small"
              :loading="loading"
              @click="emit('refresh')"
            >
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
            <el-button
              type="primary"
              size="small"
              @click="emit('export')"
            >
              <el-icon><Download /></el-icon>
              导出报告
            </el-button>
          </div>
        </div>
      </template>

      <div v-loading="loading" class="alerts-list">
        <template v-if="filteredAlerts.length">
          <AlertCard
            v-for="alert in filteredAlerts"
            :key="alert.id"
            :alert="alert"
            @ignore="emit('ignore:alert', $event)"
            @process="emit('process:alert', $event)"
            @click:entity="emit('click:entity', $event)"
          />
        </template>
        <el-empty v-else-if="!loading" description="暂无告警" :image-size="100" />
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.reasoning-results {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.statistics-row {
  margin-bottom: 8px;
}

.stat-card {
  margin-bottom: 16px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  flex-shrink: 0;
}

.stat-info {
  display: flex;
  flex-direction: column;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: var(--el-text-color-primary);
}

.stat-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.alert-distribution {
  margin-bottom: 8px;
}

.distribution-bars {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.dist-item {
  display: grid;
  grid-template-columns: 50px 1fr 40px;
  align-items: center;
  gap: 12px;
}

.dist-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  text-align: right;
}

.dist-count {
  font-size: 14px;
  font-weight: bold;
  color: var(--el-text-color-primary);
}

.alerts-section {
  flex: 1;
}

.alerts-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.alerts-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.alerts-list {
  max-height: 600px;
  overflow-y: auto;
}
</style>
