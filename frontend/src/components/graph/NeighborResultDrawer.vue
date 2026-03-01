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
    title="邻居查询结果"
    size="50%"
    @close="handleClose"
  >
    <template v-if="props.run">
      <el-descriptions :column="2" border>
        <el-descriptions-item label="实体ID">
          {{ props.run.entityId }}
        </el-descriptions-item>
        <el-descriptions-item label="深度">
          {{ props.run.depth }}
        </el-descriptions-item>
        <el-descriptions-item label="限制">
          {{ props.run.limit ?? '无限制' }}
        </el-descriptions-item>
        <el-descriptions-item label="节点">
          {{ props.run.result.entities?.length ?? 0 }}
        </el-descriptions-item>
        <el-descriptions-item label="关系">
          {{ props.run.result.relations?.length ?? 0 }}
        </el-descriptions-item>
        <el-descriptions-item label="时间戳">
          {{ new Date(props.run.createdAt).toLocaleString() }}
        </el-descriptions-item>
      </el-descriptions>

      <section class="result-section">
        <h4>实体 ({{ props.run.result.entities?.length ?? 0 }})</h4>
        <el-empty v-if="!props.run.result.entities?.length" description="未找到实体" />
        <el-table v-else :data="props.run.result.entities" size="small" height="200">
          <el-table-column prop="id" label="ID" width="160" />
          <el-table-column prop="type" label="类型" width="120" />
          <el-table-column prop="labels" label="标签" />
        </el-table>
      </section>
      <section class="result-section">
        <h4>关系 ({{ props.run.result.relations?.length ?? 0 }})</h4>
        <el-empty v-if="!props.run.result.relations?.length" description="未找到关系" />
        <el-table v-else :data="props.run.result.relations" size="small" height="200">
          <el-table-column prop="id" label="ID" width="160" />
          <el-table-column prop="type" label="类型" width="120" />
          <el-table-column prop="source_id" label="源" width="160" />
          <el-table-column prop="target_id" label="目标" width="160" />
        </el-table>
      </section>
    </template>
    <el-empty v-else description="选择邻居查询运行" />
  </el-drawer>
</template>

<style scoped>
.result-section {
  margin-top: 16px;
}
</style>
