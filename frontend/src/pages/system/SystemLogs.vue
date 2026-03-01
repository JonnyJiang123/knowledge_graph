<template>
  <div class="system-logs">
    <h2>系统日志</h2>

    <el-card class="mt-4">
      <template #header>
        <div class="filter-bar">
          <el-select v-model="filter.level" placeholder="日志级别" clearable>
            <el-option label="DEBUG" value="DEBUG" />
            <el-option label="INFO" value="INFO" />
            <el-option label="WARNING" value="WARNING" />
            <el-option label="ERROR" value="ERROR" />
            <el-option label="CRITICAL" value="CRITICAL" />
          </el-select>

          <el-select v-model="filter.service" placeholder="服务" clearable>
            <el-option label="API" value="api" />
            <el-option label="摄取" value="ingestion" />
            <el-option label="抽取" value="extraction" />
            <el-option label="查询" value="query" />
          </el-select>

          <el-date-picker
            v-model="filter.dateRange"
            type="datetimerange"
            range-separator="至"
            start-placeholder="开始时间"
            end-placeholder="结束时间"
          />

          <el-button type="primary" @click="searchLogs">搜索</el-button>
          <el-button @click="exportLogs">导出</el-button>
        </div>
      </template>

      <el-table :data="logs" v-loading="loading" height="500">
        <el-table-column prop="timestamp" label="时间" width="180" />
        <el-table-column prop="level" label="级别" width="100">
          <template #default="{ row }">
            <el-tag :type="getLevelType(row.level)" size="small">
              {{ row.level }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="service" label="服务" width="120" />
        <el-table-column prop="message" label="消息" show-overflow-tooltip />
        <el-table-column prop="request_id" label="请求ID" width="150" />
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.pageSize"
        :total="pagination.total"
        layout="total, sizes, prev, pager, next"
        @change="fetchLogs"
        class="mt-4"
      />
    </el-card>

    <el-row :gutter="20" class="mt-4">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>日志统计</span>
          </template>
          <div ref="chartRef" class="chart"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>服务分布</span>
          </template>
          <el-descriptions :column="1" border>
            <el-descriptions-item
              v-for="(count, service) in stats.byService"
              :key="service"
              :label="service"
            >
              {{ count }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import * as echarts from 'echarts'

const loading = ref(false)
const logs = ref<any[]>([])
const chartRef = ref<HTMLDivElement>()

const filter = ref({
  level: '',
  service: '',
  dateRange: []
})

const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
})

const stats = ref({
  byLevel: { DEBUG: 500, INFO: 800, WARNING: 150, ERROR: 45, CRITICAL: 5 },
  byService: { api: 600, ingestion: 400, extraction: 300, query: 200 }
})

const getLevelType = (level: string): "info" | "warning" | "danger" | "primary" | "success" | undefined => {
  const map: Record<string, "info" | "warning" | "danger" | "primary" | "success"> = {
    'DEBUG': 'info',
    'INFO': 'success',
    'WARNING': 'warning',
    'ERROR': 'danger',
    'CRITICAL': 'danger'
  }
  return map[level] || 'info'
}

const fetchLogs = async () => {
  loading.value = true
  try {
    // 模拟API调用
    logs.value = [
      {
        timestamp: '2026-02-27 10:00:00',
        level: 'INFO',
        service: 'api',
        message: '系统启动成功',
        request_id: 'req-001'
      },
      {
        timestamp: '2026-02-27 10:05:00',
        level: 'WARNING',
        service: 'ingestion',
        message: '数据摄取任务耗时较长',
        request_id: 'req-002'
      }
    ]
    pagination.value.total = 100
  } finally {
    loading.value = false
  }
}

const searchLogs = () => {
  pagination.value.page = 1
  fetchLogs()
}

const exportLogs = () => {
  // 导出日志
}

const initChart = () => {
  if (!chartRef.value) return

  const chart = echarts.init(chartRef.value)
  const option = {
    xAxis: {
      type: 'category',
      data: ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    },
    yAxis: { type: 'value' },
    series: [{
      data: [500, 800, 150, 45, 5],
      type: 'bar',
      itemStyle: {
        color: (params: any) => {
          const colors = ['#909399', '#67c23a', '#e6a23c', '#f56c6c', '#f56c6c']
          return colors[params.dataIndex]
        }
      }
    }]
  }
  chart.setOption(option)
}

onMounted(() => {
  fetchLogs()
  initChart()
})
</script>

<style scoped>
.system-logs {
  padding: 20px;
}
.mt-4 {
  margin-top: 16px;
}
.filter-bar {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
.chart {
  height: 300px;
}
</style>
