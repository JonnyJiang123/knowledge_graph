<script setup lang="ts">
import { onMounted } from 'vue'
import { useProjectStore } from '@/stores/project'
import { useAuthStore } from '@/stores/auth'

const projectStore = useProjectStore()
const authStore = useAuthStore()

onMounted(() => {
  projectStore.fetchProjects()
})
</script>

<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>项目统计</span>
          </template>
          <div class="stat-value">{{ projectStore.projects.length }}</div>
          <div class="stat-label">我的项目数</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>账户信息</span>
          </template>
          <div class="stat-value">{{ authStore.user?.username }}</div>
          <div class="stat-label">{{ authStore.user?.email }}</div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card>
          <template #header>
            <span>快速操作</span>
          </template>
          <el-button type="primary" @click="$router.push('/projects')">
            管理项目
          </el-button>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped lang="scss">
.dashboard {
  padding: 20px;
}

.stat-value {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
}

.stat-label {
  color: #999;
  margin-top: 8px;
}
</style>
