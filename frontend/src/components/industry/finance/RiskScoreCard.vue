<template>
  <el-card :body-style="{ padding: '20px' }">
    <div class="risk-score-card">
      <div class="title">{{ title }}</div>
      <div class="score" :class="scoreClass">{{ score }}</div>
      <div class="level">
        <el-tag :type="levelType" size="small">{{ levelText }}</el-tag>
      </div>
      <div v-if="trend" class="trend">
        <el-icon :class="trend">
          <ArrowUp v-if="trend === 'up'" />
          <ArrowDown v-else />
        </el-icon>
      </div>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ArrowUp, ArrowDown } from '@element-plus/icons-vue'

const props = defineProps<{
  title: string
  score: number
  level: 'LOW' | 'MEDIUM' | 'HIGH'
  trend?: 'up' | 'down'
}>()

const scoreClass = computed(() => {
  if (props.score >= 80) return 'high'
  if (props.score >= 50) return 'medium'
  return 'low'
})

const levelType = computed((): "info" | "warning" | "danger" | "primary" | "success" | undefined => {
  const map: Record<string, "info" | "warning" | "danger" | "primary" | "success"> = {
    'LOW': 'success',
    'MEDIUM': 'warning',
    'HIGH': 'danger'
  }
  return map[props.level] || 'info'
})

const levelText = computed(() => {
  const map: Record<string, string> = {
    'LOW': '低风险',
    'MEDIUM': '中风险',
    'HIGH': '高风险'
  }
  return map[props.level] || '未知'
})
</script>

<style scoped>
.risk-score-card {
  text-align: center;
}
.title {
  font-size: 14px;
  color: #909399;
  margin-bottom: 12px;
}
.score {
  font-size: 36px;
  font-weight: bold;
  margin-bottom: 12px;
}
.score.high {
  color: #f56c6c;
}
.score.medium {
  color: #e6a23c;
}
.score.low {
  color: #67c23a;
}
.level {
  margin-bottom: 8px;
}
.trend {
  font-size: 12px;
  color: #909399;
}
.trend .up {
  color: #f56c6c;
}
.trend .down {
  color: #67c23a;
}
</style>
