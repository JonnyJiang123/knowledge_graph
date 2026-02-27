<script setup lang="ts">
import { computed } from 'vue'
import type { Condition, Operator } from '@/types/reasoning'

const props = defineProps<{
  conditions: Condition[]
}>()

const emit = defineEmits<{
  (e: 'update:conditions', conditions: Condition[]): void
  (e: 'add'): void
  (e: 'remove', index: number): void
}>()

const operatorOptions: { value: Operator; label: string }[] = [
  { value: 'equals', label: '等于' },
  { value: 'not_equals', label: '不等于' },
  { value: 'in', label: '包含于' },
  { value: 'not_in', label: '不包含于' },
  { value: 'greater_than', label: '大于' },
  { value: 'less_than', label: '小于' },
  { value: 'exists', label: '存在' },
]

const fieldOptions = [
  { value: 'entity.type', label: '实体类型' },
  { value: 'entity.labels', label: '实体标签' },
  { value: 'entity.properties.risk_level', label: '风险等级' },
  { value: 'entity.properties.amount', label: '金额' },
  { value: 'entity.properties.status', label: '状态' },
  { value: 'relation.type', label: '关系类型' },
]

function addCondition() {
  const newCondition: Condition = {
    field: fieldOptions[0].value,
    operator: 'equals',
    value: '',
  }
  emit('update:conditions', [...props.conditions, newCondition])
  emit('add')
}

function removeCondition(index: number) {
  const newConditions = [...props.conditions]
  newConditions.splice(index, 1)
  emit('update:conditions', newConditions)
  emit('remove', index)
}

function updateCondition(index: number, field: keyof Condition, value: any) {
  const newConditions = [...props.conditions]
  newConditions[index] = { ...newConditions[index], [field]: value }
  emit('update:conditions', newConditions)
}

function getValuePlaceholder(operator: Operator): string {
  switch (operator) {
    case 'in':
    case 'not_in':
      return '多个值用逗号分隔'
    case 'greater_than':
    case 'less_than':
      return '输入数值'
    case 'exists':
      return '无需输入'
    default:
      return '输入值'
  }
}

const isValueDisabled = computed(() => (operator: Operator) => operator === 'exists')
</script>

<template>
  <div class="condition-builder">
    <div v-if="!conditions.length" class="empty-conditions">
      <el-empty description="暂无条件" :image-size="80">
        <el-button type="primary" size="small" @click="addCondition">
          添加条件
        </el-button>
      </el-empty>
    </div>

    <div v-else class="conditions-list">
      <div
        v-for="(condition, index) in conditions"
        :key="index"
        class="condition-item"
      >
        <div class="condition-header">
          <el-tag size="small" type="info" effect="plain">
            条件 {{ index + 1 }}
          </el-tag>
          <el-button
            link
            type="danger"
            size="small"
            @click="removeCondition(index)"
          >
            <el-icon><Delete /></el-icon>
          </el-button>
        </div>

        <div class="condition-fields">
          <el-select
            :model-value="condition.field"
            placeholder="选择字段"
            size="small"
            @change="updateCondition(index, 'field', $event)"
          >
            <el-option
              v-for="opt in fieldOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>

          <el-select
            :model-value="condition.operator"
            placeholder="选择操作符"
            size="small"
            @change="updateCondition(index, 'operator', $event)"
          >
            <el-option
              v-for="opt in operatorOptions"
              :key="opt.value"
              :label="opt.label"
              :value="opt.value"
            />
          </el-select>

          <el-input
            :model-value="condition.value"
            :placeholder="getValuePlaceholder(condition.operator)"
            :disabled="isValueDisabled(condition.operator)"
            size="small"
            @input="updateCondition(index, 'value', $event)"
          />
        </div>
      </div>

      <el-button type="primary" size="small" plain @click="addCondition">
        <el-icon><Plus /></el-icon>
        添加条件
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.condition-builder {
  padding: 8px 0;
}

.empty-conditions {
  padding: 20px 0;
}

.conditions-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.condition-item {
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  padding: 12px;
  background-color: var(--el-fill-color-light);
}

.condition-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.condition-fields {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 12px;
}

@media (max-width: 768px) {
  .condition-fields {
    grid-template-columns: 1fr;
    gap: 8px;
  }
}
</style>
