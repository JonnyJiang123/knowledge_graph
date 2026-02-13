<script setup lang="ts">
import { ref, computed } from 'vue'
import { Plus, Delete } from '@element-plus/icons-vue'
import type { CleaningRule, CleaningRuleTemplate, CleaningRuleType } from '@/types/ingestion'

const props = defineProps<{
  modelValue: CleaningRule[]
  templates: CleaningRuleTemplate[]
  fields?: string[]
}>()

const emit = defineEmits<{
  'update:modelValue': [value: CleaningRule[]]
}>()

const rules = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

// 新规则表单
const newRule = ref<Partial<CleaningRule>>({
  type: 'NOT_NULL',
  field: '',
  severity: 'WARN',
})

const ruleTypes: Array<{ value: CleaningRuleType; label: string }> = [
  { value: 'NOT_NULL', label: '非空检查' },
  { value: 'RANGE', label: '范围限制' },
  { value: 'REGEX', label: '正则匹配' },
  { value: 'DEDUPE', label: '去重' },
]

const severityOptions = [
  { value: 'INFO', label: '信息', type: 'info' as const },
  { value: 'WARN', label: '警告', type: 'warning' as const },
  { value: 'ERROR', label: '错误', type: 'danger' as const },
]

// 范围参数（仅 RANGE 类型需要）
const rangeMin = ref<number | undefined>()
const rangeMax = ref<number | undefined>()
// 正则参数（仅 REGEX 类型需要）
const regexPattern = ref('')

function addRule() {
  if (!newRule.value.field || !newRule.value.type) return

  const rule: CleaningRule = {
    type: newRule.value.type,
    field: newRule.value.field,
    severity: newRule.value.severity ?? 'WARN',
  }

  // 根据类型添加参数
  if (rule.type === 'RANGE') {
    rule.params = { min: rangeMin.value, max: rangeMax.value }
  } else if (rule.type === 'REGEX') {
    rule.params = { pattern: regexPattern.value }
  }

  rules.value = [...rules.value, rule]
  resetForm()
}

function removeRule(index: number) {
  const updated = [...rules.value]
  updated.splice(index, 1)
  rules.value = updated
}

function resetForm() {
  newRule.value = { type: 'NOT_NULL', field: '', severity: 'WARN' }
  rangeMin.value = undefined
  rangeMax.value = undefined
  regexPattern.value = ''
}

function getTemplateDescription(key: string) {
  return props.templates.find((t) => t.key === key)?.description ?? ''
}
</script>

<template>
  <div class="cleaning-rule-builder">
    <!-- 已添加的规则列表 -->
    <div v-if="rules.length > 0" class="rules-list">
      <el-table :data="rules" size="small" stripe>
        <el-table-column prop="field" label="字段" width="150" />
        <el-table-column prop="type" label="规则类型" width="120">
          <template #default="{ row }">
            {{ ruleTypes.find((t) => t.value === row.type)?.label }}
          </template>
        </el-table-column>
        <el-table-column prop="severity" label="级别" width="80">
          <template #default="{ row }">
            <el-tag
              :type="severityOptions.find((s) => s.value === row.severity)?.type"
              size="small"
            >
              {{ severityOptions.find((s) => s.value === row.severity)?.label }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="参数">
          <template #default="{ row }">
            <template v-if="row.type === 'RANGE'">
              {{ row.params?.min ?? '-∞' }} ~ {{ row.params?.max ?? '+∞' }}
            </template>
            <template v-else-if="row.type === 'REGEX'">
              <code>{{ row.params?.pattern }}</code>
            </template>
            <template v-else>-</template>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="80" fixed="right">
          <template #default="{ $index }">
            <el-button
              type="danger"
              :icon="Delete"
              size="small"
              circle
              @click="removeRule($index)"
            />
          </template>
        </el-table-column>
      </el-table>
    </div>

    <el-divider v-if="rules.length > 0" />

    <!-- 添加新规则表单 -->
    <div class="add-rule-form">
      <el-form :inline="true" size="default">
        <el-form-item label="字段">
          <el-select
            v-if="fields && fields.length > 0"
            v-model="newRule.field"
            placeholder="选择字段"
            filterable
            allow-create
            style="width: 150px"
          >
            <el-option
              v-for="field in fields"
              :key="field"
              :label="field"
              :value="field"
            />
          </el-select>
          <el-input
            v-else
            v-model="newRule.field"
            placeholder="输入字段名"
            style="width: 150px"
          />
        </el-form-item>

        <el-form-item label="规则">
          <el-select v-model="newRule.type" style="width: 120px">
            <el-option
              v-for="rt in ruleTypes"
              :key="rt.value"
              :label="rt.label"
              :value="rt.value"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="级别">
          <el-select v-model="newRule.severity" style="width: 90px">
            <el-option
              v-for="sev in severityOptions"
              :key="sev.value"
              :label="sev.label"
              :value="sev.value"
            />
          </el-select>
        </el-form-item>

        <!-- 范围参数 -->
        <template v-if="newRule.type === 'RANGE'">
          <el-form-item label="最小值">
            <el-input-number v-model="rangeMin" :controls="false" style="width: 100px" />
          </el-form-item>
          <el-form-item label="最大值">
            <el-input-number v-model="rangeMax" :controls="false" style="width: 100px" />
          </el-form-item>
        </template>

        <!-- 正则参数 -->
        <template v-if="newRule.type === 'REGEX'">
          <el-form-item label="正则">
            <el-input v-model="regexPattern" placeholder="^[A-Z]+" style="width: 180px" />
          </el-form-item>
        </template>

        <el-form-item>
          <el-button type="primary" :icon="Plus" @click="addRule">
            添加规则
          </el-button>
        </el-form-item>
      </el-form>
    </div>

    <!-- 规则模板提示 -->
    <div v-if="newRule.type" class="rule-hint">
      <el-text type="info" size="small">
        {{ getTemplateDescription(newRule.type) }}
      </el-text>
    </div>
  </div>
</template>

<style scoped lang="scss">
.cleaning-rule-builder {
  .rules-list {
    margin-bottom: 16px;
  }

  .add-rule-form {
    margin-top: 16px;
  }

  .rule-hint {
    margin-top: 8px;
  }
}
</style>
