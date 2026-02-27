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
        <h3>Entities</h3>
        <p class="hint">Define nodes you want to merge into the graph.</p>
      </div>
      <el-button type="primary" @click="emit('add')">Add entity</el-button>
    </header>

    <el-empty v-if="!drafts.length" description="No entities added yet" />

    <el-row v-else :gutter="12">
      <el-col v-for="draft in drafts" :key="draft.id" :xs="24" :md="12">
        <el-card class="entity-card" shadow="hover">
          <template #header>
            <div class="entity-card__header">
              <span>{{ draft.external_id || 'New Entity' }}</span>
              <el-space>
                <el-tag v-if="draft.status === 'saved'" type="success" size="small">saved</el-tag>
                <el-button
                  link
                  type="primary"
                  size="small"
                  @click="emit('persist', draft.id)"
                >
                  Persist
                </el-button>
                <el-button
                  link
                  type="danger"
                  size="small"
                  @click="emit('remove', draft.id)"
                >
                  Remove
                </el-button>
              </el-space>
            </div>
          </template>

          <el-form label-width="120px" class="entity-form">
            <el-form-item label="External ID">
              <el-input
                :model-value="draft.external_id"
                placeholder="company-123"
                @input="handleFieldChange(draft.id, 'external_id', $event)"
              />
            </el-form-item>
            <el-form-item label="Type">
              <el-input
                :model-value="draft.type"
                placeholder="ENTERPRISE"
                @input="handleFieldChange(draft.id, 'type', $event)"
              />
            </el-form-item>
            <el-form-item label="Labels">
              <el-select
                :model-value="draft.labels"
                multiple
                placeholder="Add labels"
                @change="handleFieldChange(draft.id, 'labels', $event)"
              >
                <el-option label="Enterprise" value="Enterprise" />
                <el-option label="Account" value="Account" />
                <el-option label="Person" value="Person" />
              </el-select>
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
