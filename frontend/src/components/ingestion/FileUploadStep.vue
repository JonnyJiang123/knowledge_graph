<script setup lang="ts">
import { ref, computed } from 'vue'
import { UploadFilled, Document } from '@element-plus/icons-vue'
import type { UploadFile, UploadUserFile } from 'element-plus'
import type { FileFormat } from '@/types/ingestion'

const props = defineProps<{
  loading?: boolean
}>()

const emit = defineEmits<{
  fileSelected: [file: File]
}>()

const selectedFile = ref<File | null>(null)
const fileList = ref<UploadUserFile[]>([])

// 支持的文件格式
const acceptedFormats = '.csv,.xlsx,.txt,.pdf,.docx'

// 文件格式映射
const formatMap: Record<string, FileFormat> = {
  csv: 'CSV',
  xlsx: 'XLSX',
  txt: 'TXT',
  pdf: 'PDF',
  docx: 'DOCX',
}

const detectedFormat = computed<FileFormat | null>(() => {
  if (!selectedFile.value) return null
  const ext = selectedFile.value.name.split('.').pop()?.toLowerCase()
  return ext ? formatMap[ext] ?? null : null
})

const fileSizeDisplay = computed(() => {
  if (!selectedFile.value) return ''
  const bytes = selectedFile.value.size
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(2)} MB`
})

function handleChange(uploadFile: UploadFile) {
  if (uploadFile.raw) {
    selectedFile.value = uploadFile.raw
    emit('fileSelected', uploadFile.raw)
  }
}

function handleRemove() {
  selectedFile.value = null
  fileList.value = []
}

function beforeUpload(file: File) {
  // 检查文件大小限制 100MB
  const isLt100M = file.size / 1024 / 1024 < 100
  if (!isLt100M) {
    return false
  }
  return true
}

defineExpose({ selectedFile, detectedFormat })
</script>

<template>
  <div class="file-upload-step">
    <el-upload
      v-model:file-list="fileList"
      drag
      :auto-upload="false"
      :limit="1"
      :accept="acceptedFormats"
      :before-upload="beforeUpload"
      :on-change="handleChange"
      :on-remove="handleRemove"
      :disabled="loading"
    >
      <el-icon class="el-icon--upload"><UploadFilled /></el-icon>
      <div class="el-upload__text">
        拖拽文件到此处，或 <em>点击上传</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          支持 CSV、Excel (.xlsx)、TXT、PDF、Word (.docx) 格式，最大 100MB
        </div>
      </template>
    </el-upload>

    <!-- 文件信息展示 -->
    <div v-if="selectedFile" class="file-info">
      <el-card shadow="never">
        <template #header>
          <div class="file-info-header">
            <el-icon><Document /></el-icon>
            <span>{{ selectedFile.name }}</span>
          </div>
        </template>
        <el-descriptions :column="2" size="small">
          <el-descriptions-item label="文件大小">
            {{ fileSizeDisplay }}
          </el-descriptions-item>
          <el-descriptions-item label="文件格式">
            <el-tag size="small">{{ detectedFormat }}</el-tag>
          </el-descriptions-item>
        </el-descriptions>
      </el-card>
    </div>
  </div>
</template>

<style scoped lang="scss">
.file-upload-step {
  .file-info {
    margin-top: 20px;

    .file-info-header {
      display: flex;
      align-items: center;
      gap: 8px;
    }
  }
}
</style>
