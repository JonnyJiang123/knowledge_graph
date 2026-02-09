<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'
import { useProjectStore } from '@/stores/project'
import type { ProjectUpdate } from '@/types'

const route = useRoute()
const router = useRouter()
const projectStore = useProjectStore()

const editing = ref(false)
const formData = ref<ProjectUpdate>({})

const projectId = computed(() => route.params.id as string)

onMounted(async () => {
  await projectStore.fetchProject(projectId.value)
  if (projectStore.currentProject) {
    formData.value = {
      name: projectStore.currentProject.name,
      description: projectStore.currentProject.description || '',
      industry: projectStore.currentProject.industry,
    }
  }
})

function startEdit() {
  if (projectStore.currentProject) {
    formData.value = {
      name: projectStore.currentProject.name,
      description: projectStore.currentProject.description || '',
      industry: projectStore.currentProject.industry,
    }
    editing.value = true
  }
}

function cancelEdit() {
  editing.value = false
}

async function saveEdit() {
  try {
    await projectStore.updateProject(projectId.value, formData.value)
    ElMessage.success('项目更新成功')
    editing.value = false
  } catch {
    ElMessage.error('更新项目失败')
  }
}
</script>

<template>
  <div class="project-detail">
    <div class="header">
      <el-button :icon="ArrowLeft" @click="router.push('/projects')">
        返回列表
      </el-button>
      <h2>项目详情</h2>
    </div>

    <el-card v-loading="projectStore.loading">
      <template v-if="!editing">
        <el-descriptions :column="2" border>
          <el-descriptions-item label="项目名称">
            {{ projectStore.currentProject?.name }}
          </el-descriptions-item>
          <el-descriptions-item label="行业">
            <el-tag :type="projectStore.currentProject?.industry === 'FINANCE' ? 'primary' : 'success'">
              {{ projectStore.currentProject?.industry === 'FINANCE' ? '金融' : '医疗' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="描述" :span="2">
            {{ projectStore.currentProject?.description || '暂无描述' }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ projectStore.currentProject?.created_at
               ? new Date(projectStore.currentProject.created_at).toLocaleString()
               : '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">
            {{ projectStore.currentProject?.updated_at
               ? new Date(projectStore.currentProject.updated_at).toLocaleString()
               : '-' }}
          </el-descriptions-item>
        </el-descriptions>
        <div class="actions">
          <el-button type="primary" @click="startEdit">编辑项目</el-button>
        </div>
      </template>

      <template v-else>
        <el-form :model="formData" label-width="80px">
          <el-form-item label="项目名称">
            <el-input v-model="formData.name" />
          </el-form-item>
          <el-form-item label="行业">
            <el-select v-model="formData.industry">
              <el-option label="金融" value="FINANCE" />
              <el-option label="医疗" value="HEALTHCARE" />
            </el-select>
          </el-form-item>
          <el-form-item label="描述">
            <el-input v-model="formData.description" type="textarea" :rows="3" />
          </el-form-item>
        </el-form>
        <div class="actions">
          <el-button @click="cancelEdit">取消</el-button>
          <el-button type="primary" @click="saveEdit">保存</el-button>
        </div>
      </template>
    </el-card>
  </div>
</template>

<style scoped lang="scss">
.project-detail {
  padding: 20px;

  .header {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 20px;

    h2 {
      margin: 0;
    }
  }

  .actions {
    margin-top: 20px;
    text-align: right;
  }
}
</style>
