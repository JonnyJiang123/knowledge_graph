<template>
  <div class="enterprise-analysis">
    <el-page-header title="企业关联分析" @back="goBack" />

    <el-row :gutter="20" class="mt-4">
      <el-col :span="16">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>关联图谱</span>
              <el-radio-group v-model="depth" size="small" @change="loadAssociations">
                <el-radio-button :label="1">1度</el-radio-button>
                <el-radio-button :label="2">2度</el-radio-button>
                <el-radio-button :label="3">3度</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <AssociationGraph
            :enterprise-id="enterpriseId"
            :depth="depth"
            :data="associationData"
            @node-click="handleNodeClick"
          />
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card>
          <template #header>
            <span>企业信息</span>
          </template>
          <div v-if="enterpriseInfo" class="enterprise-info">
            <h3>{{ enterpriseInfo.name }}</h3>
            <el-descriptions :column="1" border>
              <el-descriptions-item label="企业类型">
                {{ enterpriseInfo.type }}
              </el-descriptions-item>
              <el-descriptions-item label="注册资本">
                {{ enterpriseInfo.registeredCapital }}
              </el-descriptions-item>
              <el-descriptions-item label="成立日期">
                {{ enterpriseInfo.establishDate }}
              </el-descriptions-item>
              <el-descriptions-item label="风险等级">
                <el-tag :type="getRiskType(enterpriseInfo.riskLevel)">
                  {{ enterpriseInfo.riskLevel }}
                </el-tag>
              </el-descriptions-item>
            </el-descriptions>
          </div>
        </el-card>

        <el-card class="mt-4">
          <template #header>
            <span>关联统计</span>
          </template>
          <el-statistic
            v-for="stat in associationStats"
            :key="stat.label"
            :title="stat.label"
            :value="stat.value"
            class="mt-2"
          />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import AssociationGraph from '@/components/industry/finance/AssociationGraph.vue'

const route = useRoute()
const router = useRouter()

const enterpriseId = ref(route.params.id as string)
const depth = ref(2)
const enterpriseInfo = ref<any>(null)
const associationData = ref({ nodes: [], edges: [] })
const associationStats = ref([
  { label: '关联企业数', value: 0 },
  { label: '投资关系', value: 0 },
  { label: '担保关系', value: 0 }
])

const loadAssociations = async () => {
  // 调用API加载关联数据
  // const response = await fetchEnterpriseAssociations(enterpriseId.value, depth.value)
  // associationData.value = response
}

const handleNodeClick = (node: any) => {
  router.push(`/finance/enterprises/${node.id}`)
}

const getRiskType = (level: string): "info" | "warning" | "danger" | "primary" | "success" | undefined => {
  const map: Record<string, "info" | "warning" | "danger" | "primary" | "success"> = {
    'LOW': 'success',
    'MEDIUM': 'warning',
    'HIGH': 'danger'
  }
  return map[level] || 'info'
}

const goBack = () => {
  router.back()
}

onMounted(() => {
  loadAssociations()
})
</script>

<style scoped>
.enterprise-analysis {
  padding: 20px;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.mt-4 {
  margin-top: 16px;
}
</style>
