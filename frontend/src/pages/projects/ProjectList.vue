<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Edit, Delete } from '@element-plus/icons-vue'
import { useProjectStore } from '@/stores/project'
import type { ProjectCreate } from '@/types'

const router = useRouter()
const projectStore = useProjectStore()

const dialogVisible = ref(false)
const formData = ref<ProjectCreate>({
  name: '',
  description: '',
  industry: 'FINANCE',
})

onMounted(() => {
  projectStore.fetchProjects()
})

function openCreateDialog() {
  formData.value = {
    name: '',
    description: '',
    industry: 'FINANCE',
  }
  dialogVisible.value = true
}

async function handleCreate() {
  try {
    const project = await projectStore.createProject(formData.value)
    ElMessage.success('项目创建成功')
    dialogVisible.value = false
    router.push(`/projects/${project.id}`)
  } catch {
    ElMessage.error('创建项目失败')
  }
}

async function handleDelete(id: string, name: string) {
  try {
    await ElMessageBox.confirm(
      `确定要删除项目「${name}」吗？`,
      '删除确认',
      { type: 'warning' }
    )
    await projectStore.deleteProject(id)
    ElMessage.success('项目已删除')
  } catch {
    // 用户取消或删除失败
  }
}
</script>

<template>
  <div class="project-list">
    <div class="header">
      <h2>项目管理</h2>
      <el-button type="primary" :icon="Plus" @click="openCreateDialog">
        新建项目
      </el-button>
    </div>

    <el-table :data="projectStore.projects" v-loading="projectStore.loading">
      <el-table-column prop="name" label="项目名称" />
      <el-table-column prop="industry" label="行业" width="120">
        <template #default="{ row }">
          <el-tag :type="row.industry === 'FINANCE' ? 'primary' : 'success'">
            {{ row.industry === 'FINANCE' ? '金融' : '医疗' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="description" label="描述" />
      <el-table-column prop="created_at" label="创建时间" width="180">
        <template #default="{ row }">
          {{ row.created_at ? new Date(row.created_at).toLocaleString() : '-' }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="180">
        <template #default="{ row }">
          <el-button
            type="primary"
            :icon="Edit"
            size="small"
            @click="router.push(`/projects/${row.id}`)"
          >
            编辑
          </el-button>
          <el-button
            type="danger"
            :icon="Delete"
            size="small"
            @click="handleDelete(row.id, row.name)"
          >
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 新建项目对话框 -->
    <el-dialog v-model="dialogVisible" title="新建项目" width="500px">
      <el-form :model="formData" label-width="80px">
        <el-form-item label="项目名称">
          <el-input v-model="formData.name" placeholder="请输入项目名称" />
        </el-form-item>
        <el-form-item label="行业">
          <el-select v-model="formData.industry">
            <el-option label="金融" value="FINANCE" />
            <el-option label="医疗" value="HEALTHCARE" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input
            v-model="formData.description"
            type="textarea"
            :rows="3"
            placeholder="请输入项目描述"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreate">创建</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped lang="scss">
.project-list {
  padding: 20px;

  .header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 20px;

    h2 {
      margin: 0;
    }
  }
}
</style>
