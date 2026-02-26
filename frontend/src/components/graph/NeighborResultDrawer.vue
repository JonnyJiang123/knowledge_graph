<script setup lang="ts">
import type { NeighborRun } from '@/types/graph'

const props = defineProps<{
  modelValue: boolean
  run: NeighborRun | null
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
}>()

const handleClose = () => emit('update:modelValue', false)
</script>

<template>
  <el-drawer
    v-model="props.modelValue"
    title="Neighbor result"
    size="50%"
    @close="handleClose"
  >
    <template v-if="props.run">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="Entity ID">
          {{ props.run.entityId }}
        </el-descriptions-item>
        <el-descriptions-item label="Depth">
          {{ props.run.depth }}
        </el-descriptions-item>
        <el-descriptions-item label="Limit">
          {{ props.run.limit ?? 'Unlimited' }}
        </el-descriptions-item>
        <el-descriptions-item label="Nodes">
          {{ props.run.result.entities?.length ?? 0 }}
        </el-descriptions-item>
        <el-descriptions-item label="Relations">
          {{ props.run.result.relations?.length ?? 0 }}
        </el-descriptions-item>
        <el-descriptions-item label="Timestamp">
          {{ new Date(props.run.createdAt).toLocaleString() }}
        </el-descriptions-item>
      </el-descriptions>

      <section class="result-section">
        <h4>Entities ({{ props.run.result.entities?.length ?? 0 }})</h4>
        <el-empty v-if="!props.run.result.entities?.length" description="No entities found" />
        <el-table v-else :data="props.run.result.entities" size="small" height="200">
          <el-table-column prop="id" label="ID" width="160" />
          <el-table-column prop="type" label="Type" width="120" />
          <el-table-column prop="labels" label="Labels" />
        </el-table>
      </section>
      <section class="result-section">
        <h4>Relations ({{ props.run.result.relations?.length ?? 0 }})</h4>
        <el-empty v-if="!props.run.result.relations?.length" description="No relations found" />
        <el-table v-else :data="props.run.result.relations" size="small" height="200">
          <el-table-column prop="id" label="ID" width="160" />
          <el-table-column prop="type" label="Type" width="120" />
          <el-table-column prop="source_id" label="Source" width="160" />
          <el-table-column prop="target_id" label="Target" width="160" />
        </el-table>
      </section>
    </template>
    <el-empty v-else description="Select a neighbor run" />
  </el-drawer>
</template>

<style scoped>
.result-section {
  margin-top: 16px;
}
</style>
