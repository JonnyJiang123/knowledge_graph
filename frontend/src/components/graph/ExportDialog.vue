<script setup lang="ts">
import { ref, computed } from 'vue'
import { Download, Picture, Document } from '@element-plus/icons-vue'
import type { GraphData } from '@/types/graph'

const props = defineProps<{
  modelValue: boolean
  data: GraphData | null
  chartInstance?: any
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'export', type: 'png' | 'json', options: ExportOptions): void
}>()

export interface ExportOptions {
  filename: string
  includeMetadata: boolean
  width?: number
  height?: number
  backgroundColor: string
}

const activeTab = ref<'png' | 'json'>('png')
const filename = ref('knowledge-graph')
const includeMetadata = ref(true)
const backgroundColor = ref('#ffffff')
const customSize = ref(false)
const width = ref(1920)
const height = ref(1080)

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

function handleExport() {
  const options: ExportOptions = {
    filename: filename.value,
    includeMetadata: includeMetadata.value,
    backgroundColor: backgroundColor.value,
  }

  if (customSize.value && activeTab.value === 'png') {
    options.width = width.value
    options.height = height.value
  }

  if (activeTab.value === 'png') {
    exportAsPng(options)
  } else {
    exportAsJson(options)
  }

  emit('export', activeTab.value, options)
  visible.value = false
}

function exportAsPng(options: ExportOptions) {
  if (!props.chartInstance) return

  const url = props.chartInstance.getDataURL({
    type: 'png',
    pixelRatio: 2,
    backgroundColor: options.backgroundColor,
  })

  downloadFile(url, `${options.filename}.png`)
}

function exportAsJson(options: ExportOptions) {
  if (!props.data) return

  const exportData = options.includeMetadata
    ? {
        metadata: {
          exportedAt: new Date().toISOString(),
          nodeCount: props.data.nodes.length,
          edgeCount: props.data.edges.length,
        },
        data: props.data,
      }
    : props.data

  const blob = new Blob([JSON.stringify(exportData, null, 2)], {
    type: 'application/json',
  })
  const url = URL.createObjectURL(blob)
  downloadFile(url, `${options.filename}.json`)
  URL.revokeObjectURL(url)
}

function downloadFile(url: string, filename: string) {
  const link = document.createElement('a')
  link.download = filename
  link.href = url
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
}
</script>

<template>
  <el-dialog
    v-model="visible"
    title="导出图谱"
    width="500px"
  >
    <el-tabs v-model="activeTab">
      <!-- PNG 导出 -->
      <el-tab-pane name="png">
        <template #label>
          <el-icon><Picture /></el-icon>
          PNG 图片
        </template>
        <div class="export-options">
          <el-form label-width="100px">
            <el-form-item label="文件名">
              <el-input v-model="filename" placeholder="knowledge-graph">
                <template #append>.png</template>
              </el-input>
            </el-form-item>
            <el-form-item label="背景颜色">
              <el-color-picker v-model="backgroundColor" show-alpha />
            </el-form-item>
            <el-form-item label="自定义尺寸">
              <el-switch v-model="customSize" />
            </el-form-item>
            <template v-if="customSize">
              <el-form-item label="宽度">
                <el-input-number v-model="width" :min="100" :max="7680" />
              </el-form-item>
              <el-form-item label="高度">
                <el-input-number v-model="height" :min="100" :max="4320" />
              </el-form-item>
            </template>
          </el-form>
        </div>
      </el-tab-pane>

      <!-- JSON 导出 -->
      <el-tab-pane name="json">
        <template #label>
          <el-icon><Document /></el-icon>
          JSON 数据
        </template>
        <div class="export-options">
          <el-form label-width="100px">
            <el-form-item label="文件名">
              <el-input v-model="filename" placeholder="knowledge-graph">
                <template #append>.json</template>
              </el-input>
            </el-form-item>
            <el-form-item label="包含元数据">
              <el-switch v-model="includeMetadata" />
            </el-form-item>
          </el-form>
          <div class="json-preview">
            <div class="preview-label">预览:</div>
            <pre class="preview-code">{{ JSON.stringify({
              metadata: includeMetadata ? {
                exportedAt: new Date().toISOString(),
                nodeCount: data?.nodes.length ?? 0,
                edgeCount: data?.edges.length ?? 0,
              } : undefined,
              data: { nodes: '...', edges: '...', categories: '...' }
            }, null, 2) }}</pre>
          </div>
        </div>
      </el-tab-pane>
    </el-tabs>

    <template #footer>
      <el-button @click="visible = false">取消</el-button>
      <el-button type="primary" @click="handleExport">
        <el-icon><Download /></el-icon>
        导出
      </el-button>
    </template>
  </el-dialog>
</template>

<style scoped>
.export-options {
  padding: 16px 0;
}

.json-preview {
  margin-top: 16px;
  padding: 12px;
  background: var(--el-fill-color-light);
  border-radius: 4px;
}

.preview-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-bottom: 8px;
}

.preview-code {
  margin: 0;
  font-family: 'Fira Code', 'Monaco', 'Consolas', monospace;
  font-size: 12px;
  color: var(--el-text-color-regular);
  overflow-x: auto;
}
</style>
