<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  data: Array<Record<string, unknown>> | null
  loading?: boolean
}>()

// 从数据中提取列名
const columns = computed(() => {
  if (!props.data || props.data.length === 0) return []
  const firstRow = props.data[0]
  return firstRow ? Object.keys(firstRow) : []
})

// 格式化单元格值
function formatCell(value: unknown): string {
  if (value === null || value === undefined) return '-'
  if (typeof value === 'object') return JSON.stringify(value)
  return String(value)
}

// 判断是否为空值（用于样式标记）
function isEmptyValue(value: unknown): boolean {
  return value === null || value === undefined || value === ''
}
</script>

<template>
  <div class="preview-table">
    <template v-if="loading">
      <el-skeleton :rows="5" animated />
    </template>

    <template v-else-if="data && data.length > 0">
      <el-table
        :data="data"
        stripe
        border
        size="small"
        max-height="400"
        style="width: 100%"
      >
        <el-table-column type="index" label="#" width="50" fixed="left" />
        <el-table-column
          v-for="col in columns"
          :key="col"
          :prop="col"
          :label="col"
          min-width="120"
          show-overflow-tooltip
        >
          <template #default="{ row }">
            <span :class="{ 'empty-cell': isEmptyValue(row[col]) }">
              {{ formatCell(row[col]) }}
            </span>
          </template>
        </el-table-column>
      </el-table>

      <div class="preview-footer">
        <el-text type="info" size="small">
          显示前 {{ data.length }} 行预览数据
        </el-text>
      </div>
    </template>

    <template v-else>
      <el-empty description="暂无预览数据" />
    </template>
  </div>
</template>

<style scoped lang="scss">
.preview-table {
  .empty-cell {
    color: var(--el-text-color-placeholder);
    font-style: italic;
  }

  .preview-footer {
    margin-top: 12px;
    text-align: right;
  }
}
</style>
