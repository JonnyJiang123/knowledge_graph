<script setup lang="ts">
import { computed, reactive, ref } from 'vue'
import type { GraphProject, GraphProjectCreatePayload } from '@/types/graph'

const props = defineProps<{
  modelValue: string
  projects: GraphProject[]
  loading?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'create', payload: GraphProjectCreatePayload): void
}>()

const dialogVisible = ref(false)
const form = reactive<GraphProjectCreatePayload>({
  name: '',
  industry: 'FINANCE',
  description: '',
  metadata: {},
})

const hasProjects = computed(() => props.projects.length > 0)

function handleSelect(value: string) {
  emit('update:modelValue', value)
}

function openDialog() {
  dialogVisible.value = true
}

function resetForm() {
  form.name = ''
  form.industry = 'FINANCE'
  form.description = ''
  form.metadata = {}
}

function submitForm() {
  emit('create', { ...form })
  dialogVisible.value = false
  resetForm()
}
</script>

<template>
  <section class="graph-project-selector">
    <el-form label-width="120px" class="project-form">
      <el-form-item label="图谱项目">
        <el-select
          v-model="props.modelValue"
          placeholder="选择现有项目"
          class="selector"
          :loading="props.loading"
          :disabled="!hasProjects"
          @change="handleSelect"
        >
          <el-option
            v-for="project in props.projects"
            :key="project.id"
            :label="`${project.name} (${project.industry})`"
            :value="project.id"
          />
        </el-select>
        <el-button type="primary" @click="openDialog">
          {{ hasProjects ? '新建图谱项目' : '创建首个图谱项目' }}
        </el-button>
      </el-form-item>
    </el-form>

    <el-dialog v-model="dialogVisible" title="新建图谱项目" width="480px">
      <el-form label-width="120px">
        <el-form-item label="名称">
          <el-input v-model="form.name" placeholder="知识图谱 V1" />
        </el-form-item>
        <el-form-item label="行业">
          <el-select v-model="form.industry">
            <el-option label="金融" value="FINANCE" />
            <el-option label="医疗" value="HEALTHCARE" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :disabled="!form.name" @click="submitForm">
          创建
        </el-button>
      </template>
    </el-dialog>
  </section>
</template>

<style scoped>
.graph-project-selector {
  display: flex;
  flex-direction: column;
  gap: 16px;
}
.project-form {
  max-width: 640px;
}
.selector {
  width: 320px;
  margin-right: 12px;
}
</style>
