<script setup lang="ts">
import type { GraphRelationDraft } from '@/types/graph'

const props = defineProps<{
  drafts: GraphRelationDraft[]
}>()

const emit = defineEmits<{
  (e: 'add'): void
  (e: 'change', payload: { id: string; patch: Partial<GraphRelationDraft> }): void
  (e: 'remove', id: string): void
  (e: 'persist', id: string): void
}>()

function handleFieldChange(id: string, field: keyof GraphRelationDraft, value: unknown) {
  emit('change', { id, patch: { [field]: value } })
}
</script>

<template>
  <section class="relation-composer">
    <header class="relation-composer__header">
      <div>
        <h3>关系</h3>
        <p class="hint">通过指定关系类型和端点来链接已保存的实体。</p>
      </div>
      <el-button type="primary" @click="emit('add')">添加关系</el-button>
    </header>

    <el-empty v-if="!drafts.length" description="尚未定义关系" />

    <el-row v-else :gutter="12">
      <el-col v-for="draft in drafts" :key="draft.id" :xs="24" :md="12">
        <el-card class="relation-card" shadow="hover">
          <template #header>
            <div class="relation-card__header">
              <span>{{ draft.type || '新关系' }}</span>
              <el-space>
                <el-tag v-if="draft.status === 'saved'" type="success" size="small">已保存</el-tag>
                <el-button link type="primary" size="small" @click="emit('persist', draft.id)">
                  保存
                </el-button>
                <el-button link type="danger" size="small" @click="emit('remove', draft.id)">
                  删除
                </el-button>
              </el-space>
            </div>
          </template>
          <el-form label-width="120px" class="relation-form">
            <el-form-item label="Source Entity ID">
              <el-input
                :model-value="draft.source_id"
                placeholder="entity-id"
                @input="handleFieldChange(draft.id, 'source_id', $event)"
              />
            </el-form-item>
            <el-form-item label="Target Entity ID">
              <el-input
                :model-value="draft.target_id"
                placeholder="entity-id"
                @input="handleFieldChange(draft.id, 'target_id', $event)"
              />
            </el-form-item>
            <el-form-item label="Relation Type">
              <el-input
                :model-value="draft.type"
                placeholder="OWNS"
                @input="handleFieldChange(draft.id, 'type', $event)"
              />
            </el-form-item>
            <el-form-item label="Properties JSON">
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
.relation-composer__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.relation-card {
  margin-bottom: 16px;
}
.relation-card__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.hint {
  color: var(--el-text-color-secondary);
}
</style>
