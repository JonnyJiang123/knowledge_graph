<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const form = ref({
  username: '',
  password: '',
})
const loading = ref(false)

async function handleLogin() {
  loading.value = true
  try {
    await authStore.login(form.value)
    ElMessage.success('登录成功')
    const redirect = route.query.redirect as string
    router.push(redirect || '/')
  } catch (e: unknown) {
    const error = e as { response?: { data?: { detail?: string } } }
    ElMessage.error(error.response?.data?.detail || '登录失败')
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <h2>智能知识图谱平台</h2>
      </template>

      <el-form
        :model="form"
        label-position="top"
        @submit.prevent="handleLogin"
      >
        <el-form-item label="用户名">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>

        <el-form-item label="密码">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            show-password
          />
        </el-form-item>

        <el-form-item>
          <el-button
            type="primary"
            native-type="submit"
            :loading="loading"
            style="width: 100%"
          >
            登录
          </el-button>
        </el-form-item>

        <div class="login-links">
          <router-link to="/register">没有账号？立即注册</router-link>
        </div>
      </el-form>
    </el-card>
  </div>
</template>

<style scoped lang="scss">
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
}

.login-card {
  width: 400px;

  h2 {
    margin: 0;
    text-align: center;
  }
}

.login-links {
  text-align: center;
  margin-top: 16px;

  a {
    color: #409eff;
    text-decoration: none;

    &:hover {
      text-decoration: underline;
    }
  }
}
</style>
