<script setup lang="ts">
import { computed } from 'vue'
import type { Rule, RuleType } from '@/types/reasoning'

const props = defineProps<{
  rules: Rule[]
  loading?: boolean
}>()

const emit = defineEmits<{
  (e: 'edit', rule: Rule): void
  (e: 'delete', rule: Rule): void
  (e: 'toggle', rule: Rule, isActive: boolean): void
  (e: 'run', rule: Rule): void
}>()

const sortedRules = computed(() => {
  return [...props.rules].sort((a, b) => b.priority - a.priority)
})

function getRuleTypeLabel(type: RuleType): string {
  const labels: Record<RuleType, string> = {
    FINANCE_FRAUD: '金融欺诈检测',
    FINANCE_RISK: '金融风险评估',
    HEALTHCARE_DRUG: '医疗用药分析',
    HEALTHCARE_DIAGNOSIS: '医疗诊断辅助',
    CUSTOM: '自定义规则',
  }
  return labels[type] ?? type
}

function getRuleTypeTag(type: RuleType): "info" | "warning" | "danger" | "primary" | "success" | undefined {
  const tags: Record<RuleType, "info" | "warning" | "danger" | "primary" | "success" | undefined> = {
    FINANCE_FRAUD: 'danger',
    FINANCE_RISK: 'warning',
    HEALTHCARE_DRUG: 'success',
    HEALTHCARE_DIAGNOSIS: 'info',
    CUSTOM: undefined,
  }
  return tags[type]
}

function getStatusTag(isActive: boolean) {
  return isActive ? 'success' : 'info'
}

function getStatusLabel(isActive: boolean) {
  return isActive ? '启用' : '禁用'
}

function formatDate(dateStr: string): string {
  return new Date(dateStr).toLocaleString('zh-CN')
}
</script>

<template>
  <div class="rule-list">
    <el-table
      v-loading="loading"
      :data="sortedRules"
      stripe
      style="width: 100%"
    >
      <el-table-column prop="name" label="规则名称" min-width="150">
        <template #default="{ row }">
          <div class="rule-name">
            <span class="name-text">{{ row.name }}</span>
            <el-tag
              size="small"
              :type="getRuleTypeTag(row.ruleType)"
              class="rule-type-tag"
            >
              {{ getRuleTypeLabel(row.ruleType) }}
            </el-tag>
          </div>
        </template>
      </el-table-column>

      <el-table-column prop="description" label="描述" min-width="200" show-overflow-tooltip>
        <template #default="{ row }">
          {{ row.description || '-' }}
        </template>
      </el-table-column>

      <el-table-column prop="priority" label="优先级" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="row.priority >= 80 ? 'danger' : row.priority >= 50 ? 'warning' : 'info'" effect="plain">
            {{ row.priority }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="isActive" label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-tag :type="getStatusTag(row.isActive)" effect="light">
            {{ getStatusLabel(row.isActive) }}
          </el-tag>
        </template>
      </el-table-column>

      <el-table-column prop="updatedAt" label="更新时间" width="160">
        <template #default="{ row }">
          {{ formatDate(row.updatedAt) }}
        </template>
      </el-table-column>

      <el-table-column label="操作" width="240" fixed="right">
        <template #default="{ row }">
          <el-space>
            <el-switch
              :model-value="row.isActive"
              size="small"
              @change="emit('toggle', row, $event as boolean)"
            />
            <el-button
              link
              type="primary"
              size="small"
              @click="emit('edit', row)"
            >
              编辑
            </el-button>
            <el-button
              link
              type="success"
              size="small"
              @click="emit('run', row)"
            >
              运行
            </el-button>
            <el-button
              link
              type="danger"
              size="small"
              @click="emit('delete', row)"
            >
              删除
            </el-button>
          </el-space>
        </template>
      </el-table-column>
    </el-table>

    <el-empty v-if="!rules.length && !loading" description="暂无规则" :image-size="100">
      <template #description>
        <p>暂无规则</p>
        <p class="hint">点击上方按钮创建新规则</p>
      </template>
    </el-empty>
  </div>
</template>

<style scoped>
.rule-list {
  width: 100%;
}

.rule-name {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.name-text {
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.rule-type-tag {
  align-self: flex-start;
}

.hint {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}
</style>
