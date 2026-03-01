<template>
  <div class="risk-dashboard">
    <h2>金融风险监控仪表板</h2>

    <el-row :gutter="20" class="mt-4">
      <el-col :span="6" v-for="metric in riskMetrics" :key="metric.title">
        <RiskScoreCard
          :title="metric.title"
          :score="metric.score"
          :level="metric.level"
          :trend="metric.trend"
        />
      </el-col>
    </el-row>

    <el-row :gutter="20" class="mt-4">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>高风险企业预警</span>
          </template>
          <el-table :data="highRiskEnterprises" style="width: 100%">
            <el-table-column prop="name" label="企业名称" />
            <el-table-column prop="riskScore" label="风险评分" width="100">
              <template #default="{ row }">
                <el-tag :type="row.riskScore > 80 ? 'danger' : 'warning'">
                  {{ row.riskScore }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="riskType" label="风险类型" />
            <el-table-column label="操作" width="100">
              <template #default="{ row }">
                <el-button link type="primary" @click="viewEnterprise(row.id)">
                  查看
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card>
          <template #header>
            <span>欺诈检测告警</span>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="alert in fraudAlerts"
              :key="alert.id"
              :type="alert.severity === 'HIGH' ? 'danger' : 'warning'"
              :timestamp="alert.time"
            >
              <h4>{{ alert.title }}</h4>
              <p>{{ alert.description }}</p>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import RiskScoreCard from '@/components/industry/finance/RiskScoreCard.vue'

const router = useRouter()

const riskMetrics = ref<Array<{ title: string; score: number; level: 'LOW' | 'MEDIUM' | 'HIGH'; trend: 'up' | 'down' | undefined }>>([
  { title: '整体风险指数', score: 72, level: 'MEDIUM', trend: 'down' },
  { title: '欺诈检测率', score: 85, level: 'LOW', trend: 'up' },
  { title: '关联风险企业', score: 156, level: 'HIGH', trend: 'up' },
  { title: '待处理告警', score: 23, level: 'MEDIUM', trend: 'down' }
])

const highRiskEnterprises = ref([
  { id: '1', name: '示例企业A', riskScore: 92, riskType: '资金链断裂风险' },
  { id: '2', name: '示例企业B', riskScore: 87, riskType: '关联企业风险' }
])

const fraudAlerts = ref([
  {
    id: '1',
    title: '可疑交易聚类检测',
    description: '发现3个账户存在循环交易模式',
    severity: 'HIGH',
    time: '2026-02-27 10:00:00'
  },
  {
    id: '2',
    title: '异常金额预警',
    description: '检测到单笔交易金额超出历史平均值5倍',
    severity: 'MEDIUM',
    time: '2026-02-27 09:30:00'
  }
])

const viewEnterprise = (id: string) => {
  router.push(`/finance/enterprises/${id}`)
}

onMounted(() => {
  // 加载风险数据
})
</script>

<style scoped>
.risk-dashboard {
  padding: 20px;
}
.mt-4 {
  margin-top: 16px;
}
</style>
