<template>
  <div class="diagnosis-result">
    <div v-if="result.possible_diseases?.length > 0" class="diseases-list">
      <div
        v-for="(disease, index) in result.possible_diseases"
        :key="disease.disease_id"
        class="disease-card"
      >
        <div class="disease-header">
          <span class="rank">{{ index + 1 }}</span>
          <h4 class="disease-name">{{ disease.disease_name }}</h4>
          <el-tag :type="getSeverityType(disease.severity)">
            {{ disease.severity }}
          </el-tag>
        </div>

        <el-progress
          :percentage="Math.round(disease.match_score * 100)"
          :status="getProgressStatus(disease.match_score)"
          class="match-progress"
        />

        <p class="description">{{ disease.description }}</p>

        <div class="matched-symptoms">
          <el-tag
            v-for="symptom in disease.matched_symptoms"
            :key="symptom"
            size="small"
            type="success"
            effect="plain"
            class="symptom-tag"
          >
            {{ symptom }}
          </el-tag>
        </div>
      </div>
    </div>

    <el-divider />

    <div class="recommendations">
      <h4>推荐科室</h4>
      <el-tag
        v-for="dept in result.recommended_departments"
        :key="dept"
        type="primary"
        class="dept-tag"
      >
        {{ dept }}
      </el-tag>
    </div>

    <el-alert
      title="免责声明"
      type="warning"
      :closable="false"
      show-icon
      class="disclaimer"
    >
      本诊断结果仅供参考，不能替代专业医生的诊断。如有不适，请及时就医。
    </el-alert>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  result: {
    possible_diseases: Array<{
      disease_id: string
      disease_name: string
      match_score: number
      matched_symptoms: string[]
      description: string
      severity: string
    }>
    recommended_departments: string[]
    confidence: number
  }
}>()

const getSeverityType = (severity: string): "info" | "warning" | "danger" | "primary" | "success" | undefined => {
  const map: Record<string, "info" | "warning" | "danger" | "primary" | "success"> = {
    'HIGH': 'danger',
    'MEDIUM': 'warning',
    'LOW': 'success'
  }
  return map[severity] || 'info'
}

const getProgressStatus = (score: number) => {
  if (score >= 0.8) return 'success'
  if (score >= 0.6) return ''
  return 'warning'
}
</script>

<style scoped>
.diagnosis-result {
  padding: 8px;
}
.disease-card {
  padding: 16px;
  margin-bottom: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background-color: #f5f7fa;
}
.disease-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}
.rank {
  width: 28px;
  height: 28px;
  line-height: 28px;
  text-align: center;
  background-color: #409eff;
  color: white;
  border-radius: 50%;
  font-weight: bold;
}
.disease-name {
  flex: 1;
  margin: 0;
}
.match-progress {
  margin-bottom: 12px;
}
.description {
  color: #606266;
  margin-bottom: 12px;
}
.matched-symptoms {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.symptom-tag {
  margin: 2px;
}
.recommendations {
  margin-top: 16px;
}
.dept-tag {
  margin: 4px;
}
.disclaimer {
  margin-top: 24px;
}
</style>
