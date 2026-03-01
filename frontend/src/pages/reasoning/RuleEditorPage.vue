<script setup lang="ts">
import { onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import RuleEditor from '@/components/reasoning/RuleEditor.vue'
import { useReasoningStore } from '@/stores/reasoning'
import { useGraphStore } from '@/stores/graph'
import type { CreateRuleParams, UpdateRuleParams } from '@/types/reasoning'

const route = useRoute()
const router = useRouter()
const reasoningStore = useReasoningStore()
const graphStore = useGraphStore()

const ruleId = computed(() => route.params.id as string | undefined)
const isEdit = computed(() => !!ruleId.value)

const currentRule = computed(() => {
  if (!ruleId.value) return undefined
  return reasoningStore.getRuleById(ruleId.value)
})

onMounted(async () => {
  if (!graphStore.currentProjectId) {
    await graphStore.loadProjects()
  }
  if (ruleId.value && !reasoningStore.rules.length) {
    await reasoningStore.loadRules(graphStore.currentProjectId)
  }
})

async function handleSave(params: CreateRuleParams | UpdateRuleParams) {
  try {
    if (isEdit.value && ruleId.value) {
      await reasoningStore.updateRule(ruleId.value, params as UpdateRuleParams)
      ElMessage.success('规则已更新')
    } else {
      await reasoningStore.createRule(graphStore.currentProjectId, params as CreateRuleParams)
      ElMessage.success('规则已创建')
    }
    router.push('/reasoning/rules')
  } catch (error) {
    ElMessage.error(error instanceof Error ? error.message : '操作失败')
  }
}

function handleCancel() {
  router.push('/reasoning/rules')
}
</script>

<template>
  <div class="rule-editor-page">
    <el-card>
      <template #header>
        <div class="editor-header">
          <div>
            <h2>{{ isEdit ? '编辑规则' : '创建规则' }}</h2>
            <p class="hint">
              {{ isEdit ? '修改现有推理规则的配置' : '配置新的知识图谱推理规则' }}
            </p>
          </div>
        </div>
      </template>

      <RuleEditor
        :rule="currentRule"
        :project-id="graphStore.currentProjectId"
        :loading="reasoningStore.loading.save"
        @save="handleSave"
        @cancel="handleCancel"
      />
    </el-card>
  </div>
</template>

<style scoped>
.rule-editor-page {
  padding: 24px;
  max-width: 1000px;
  margin: 0 auto;
}

.editor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.hint {
  color: var(--el-text-color-secondary);
  margin: 4px 0 0 0;
}
</style>
