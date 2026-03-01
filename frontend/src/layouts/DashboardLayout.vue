<template>
  <el-container class="dashboard-layout">
    <el-aside width="220px" class="sidebar">
      <div class="logo">
        <h3>知识图谱平台</h3>
      </div>

      <el-menu
        :default-active="route.path"
        router
        class="menu"
        background-color="#304156"
        text-color="#bfcbd9"
        active-text-color="#409EFF"
      >
        <el-menu-item index="/dashboard">
          <el-icon><HomeFilled /></el-icon>
          <span>仪表板</span>
        </el-menu-item>

        <el-sub-menu index="/graph">
          <template #title>
            <el-icon><Share /></el-icon>
            <span>知识图谱</span>
          </template>
          <el-menu-item index="/graph/builder">图谱构建</el-menu-item>
          <el-menu-item index="/graph/visualization">图谱可视化</el-menu-item>
          <el-menu-item index="/graph/jobs">任务管理</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="/extraction">
          <template #title>
            <el-icon><DataLine /></el-icon>
            <span>数据摄取</span>
          </template>
          <el-menu-item index="/extraction/wizard">摄取向导</el-menu-item>
          <el-menu-item index="/extraction/manager">抽取管理</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="/query">
          <template #title>
            <el-icon><Search /></el-icon>
            <span>查询分析</span>
          </template>
          <el-menu-item index="/query/builder">查询构建</el-menu-item>
          <el-menu-item index="/query/natural">自然语言查询</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="/industry">
          <template #title>
            <el-icon><OfficeBuilding /></el-icon>
            <span>行业应用</span>
          </template>
          <el-menu-item index="/finance/enterprises">金融分析</el-menu-item>
          <el-menu-item index="/healthcare/diagnosis">医疗诊断</el-menu-item>
        </el-sub-menu>

        <el-sub-menu index="/system">
          <template #title>
            <el-icon><Setting /></el-icon>
            <span>系统管理</span>
          </template>
          <el-menu-item index="/system/jobs">任务监控</el-menu-item>
          <el-menu-item index="/system/logs">系统日志</el-menu-item>
          <el-menu-item index="/system/settings">系统设置</el-menu-item>
        </el-sub-menu>
      </el-menu>
    </el-aside>

    <el-container>
      <el-header class="header">
        <div class="header-left">
          <breadcrumb />
        </div>
        <div class="header-right">
          <el-badge :value="unreadCount" class="notification-badge">
            <el-icon size="20"><Bell /></el-icon>
          </el-badge>
          <el-dropdown>
            <span class="user-info">
              <el-avatar :size="32" :src="userAvatar" />
              <span>{{ userName }}</span>
              <el-icon><ArrowDown /></el-icon>
            </span>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item>个人中心</el-dropdown-item>
                <el-dropdown-item>系统设置</el-dropdown-item>
                <el-dropdown-item divided @click="logout">退出登录</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </el-header>

      <el-main class="main">
        <router-view />
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import {
  HomeFilled,
  Share,
  DataLine,
  Search,
  OfficeBuilding,
  Setting,
  Bell,
  ArrowDown
} from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

const userName = computed(() => authStore.user?.username || '用户')
const userAvatar = computed(() => (authStore.user as any)?.avatar || '')
const unreadCount = computed(() => 5)

const logout = () => {
  authStore.logout()
  router.push('/login')
}
</script>

<style scoped>
.dashboard-layout {
  height: 100vh;
}
.sidebar {
  background-color: #304156;
}
.logo {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  border-bottom: 1px solid #1f2d3d;
}
.logo h3 {
  margin: 0;
}
.menu {
  border-right: none;
}
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: white;
  box-shadow: 0 1px 4px rgba(0, 0, 0, 0.08);
}
.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}
.notification-badge {
  cursor: pointer;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}
.main {
  background-color: #f0f2f5;
  padding: 20px;
  overflow-y: auto;
}
</style>
