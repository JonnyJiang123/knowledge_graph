<template>
  <div class="file-uploader">
    <el-upload
      drag
      action="/api/upload"
      :on-preview="handlePreview"
      :on-remove="handleRemove"
      :on-success="handleSuccess"
      :on-error="handleError"
      :before-upload="beforeUpload"
      :file-list="fileList"
      :accept="accept"
      :multiple="multiple"
    >
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">
        将文件拖到此处，或<em>点击上传</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          支持 {{ accept }} 格式文件，单个文件不超过 {{ maxSize }}MB
        </div>
      </template>
    </el-upload>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { UploadFilled } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'

const props = defineProps<{
  accept?: string
  multiple?: boolean
  maxSize?: number  // MB
}>()

const emit = defineEmits<{
  success: [response: any, file: any]
  error: [error: any, file: any]
  remove: [file: any]
}>()

const fileList = ref<any[]>([])

const beforeUpload = (file: File) => {
  const maxSize = (props.maxSize || 10) * 1024 * 1024
  if (file.size > maxSize) {
    ElMessage.error(`文件大小不能超过 ${props.maxSize || 10}MB`)
    return false
  }
  return true
}

const handlePreview = (file: any) => {
  console.log('preview', file)
}

const handleRemove = (file: any) => {
  emit('remove', file)
}

const handleSuccess = (response: any, file: any) => {
  ElMessage.success('上传成功')
  emit('success', response, file)
}

const handleError = (error: any, file: any) => {
  ElMessage.error('上传失败')
  emit('error', error, file)
}
</script>

<style scoped>
.file-uploader {
  padding: 20px;
}
</style>
