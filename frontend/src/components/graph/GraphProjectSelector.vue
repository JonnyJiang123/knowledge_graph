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
      <el-form-item label="Graph Project">
        <el-select
          v-model="props.modelValue"
          placeholder="Select an existing project"
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
          {{ hasProjects ? 'New graph project' : 'Create first graph project' }}
        </el-button>
      </el-form-item>
    </el-form>

    <el-dialog v-model="dialogVisible" title="New Graph Project" width="480px">
      <el-form label-width="120px">
        <el-form-item label="Name">
          <el-input v-model="form.name" placeholder="Knowledge Graph V1" />
        </el-form-item>
        <el-form-item label="Industry">
          <el-select v-model="form.industry">
            <el-option label="Finance" value="FINANCE" />
            <el-option label="Healthcare" value="HEALTHCARE" />
          </el-select>
        </el-form-item>
        <el-form-item label="Description">
          <el-input v-model="form.description" type="textarea" rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">Cancel</el-button>
        <el-button type="primary" :disabled="!form.name" @click="submitForm">
          Create
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
