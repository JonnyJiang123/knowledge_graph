<script setup lang="ts">
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import {
  House,
  Folder,
  Setting,
  SwitchButton,
  Upload,
  List,
} from '@element-plus/icons-vue'

const router = useRouter()
const authStore = useAuthStore()

function handleLogout() {
  authStore.logout()
  router.push('/login')
}
</script>

<template>
  <el-container class="layout-container">
    <!-- 侧边栏 -->
    <el-aside width="200px" class="layout-aside">
      <div class="logo">
        <h3>知识图谱</h3>
      </div>
      <el-menu
        :default-active="$route.path"
        router
        background-color="#001529"
        text-color="#fff"
        active-text-color="#409eff"
      >
        <el-menu-item index="/">
          <el-icon><House /></el-icon>
          <span>首页</span>
        </el-menu-item>
        <el-menu-item index="/projects">
          <el-icon><Folder /></el-icon>
          <span>项目管理</span>
        </el-menu-item>
        <el-sub-menu index="/ingestion">
          <template #title>
            <el-icon><Upload /></el-icon>
            <span>数据导入</span>
          </template>
          <el-menu-item index="/ingestion/wizard">
            <el-icon><Upload /></el-icon>
            <span>导入向导</span>
          </el-menu-item>
          <el-menu-item index="/ingestion/jobs">
            <el-icon><List /></el-icon>
            <span>任务列表</span>
          </el-menu-item>
        </el-sub-menu>
        <el-menu-item index="/settings" v-if="authStore.isSuperuser">
          <el-icon><Setting /></el-icon>
          <span>系统设置</span>
        </el-menu-item>
      </el-menu>
    </el-aside>

    <el-container>
      <!-- 顶部导航 -->
      <el-header class="layout-header">
        <div class="header-content">
          <span>欢迎，{{ authStore.user?.username }}</span>
          <el-button
            type="danger"
            :icon="SwitchButton"
            @click="handleLogout"
          >
            退出登录
          </el-button>
        </div>
      </el-header>

      <!-- 主内容区 -->
      <el-main class="layout-main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<style scoped lang="scss">
.layout-container {
  min-height: 100vh;
}

.layout-aside {
  background-color: #001529;

  .logo {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;

    h3 {
      margin: 0;
    }
  }
}

.layout-header {
  background: #fff;
  border-bottom: 1px solid #eee;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  padding: 0 20px;

  .header-content {
    display: flex;
    align-items: center;
    gap: 16px;
  }
}

.layout-main {
  background: #f5f7fa;
}
</style>
