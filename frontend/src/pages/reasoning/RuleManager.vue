<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import RuleList from '@/components/reasoning/RuleList.vue'
import { useReasoningStore } from '@/stores/reasoning'
import { useGraphStore } from '@/stores/graph'

const router = useRouter()
const reasoningStore = useReasoningStore()
const graphStore = useGraphStore()

const currentPage = ref(1)
const pageSize = ref(10)

const totalRules = computed(() => reasoningStore.rules.length)

const paginatedRules = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return reasoningStore.rules.slice(start, end)
})

onMounted(async () => {
  if (!graphStore.currentProjectId) {
    await graphStore.loadProjects()
  }
  if (graphStore.currentProjectId) {
    await reasoningStore.loadRules(graphStore.currentProjectId)
  }
})

function handleCreate() {
  router.push('/reasoning/rules/create')
}

function handleEdit(rule: any) {
  router.push(`/reasoning/rules/${rule.id}/edit`)
}

async function handleToggle(rule: any, isActive: boolean) {
  try {
    await reasoningStore.updateRule(rule.id, { isActive })
    ElMessage.success(isActive ? '规则已启用' : '规则已禁用')
  } catch (error) {
    ElMessage.error('操作失败')
  }
}

async function handleDelete(rule: any) {
  try {
    await ElMessageBox.confirm(
      `确定要删除规则 "${rule.name}" 吗？`,
      '删除确认',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    await reasoningStore.deleteRule(rule.id)
    ElMessage.success('规则已删除')
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

async function handleRun(rule: any) {
  try {
    const job = await reasoningStore.runReasoning(graphStore.currentProjectId, rule.id)
    ElMessage.success('推理任务已启动')
    router.push(`/reasoning/results/${job.jobId}`)
  } catch (error) {
    ElMessage.error('启动推理失败')
  }
}
</script>

<template>
  <div class="rule-manager">
    <el-card>
      <template #header>
        <div class="manager-header">
          <div>
            <h2>推理规则管理</h2>
            <p class="hint">管理知识图谱推理规则，配置条件与动作</p>
          </div>
          <el-button type="primary" @click="handleCreate">
            <el-icon><Plus /></el-icon>
            创建规则
          </el-button>
        </div>
      </template>

      <div class="project-info" v-if="graphStore.currentProjectId">
        <el-tag type="info" effect="plain">
          当前项目: {{ graphStore.projects.find(p => p.id === graphStore.currentProjectId)?.name }}
        </el-tag>
      </div>

      <RuleList
        :rules="paginatedRules"
        :loading="reasoningStore.loading.rules"
        @edit="handleEdit"
        @delete="handleDelete"
        @toggle="handleToggle"
        @run="handleRun"
      />

      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :total="totalRules"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          background
        />
      </div>
    </el-card>
  </div>
</template>

<style scoped>
.rule-manager {
  padding: 24px;
}

.manager-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.hint {
  color: var(--el-text-color-secondary);
  margin: 4px 0 0 0;
}

.project-info {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--el-border-color-light);
}

.pagination-wrapper {
  display: flex;
  justify-content: flex-end;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--el-border-color-light);
}
</style>
