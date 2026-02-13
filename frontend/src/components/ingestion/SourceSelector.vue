<script setup lang="ts">
import { computed } from 'vue'
import type { DataSourceType, DataSource } from '@/types/ingestion'
import { Upload, Coin } from '@element-plus/icons-vue'

const props = defineProps<{
  modelValue: DataSourceType
  sources: DataSource[]
  selectedSourceId?: string
}>()

const emit = defineEmits<{
  'update:modelValue': [value: DataSourceType]
  'update:selectedSourceId': [value: string | undefined]
}>()

const sourceType = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

const selectedSource = computed({
  get: () => props.selectedSourceId,
  set: (val) => emit('update:selectedSourceId', val),
})

// 筛选 MYSQL 类型的已保存数据源
const mysqlSources = computed(() =>
  props.sources.filter((s) => s.type === 'MYSQL' && s.status === 'ACTIVE'),
)
</script>

<template>
  <div class="source-selector">
    <el-form label-position="top">
      <el-form-item label="选择数据源类型">
        <el-radio-group v-model="sourceType" size="large">
          <el-radio-button value="FILE">
            <el-icon><Upload /></el-icon>
            <span style="margin-left: 4px">文件上传</span>
          </el-radio-button>
          <el-radio-button value="MYSQL">
            <el-icon><Coin /></el-icon>
            <span style="margin-left: 4px">MySQL 数据库</span>
          </el-radio-button>
        </el-radio-group>
      </el-form-item>

      <!-- MySQL 已保存数据源列表 -->
      <el-form-item
        v-if="sourceType === 'MYSQL' && mysqlSources.length > 0"
        label="选择已保存的数据源（可选）"
      >
        <el-select
          v-model="selectedSource"
          placeholder="选择已保存的连接，或填写新连接"
          clearable
          style="width: 100%"
        >
          <el-option
            v-for="src in mysqlSources"
            :key="src.id"
            :label="src.name"
            :value="src.id"
          />
        </el-select>
      </el-form-item>

      <div class="source-hint">
        <template v-if="sourceType === 'FILE'">
          <el-text type="info">
            支持 CSV、Excel (.xlsx)、TXT、PDF、Word 文件
          </el-text>
        </template>
        <template v-else>
          <el-text type="info">
            连接 MySQL 数据库导入表数据
          </el-text>
        </template>
      </div>
    </el-form>
  </div>
</template>

<style scoped lang="scss">
.source-selector {
  .source-hint {
    margin-top: 16px;
  }
}
</style>
