<script setup lang="ts">
import type { GraphEntityDraft } from '@/types/graph'

const props = defineProps<{
  drafts: GraphEntityDraft[]
}>()

const emit = defineEmits<{
  (e: 'add'): void
  (e: 'change', payload: { id: string; patch: Partial<GraphEntityDraft> }): void
  (e: 'remove', id: string): void
  (e: 'persist', id: string): void
}>()

function handleFieldChange(id: string, field: keyof GraphEntityDraft, value: unknown) {
  emit('change', { id, patch: { [field]: value } })
}
</script>

<template>
  <section class="entity-composer">
    <header class="entity-composer__header">
      <div>
        <h3>实体</h3>
        <p class="hint">定义要合并到图谱中的节点。</p>
      </div>
      <el-button type="primary" @click="emit('add')">添加实体</el-button>
    </header>

    <el-empty v-if="!drafts.length" description="尚未添加实体" />

    <el-row v-else :gutter="12">
      <el-col v-for="draft in drafts" :key="draft.id" :xs="24" :md="12">
        <el-card class="entity-card" shadow="hover">
          <template #header>
            <div class="entity-card__header">
              <span>{{ draft.external_id || '新实体' }}</span>
              <el-space>
                <el-tag v-if="draft.status === 'saved'" type="success" size="small">已保存</el-tag>
                <el-button
                  link
                  type="primary"
                  size="small"
                  @click="emit('persist', draft.id)"
                >
                  保存
                </el-button>
                <el-button
                  link
                  type="danger"
                  size="small"
                  @click="emit('remove', draft.id)"
                >
                  删除
                </el-button>
              </el-space>
            </div>
          </template>

          <el-form label-width="120px" class="entity-form">
            <el-form-item label="外部ID">
              <el-input
                :model-value="draft.external_id"
                placeholder="company-123"
                @input="handleFieldChange(draft.id, 'external_id', $event)"
              />
            </el-form-item>
            <el-form-item label="类型">
              <el-input
                :model-value="draft.type"
                placeholder="ENTERPRISE"
                @input="handleFieldChange(draft.id, 'type', $event)"
              />
            </el-form-item>
            <el-form-item label="标签">
              <el-select
                :model-value="draft.labels"
                multiple
                placeholder="添加标签"
                @change="handleFieldChange(draft.id, 'labels', $event)"
              >
                <el-option label="企业" value="Enterprise" />
                <el-option label="账户" value="Account" />
                <el-option label="个人" value="Person" />
              </el-select>
            </el-form-item>
            <el-form-item label="属性 JSON">
              <el-input
                type="textarea"
                :model-value="JSON.stringify(draft.properties ?? {}, null, 2)"
                :rows="4"
                @change="(value: string) => {
                  try {
                    handleFieldChange(draft.id, 'properties', JSON.parse(value || '{}'))
                  } catch (error) {
                    console.error('Invalid JSON', error)
                  }
                }"
              />
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>
  </section>
</template>

<style scoped>
.entity-composer__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.entity-card {
  margin-bottom: 16px;
}
.entity-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.hint {
  color: var(--el-text-color-secondary);
}
</style>
