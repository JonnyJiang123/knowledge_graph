<script setup lang="ts">
import { computed, ref } from 'vue'
import ConditionBuilder from './ConditionBuilder.vue'
import type {
  Rule,
  RuleType,
  ActionType,
  CreateRuleParams,
  UpdateRuleParams,
} from '@/types/reasoning'

const props = defineProps<{
  rule?: Rule
  projectId: string
  loading?: boolean
}>()

const emit = defineEmits<{
  (e: 'save', params: CreateRuleParams | UpdateRuleParams): void
  (e: 'cancel'): void
}>()

const isEdit = computed(() => !!props.rule)

const ruleTypeOptions: { value: RuleType; label: string }[] = [
  { value: 'FINANCE_FRAUD', label: '金融欺诈检测' },
  { value: 'FINANCE_RISK', label: '金融风险评估' },
  { value: 'HEALTHCARE_DRUG', label: '医疗用药分析' },
  { value: 'HEALTHCARE_DIAGNOSIS', label: '医疗诊断辅助' },
  { value: 'CUSTOM', label: '自定义规则' },
]

const actionTypeOptions: { value: ActionType; label: string }[] = [
  { value: 'flag_risk', label: '标记风险' },
  { value: 'create_alert', label: '创建告警' },
  { value: 'add_relation', label: '添加关系' },
  { value: 'update_property', label: '更新属性' },
]

const form = ref({
  name: props.rule?.name ?? '',
  description: props.rule?.description ?? '',
  ruleType: props.rule?.ruleType ?? 'CUSTOM',
  conditions: props.rule?.conditions ?? [],
  actions: props.rule?.actions ?? [],
  priority: props.rule?.priority ?? 50,
  isActive: props.rule?.isActive ?? true,
})

const formRef = ref()

const rules = {
  name: [
    { required: true, message: '请输入规则名称', trigger: 'blur' },
    { min: 2, max: 50, message: '名称长度在2-50个字符', trigger: 'blur' },
  ],
  description: [
    { max: 200, message: '描述长度不超过200个字符', trigger: 'blur' },
  ],
  ruleType: [
    { required: true, message: '请选择规则类型', trigger: 'change' },
  ],
  conditions: [
    { required: true, message: '请至少添加一个条件', trigger: 'change' },
  ],
  actions: [
    { required: true, message: '请至少配置一个动作', trigger: 'change' },
  ],
}

function addAction() {
  form.value.actions.push({
    type: 'create_alert',
    params: { level: 'MEDIUM', message: '' },
  })
}

function removeAction(index: number) {
  form.value.actions.splice(index, 1)
}

function updateActionType(index: number, type: ActionType) {
  const defaultParams: Record<ActionType, Record<string, any>> = {
    flag_risk: { level: 'MEDIUM' },
    create_alert: { level: 'MEDIUM', message: '' },
    add_relation: { type: 'RELATED_TO', target: '' },
    update_property: { key: '', value: '' },
  }
  form.value.actions[index] = {
    type,
    params: defaultParams[type],
  }
}

function validateConditions(): boolean {
  return form.value.conditions.length > 0
}

function validateActions(): boolean {
  return form.value.actions.length > 0
}

async function handleSave() {
  if (!formRef.value) return

  await formRef.value.validate((valid: boolean) => {
    if (!valid) return

    if (!validateConditions()) {
      return
    }

    if (!validateActions()) {
      return
    }

    const params = isEdit.value
      ? {
          name: form.value.name,
          description: form.value.description,
          ruleType: form.value.ruleType,
          conditions: form.value.conditions,
          actions: form.value.actions,
          priority: form.value.priority,
          isActive: form.value.isActive,
        }
      : {
          projectId: props.projectId,
          name: form.value.name,
          description: form.value.description,
          ruleType: form.value.ruleType,
          conditions: form.value.conditions,
          actions: form.value.actions,
          priority: form.value.priority,
          isActive: form.value.isActive,
        }

    emit('save', params)
  })
}

// function getActionTypeLabel(type: ActionType): string {
//   return actionTypeOptions.find((opt) => opt.value === type)?.label ?? type
// }
</script>

<template>
  <el-form
    ref="formRef"
    :model="form"
    :rules="rules"
    label-width="100px"
    class="rule-editor"
  >
    <el-card>
      <template #header>
        <span>基本信息</span>
      </template>

      <el-form-item label="规则名称" prop="name">
        <el-input v-model="form.name" placeholder="输入规则名称" />
      </el-form-item>

      <el-form-item label="规则描述" prop="description">
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="2"
          placeholder="输入规则描述"
        />
      </el-form-item>

      <el-form-item label="规则类型" prop="ruleType">
        <el-select v-model="form.ruleType" placeholder="选择规则类型" style="width: 100%">
          <el-option
            v-for="opt in ruleTypeOptions"
            :key="opt.value"
            :label="opt.label"
            :value="opt.value"
          />
        </el-select>
      </el-form-item>

      <el-form-item label="优先级">
        <div class="priority-slider">
          <el-slider v-model="form.priority" :min="1" :max="100" show-stops />
          <span class="priority-value">{{ form.priority }}</span>
        </div>
      </el-form-item>

      <el-form-item label="启用状态">
        <el-switch
          v-model="form.isActive"
          active-text="启用"
          inactive-text="禁用"
        />
      </el-form-item>
    </el-card>

    <el-card class="mt-4">
      <template #header>
        <span>条件配置</span>
      </template>

      <ConditionBuilder
        v-model:conditions="form.conditions"
        @add="form.conditions.push({ field: '', operator: 'equals', value: '' })"
      />

      <el-alert
        v-if="!form.conditions.length"
        title="请至少添加一个条件"
        type="warning"
        :closable="false"
        class="mt-2"
      />
    </el-card>

    <el-card class="mt-4">
      <template #header>
        <div class="actions-header">
          <span>动作配置</span>
          <el-button type="primary" size="small" @click="addAction">
            <el-icon><Plus /></el-icon>
            添加动作
          </el-button>
        </div>
      </template>

      <div v-if="!form.actions.length" class="empty-actions">
        <el-empty description="暂无动作" :image-size="60" />
      </div>

      <div v-else class="actions-list">
        <div
          v-for="(action, index) in form.actions"
          :key="index"
          class="action-item"
        >
          <div class="action-header">
            <el-tag size="small" type="warning" effect="plain">
              动作 {{ index + 1 }}
            </el-tag>
            <el-button
              link
              type="danger"
              size="small"
              @click="removeAction(index)"
            >
              <el-icon><Delete /></el-icon>
            </el-button>
          </div>

          <div class="action-fields">
            <el-select
              :model-value="action.type"
              placeholder="选择动作类型"
              size="small"
              @change="updateActionType(index, $event)"
            >
              <el-option
                v-for="opt in actionTypeOptions"
                :key="opt.value"
                :label="opt.label"
                :value="opt.value"
              />
            </el-select>

            <!-- flag_risk params -->
            <template v-if="action.type === 'flag_risk'">
              <el-select
                v-model="action.params.level"
                placeholder="风险等级"
                size="small"
              >
                <el-option label="低" value="LOW" />
                <el-option label="中" value="MEDIUM" />
                <el-option label="高" value="HIGH" />
                <el-option label="严重" value="CRITICAL" />
              </el-select>
            </template>

            <!-- create_alert params -->
            <template v-if="action.type === 'create_alert'">
              <el-select
                v-model="action.params.level"
                placeholder="告警等级"
                size="small"
              >
                <el-option label="低" value="LOW" />
                <el-option label="中" value="MEDIUM" />
                <el-option label="高" value="HIGH" />
                <el-option label="严重" value="CRITICAL" />
              </el-select>
              <el-input
                v-model="action.params.message"
                placeholder="告警消息"
                size="small"
              />
            </template>

            <!-- add_relation params -->
            <template v-if="action.type === 'add_relation'">
              <el-input
                v-model="action.params.type"
                placeholder="关系类型"
                size="small"
              />
              <el-input
                v-model="action.params.target"
                placeholder="目标实体ID"
                size="small"
              />
            </template>

            <!-- update_property params -->
            <template v-if="action.type === 'update_property'">
              <el-input
                v-model="action.params.key"
                placeholder="属性名"
                size="small"
              />
              <el-input
                v-model="action.params.value"
                placeholder="属性值"
                size="small"
              />
            </template>
          </div>
        </div>
      </div>

      <el-alert
        v-if="!form.actions.length"
        title="请至少配置一个动作"
        type="warning"
        :closable="false"
        class="mt-2"
      />
    </el-card>

    <div class="editor-actions">
      <el-button @click="emit('cancel')">取消</el-button>
      <el-button
        type="primary"
        :loading="loading"
        @click="handleSave"
      >
        {{ isEdit ? '保存' : '创建' }}
      </el-button>
    </div>
  </el-form>
</template>

<style scoped>
.rule-editor {
  max-width: 800px;
}

.mt-4 {
  margin-top: 16px;
}

.priority-slider {
  display: flex;
  align-items: center;
  gap: 16px;
}

.priority-slider .el-slider {
  flex: 1;
}

.priority-value {
  width: 40px;
  text-align: center;
  font-weight: bold;
  color: var(--el-color-primary);
}

.actions-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.empty-actions {
  padding: 20px 0;
}

.actions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.action-item {
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  padding: 12px;
  background-color: var(--el-fill-color-light);
}

.action-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.action-fields {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
}

.editor-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--el-border-color-light);
}
</style>
