<template>
  <div class="data-preview">
    <el-tabs v-model="activeTab">
      <el-tab-pane label="数据预览" name="preview">
        <el-table :data="previewData" height="300" v-loading="loading">
          <el-table-column
            v-for="col in columns"
            :key="col"
            :prop="col"
            :label="col"
            show-overflow-tooltip
          />
        </el-table>
      </el-tab-pane>

      <el-tab-pane label="列信息" name="columns">
        <el-descriptions :column="1" border>
          <el-descriptions-item
            v-for="col in columnInfo"
            :key="col.name"
            :label="col.name"
          >
            类型: {{ col.type }} | 空值: {{ col.nullable ? '允许' : '不允许' }}
          </el-descriptions-item>
        </el-descriptions>
      </el-tab-pane>

      <el-tab-pane label="统计信息" name="stats">
        <el-statistic
          v-for="stat in statistics"
          :key="stat.label"
          :title="stat.label"
          :value="stat.value"
          class="stat-item"
        />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'

const props = defineProps<{
  sourceId: string
}>()

const activeTab = ref('preview')
const loading = ref(false)
const previewData = ref<any[]>([])
const columns = ref<string[]>([])
const columnInfo = ref<any[]>([])
const statistics = ref<any[]>([])

// 模拟加载数据
const loadPreview = async () => {
  loading.value = true
  try {
    // 调用API获取预览数据
    previewData.value = [
      { id: 1, name: '示例1', value: 100 },
      { id: 2, name: '示例2', value: 200 }
    ]
    columns.value = ['id', 'name', 'value']
    columnInfo.value = [
      { name: 'id', type: 'INTEGER', nullable: false },
      { name: 'name', type: 'VARCHAR', nullable: false },
      { name: 'value', type: 'DECIMAL', nullable: true }
    ]
    statistics.value = [
      { label: '总行数', value: 10000 },
      { label: '列数', value: 3 },
      { label: '文件大小', value: '2.5 MB' }
    ]
  } finally {
    loading.value = false
  }
}

watch(() => props.sourceId, loadPreview, { immediate: true })
</script>

<style scoped>
.data-preview {
  padding: 16px;
}
.stat-item {
  margin: 16px 0;
}
</style>
