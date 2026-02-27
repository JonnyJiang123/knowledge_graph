<template>
  <div class="diagnosis-assistant">
    <h2>智能诊断助手</h2>

    <el-row :gutter="20" class="mt-4">
      <el-col :span="10">
        <el-card>
          <template #header>
            <span>选择症状</span>
          </template>
          <SymptomSelector
            v-model="selectedSymptoms"
            @confirm="handleDiagnose"
          />

          <el-divider />

          <div class="patient-info">
            <el-form :model="patientInfo" label-width="80px">
              <el-form-item label="年龄">
                <el-input-number v-model="patientInfo.age" :min="0" :max="150" />
              </el-form-item>
              <el-form-item label="性别">
                <el-radio-group v-model="patientInfo.gender">
                  <el-radio label="male">男</el-radio>
                  <el-radio label="female">女</el-radio>
                </el-radio-group>
              </el-form-item>
            </el-form>
          </div>

          <el-button
            type="primary"
            :disabled="selectedSymptoms.length === 0"
            :loading="loading"
            @click="handleDiagnose"
            class="diagnose-btn"
          >
            开始诊断
          </el-button>
        </el-card>
      </el-col>

      <el-col :span="14">
        <el-card v-if="diagnosisResult">
          <template #header>
            <span>诊断结果</span>
            <el-tag v-if="diagnosisResult.confidence" type="info">
              置信度: {{ (diagnosisResult.confidence * 100).toFixed(1) }}%
            </el-tag>
          </template>
          <DiagnosisResult :result="diagnosisResult" />
        </el-card>

        <el-card v-else class="empty-result">
          <el-empty description="请选择症状并开始诊断" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import SymptomSelector from '@/components/industry/healthcare/SymptomSelector.vue'
import DiagnosisResult from '@/components/industry/healthcare/DiagnosisResult.vue'

const selectedSymptoms = ref<string[]>([])
const loading = ref(false)
const diagnosisResult = ref<any>(null)

const patientInfo = ref({
  age: undefined as number | undefined,
  gender: 'male'
})

const handleDiagnose = async () => {
  if (selectedSymptoms.value.length === 0) {
    ElMessage.warning('请至少选择一个症状')
    return
  }

  loading.value = true
  try {
    // 调用诊断API
    // const response = await diagnose({
    //   symptoms: selectedSymptoms.value,
    //   patient_age: patientInfo.value.age,
    //   patient_gender: patientInfo.value.gender
    // })
    // diagnosisResult.value = response

    // 模拟数据
    diagnosisResult.value = {
      possible_diseases: [
        {
          disease_id: 'disease-1',
          disease_name: '上呼吸道感染',
          match_score: 0.85,
          matched_symptoms: ['发热', '咳嗽'],
          description: '常见的呼吸道感染疾病',
          severity: 'LOW'
        }
      ],
      recommended_departments: ['呼吸科', '内科'],
      confidence: 0.85
    }
  } catch (error) {
    ElMessage.error('诊断失败，请重试')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.diagnosis-assistant {
  padding: 20px;
}
.mt-4 {
  margin-top: 16px;
}
.diagnose-btn {
  width: 100%;
  margin-top: 16px;
}
.empty-result {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
