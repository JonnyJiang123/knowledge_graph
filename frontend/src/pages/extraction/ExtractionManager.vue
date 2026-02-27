<template>
  <div class="extraction-manager">
    <h2>知识抽取管理</h2>

    <el-row :gutter="20" class="mt-4">
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>创建抽取任务</span>
          </template>

          <el-form :model="form" label-width="100px">
            <el-form-item label="任务名称">
              <el-input v-model="form.name" placeholder="输入任务名称" />
            </el-form-item>

            <el-form-item label="数据源">
              <el-select v-model="form.sourceId" placeholder="选择数据源">
                <el-option
                  v-for="source in dataSources"
                  :key="source.id"
                  :label="source.name"
                  :value="source.id"
                />
              </el-select>
            </el-form-item>

            <el-form-item label="抽取类型">
              <el-checkbox-group v-model="form.extractionTypes">
                <el-checkbox label="entity">实体抽取</el-checkbox>
                <el-checkbox label="relation">关系抽取</el-checkbox>
              </el-checkbox-group>
            </el-form-item>

            <el-form-item label="实体类型">
              <el-select
                v-model="form.entityTypes"
                multiple
                placeholder="选择要抽取的实体类型"
              >
                <el-option label="人物" value="PERSON" />
                <el-option label="组织" value="ORGANIZATION" />
                <el-option label="地点" value="LOCATION" />
                <el-option label="时间" value="DATE" />
              </el-select>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="startExtraction" :loading="starting">
                开始抽取
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="16">
        <el-card>
          <template #header>
            <span>抽取任务列表</span>
          </template>

          <el-table :data="extractionJobs" v-loading="loading">
            <el-table-column prop="job_id" label="任务ID" width="180" />
            <el-table-column prop="name" label="任务名称" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="getStatusType(row.status)">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="created_at" label="创建时间" width="180" />
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button link type="primary" @click="viewResult(row)">
                  查看结果
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>

        <el-card v-if="currentJob" class="mt-4">
          <template #header>
            <span>任务进度</span>
          </template>
          <JobProgress
            :job-type="currentJob.type"
            :progress="currentJob.progress"
            :status="currentJob.status"
            :stages="currentJob.stages"
            :error="currentJob.error"
          />
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import JobProgress from '@/components/extraction/JobProgress.vue'
import { useJobPolling } from '@/composables/useJobPolling'

const form = reactive({
  name: '',
  sourceId: '',
  extractionTypes: ['entity'],
  entityTypes: []
})

const loading = ref(false)
const starting = ref(false)
const currentJobId = ref('')
const currentJob = ref<any>(null)

const dataSources = ref([
  { id: 'source-1', name: '示例数据源1' },
  { id: 'source-2', name: '示例数据源2' }
])

const extractionJobs = ref<any[]>([])

const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    'pending': 'info',
    'running': 'warning',
    'completed': 'success',
    'failed': 'danger'
  }
  return map[status] || 'info'
}

const startExtraction = async () => {
  if (!form.name || !form.sourceId) {
    ElMessage.warning('请填写完整信息')
    return
  }

  starting.value = true
  try {
    // 调用API创建抽取任务
    // const response = await createExtractionJob(form)
    // currentJobId.value = response.job_id

    // 模拟
    currentJobId.value = `job-${Date.now()}`
    currentJob.value = {
      type: '知识抽取',
      status: 'running',
      progress: {
        percentage: 0,
        processed: 0,
        total: 100
      },
      stages: [
        { name: '数据加载', status: 'completed' },
        { name: '实体抽取', status: 'running' },
        { name: '关系抽取', status: 'pending' }
      ]
    }

    // 开始轮询
    const { status } = useJobPolling(currentJobId.value, {
      onComplete: (result) => {
        ElMessage.success('抽取完成')
        currentJob.value = result
      },
      onError: (error) => {
        ElMessage.error(error)
      }
    })

  } finally {
    starting.value = false
  }
}

const viewResult = (job: any) => {
  ElMessage.info(`查看任务结果: ${job.job_id}`)
}
</script>

<style scoped>
.extraction-manager {
  padding: 20px;
}
.mt-4 {
  margin-top: 16px;
}
</style>
