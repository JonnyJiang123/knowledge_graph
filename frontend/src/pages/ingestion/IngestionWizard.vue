<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useIngestionStore } from '@/stores/ingestion'
import { useProjectStore } from '@/stores/project'
import { ElMessage } from 'element-plus'
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'

import SourceSelector from '@/components/ingestion/SourceSelector.vue'
import MySQLConnectorForm from '@/components/ingestion/MySQLConnectorForm.vue'
import FileUploadStep from '@/components/ingestion/FileUploadStep.vue'
import CleaningRuleBuilder from '@/components/ingestion/CleaningRuleBuilder.vue'
import PreviewTable from '@/components/ingestion/PreviewTable.vue'
import SubmissionPanel from '@/components/ingestion/SubmissionPanel.vue'

const route = useRoute()
const router = useRouter()
const ingestionStore = useIngestionStore()
const projectStore = useProjectStore()

// 向导步骤
const activeStep = ref(0)
const steps = [
  { title: '选择数据源', description: '选择文件或数据库' },
  { title: '配置数据源', description: '上传文件或配置连接' },
  { title: '数据清洗', description: '配置清洗规则' },
  { title: '预览确认', description: '预览并提交' },
]

// 项目 ID（从路由或 store 获取）
const projectId = computed(() => {
  return (route.query.projectId as string) || projectStore.currentProject?.id || ''
})

// 选中的文件
const selectedFile = ref<File | null>(null)
// MySQL 测试状态
const mysqlTesting = ref(false)
const mysqlTestResult = ref<{ ok: boolean; message: string } | null>(null)
// 提交状态
const submitting = ref(false)
const submittedJobId = ref<string | null>(null)
const submittedJobStatus = ref<'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED' | null>(null)
const submittedJobMode = ref<'SYNC' | 'ASYNC' | null>(null)

// 初始化
onMounted(async () => {
  if (projectId.value) {
    ingestionStore.setProject(projectId.value)
  }
  // 加载清洗规则模板和已保存的数据源
  await Promise.all([
    ingestionStore.fetchTemplates(),
    projectId.value ? ingestionStore.fetchSources(projectId.value) : Promise.resolve(),
  ])
})

// 监听项目变化
watch(projectId, (newId) => {
  if (newId) {
    ingestionStore.setProject(newId)
    ingestionStore.fetchSources(newId)
  }
})

// 验证当前步骤是否可以继续
const canProceed = computed(() => {
  switch (activeStep.value) {
    case 0:
      // 数据源类型已选择
      return !!ingestionStore.wizardForm.sourceType
    case 1:
      // 文件已选择或 MySQL 连接已测试
      if (ingestionStore.wizardForm.sourceType === 'FILE') {
        return !!selectedFile.value
      } else {
        return mysqlTestResult.value?.ok || !!ingestionStore.wizardForm.selectedSourceId
      }
    case 2:
      // 清洗规则步骤可以跳过（规则可选）
      return true
    case 3:
      // 确认步骤
      return true
    default:
      return false
  }
})

// 下一步
function nextStep() {
  if (activeStep.value < steps.length - 1) {
    activeStep.value++
  }
}

// 上一步
function prevStep() {
  if (activeStep.value > 0) {
    activeStep.value--
  }
}

// 处理文件选择
function handleFileSelected(file: File) {
  selectedFile.value = file
}

// 测试 MySQL 连接
async function handleTestMysql() {
  if (!projectId.value) {
    ElMessage.warning('请先选择项目')
    return
  }

  mysqlTesting.value = true
  mysqlTestResult.value = null

  try {
    const result = await ingestionStore.testMysql({
      ...ingestionStore.wizardForm.mysql,
      projectId: projectId.value,
    })
    mysqlTestResult.value = result
    if (result.ok) {
      ElMessage.success('连接成功')
    } else {
      ElMessage.error(result.message || '连接失败')
    }
  } catch (error) {
    mysqlTestResult.value = { ok: false, message: '连接测试失败' }
    ElMessage.error('连接测试失败')
  } finally {
    mysqlTesting.value = false
  }
}

// 提交任务
async function handleSubmit() {
  if (!projectId.value) {
    ElMessage.warning('请先选择项目')
    return
  }

  submitting.value = true

  try {
    if (ingestionStore.wizardForm.sourceType === 'FILE' && selectedFile.value) {
      // 文件上传
      const response = await ingestionStore.uploadFile({
        projectId: projectId.value,
        file: selectedFile.value,
        rules: ingestionStore.wizardForm.cleaningRules,
      })
      submittedJobId.value = response.jobId ?? null
      submittedJobStatus.value = response.status
      submittedJobMode.value = response.mode
      ElMessage.success('文件上传成功')
    } else {
      // MySQL 导入
      const sourceId = ingestionStore.wizardForm.selectedSourceId
      if (!sourceId) {
        // 需要先保存数据源
        const source = await ingestionStore.saveSource({
          projectId: projectId.value,
          type: 'MYSQL',
          name: `MySQL-${ingestionStore.wizardForm.mysql.database}`,
          mysql: ingestionStore.wizardForm.mysql,
        })
        ingestionStore.wizardForm.selectedSourceId = source.id
      }

      const job = await ingestionStore.submitMysqlImport({
        projectId: projectId.value,
        sourceId: ingestionStore.wizardForm.selectedSourceId!,
        table: ingestionStore.wizardForm.mysql.table,
        rules: ingestionStore.wizardForm.cleaningRules,
      })
      submittedJobId.value = job.id
      submittedJobStatus.value = job.status
      submittedJobMode.value = job.mode
      ElMessage.success('MySQL 导入任务已提交')
    }
  } catch (error) {
    ElMessage.error('提交失败，请重试')
  } finally {
    submitting.value = false
  }
}

// 跳转到任务列表
function handleViewJobs() {
  router.push({ path: '/ingestion/jobs', query: { projectId: projectId.value } })
}

// 重置向导
function resetWizard() {
  activeStep.value = 0
  selectedFile.value = null
  mysqlTestResult.value = null
  submittedJobId.value = null
  submittedJobStatus.value = null
  submittedJobMode.value = null
  ingestionStore.resetWizard(projectId.value)
}
</script>

<template>
  <div class="ingestion-wizard">
    <el-page-header @back="router.back()">
      <template #content>
        <span class="page-title">数据导入向导</span>
      </template>
      <template #extra>
        <el-button @click="resetWizard">重置</el-button>
      </template>
    </el-page-header>

    <el-card class="wizard-card">
      <!-- 步骤条 -->
      <el-steps :active="activeStep" finish-status="success" align-center>
        <el-step
          v-for="(step, index) in steps"
          :key="index"
          :title="step.title"
          :description="step.description"
        />
      </el-steps>

      <el-divider />

      <!-- 步骤内容 -->
      <div class="step-content">
        <!-- 步骤 1: 选择数据源 -->
        <div v-show="activeStep === 0">
          <SourceSelector
            v-model="ingestionStore.wizardForm.sourceType"
            v-model:selected-source-id="ingestionStore.wizardForm.selectedSourceId"
            :sources="ingestionStore.sources"
          />
        </div>

        <!-- 步骤 2: 配置数据源 -->
        <div v-show="activeStep === 1">
          <template v-if="ingestionStore.wizardForm.sourceType === 'FILE'">
            <FileUploadStep
              :loading="ingestionStore.loading.upload"
              @file-selected="handleFileSelected"
            />
          </template>
          <template v-else>
            <MySQLConnectorForm
              v-model="ingestionStore.wizardForm.mysql"
              :loading="mysqlTesting"
              @test="handleTestMysql"
            />
          </template>
        </div>

        <!-- 步骤 3: 清洗规则 -->
        <div v-show="activeStep === 2">
          <CleaningRuleBuilder
            v-model="ingestionStore.wizardForm.cleaningRules"
            :templates="ingestionStore.cleaningRuleTemplates"
          />
          <el-alert
            v-if="ingestionStore.wizardForm.cleaningRules.length === 0"
            type="info"
            title="提示"
            description="清洗规则为可选配置，您可以直接跳过此步骤"
            :closable="false"
            show-icon
            style="margin-top: 16px"
          />
        </div>

        <!-- 步骤 4: 预览确认 -->
        <div v-show="activeStep === 3">
          <el-row :gutter="24">
            <el-col :span="12">
              <h4>数据预览</h4>
              <PreviewTable
                :data="ingestionStore.previewRows"
                :loading="ingestionStore.loading.upload"
              />
            </el-col>
            <el-col :span="12">
              <SubmissionPanel
                :source-type="ingestionStore.wizardForm.sourceType"
                :file-name="selectedFile?.name"
                :mysql-source-name="ingestionStore.wizardForm.mysql.database"
                :rules-count="ingestionStore.wizardForm.cleaningRules.length"
                :loading="submitting"
                :submitted-job-id="submittedJobId"
                :job-status="submittedJobStatus ?? undefined"
                :job-mode="submittedJobMode ?? undefined"
                @submit="handleSubmit"
                @view-jobs="handleViewJobs"
              />
            </el-col>
          </el-row>
        </div>
      </div>

      <!-- 导航按钮 -->
      <div class="step-actions">
        <el-button
          v-if="activeStep > 0"
          :icon="ArrowLeft"
          @click="prevStep"
        >
          上一步
        </el-button>
        <el-button
          v-if="activeStep < steps.length - 1"
          type="primary"
          :disabled="!canProceed"
          @click="nextStep"
        >
          下一步
          <el-icon class="el-icon--right"><ArrowRight /></el-icon>
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<style scoped lang="scss">
.ingestion-wizard {
  padding: 20px;

  .page-title {
    font-size: 18px;
    font-weight: 600;
  }

  .wizard-card {
    margin-top: 20px;
  }

  .step-content {
    min-height: 300px;
    padding: 20px 0;
  }

  .step-actions {
    display: flex;
    justify-content: center;
    gap: 16px;
    padding-top: 20px;
    border-top: 1px solid var(--el-border-color-light);
  }
}
</style>
