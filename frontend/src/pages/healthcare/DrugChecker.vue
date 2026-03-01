<template>
  <div class="drug-checker">
    <h2>药物相互作用检查</h2>

    <el-row :gutter="20" class="mt-4">
      <el-col :span="12">
        <el-card>
          <template #header>
            <span>添加药物</span>
          </template>

          <el-select
            v-model="selectedDrugs"
            multiple
            filterable
            remote
            placeholder="搜索药物..."
            :remote-method="searchDrugs"
            :loading="searching"
            style="width: 100%"
          >
            <el-option
              v-for="drug in drugOptions"
              :key="drug.id"
              :label="drug.name"
              :value="drug.id"
            />
          </el-select>

          <el-divider />

          <div class="selected-drugs">
            <h4>已选药物</h4>
            <el-tag
              v-for="drugId in selectedDrugs"
              :key="drugId"
              closable
              @close="removeDrug(drugId)"
              class="drug-tag"
            >
              {{ getDrugName(drugId) }}
            </el-tag>
            <el-empty v-if="selectedDrugs.length === 0" description="未选择药物" />
          </div>

          <el-button
            type="primary"
            :disabled="selectedDrugs.length < 2"
            :loading="checking"
            @click="checkInteractions"
            class="check-btn"
          >
            检查相互作用
          </el-button>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card v-if="interactionResult">
          <template #header>
            <span>检查结果</span>
            <el-tag :type="resultTagType">
              {{ interactionResult.summary }}
            </el-tag>
          </template>

          <el-alert
            v-if="interactionResult.has_contraindication"
            title="发现禁忌配伍"
            type="error"
            :closable="false"
            show-icon
            class="mb-4"
          />

          <div
            v-for="interaction in interactionResult.interactions"
            :key="interaction.drug_a_id + interaction.drug_b_id"
            class="interaction-item"
          >
            <el-divider />
            <h4>{{ interaction.drug_a_name }} + {{ interaction.drug_b_name }}</h4>
            <el-tag :type="getSeverityType(interaction.severity)">
              {{ interaction.severity }}
            </el-tag>
            <p>{{ interaction.description }}</p>
            <el-alert
              :title="interaction.recommendation"
              type="warning"
              :closable="false"
            />
          </div>
        </el-card>

        <el-card v-else class="empty-result">
          <el-empty description="请选择至少两种药物并检查" />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'

const selectedDrugs = ref<string[]>([])
const drugOptions = ref<any[]>([])
const searching = ref(false)
const checking = ref(false)
const interactionResult = ref<any>(null)

const resultTagType = computed(() => {
  if (!interactionResult.value) return 'info'
  if (interactionResult.value.has_contraindication) return 'danger'
  if (interactionResult.value.interactions.length > 0) return 'warning'
  return 'success'
})

const searchDrugs = async (query: string) => {
  if (query.length < 2) return
  searching.value = true
  // 模拟搜索API
  drugOptions.value = [
    { id: 'drug-1', name: '阿莫西林' },
    { id: 'drug-2', name: '布洛芬' },
    { id: 'drug-3', name: '奥美拉唑' }
  ].filter(d => d.name.includes(query))
  searching.value = false
}

const getDrugName = (id: string) => {
  const drug = drugOptions.value.find(d => d.id === id)
  return drug?.name || id
}

const removeDrug = (id: string) => {
  selectedDrugs.value = selectedDrugs.value.filter(drugId => drugId !== id)
}

const getSeverityType = (severity: string): "info" | "warning" | "danger" | "primary" | "success" | undefined => {
  const map: Record<string, "info" | "warning" | "danger" | "primary" | "success"> = {
    'HIGH': 'danger',
    'MEDIUM': 'warning',
    'LOW': 'info'
  }
  return map[severity] || 'info'
}

const checkInteractions = async () => {
  checking.value = true
  try {
    // 模拟API调用
    interactionResult.value = {
      interactions: [
        {
          drug_a_id: 'drug-1',
          drug_a_name: '阿莫西林',
          drug_b_id: 'drug-2',
          drug_b_name: '布洛芬',
          severity: 'MEDIUM',
          description: '两药合用可能增加胃肠道不适风险',
          recommendation: '建议饭后服用，监测胃肠道反应'
        }
      ],
      has_contraindication: false,
      summary: '发现1个药物相互作用'
    }
  } catch (error) {
    ElMessage.error('检查失败，请重试')
  } finally {
    checking.value = false
  }
}
</script>

<style scoped>
.drug-checker {
  padding: 20px;
}
.mt-4 {
  margin-top: 16px;
}
.selected-drugs {
  min-height: 100px;
}
.drug-tag {
  margin: 4px;
}
.check-btn {
  width: 100%;
  margin-top: 16px;
}
.empty-result {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
}
.interaction-item {
  margin-bottom: 16px;
}
.mb-4 {
  margin-bottom: 16px;
}
</style>
