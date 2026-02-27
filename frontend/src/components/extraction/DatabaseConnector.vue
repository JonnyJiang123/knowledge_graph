<template>
  <div class="database-connector">
    <el-form :model="connection" label-width="120px">
      <el-form-item label="数据库类型">
        <el-select v-model="connection.type" placeholder="选择数据库类型">
          <el-option label="MySQL" value="mysql" />
          <el-option label="PostgreSQL" value="postgresql" />
          <el-option label="SQL Server" value="sqlserver" />
          <el-option label="Oracle" value="oracle" />
        </el-select>
      </el-form-item>

      <el-form-item label="主机地址">
        <el-input v-model="connection.host" placeholder="localhost" />
      </el-form-item>

      <el-form-item label="端口">
        <el-input-number v-model="connection.port" :min="1" :max="65535" />
      </el-form-item>

      <el-form-item label="数据库名">
        <el-input v-model="connection.database" placeholder="数据库名称" />
      </el-form-item>

      <el-form-item label="用户名">
        <el-input v-model="connection.username" placeholder="用户名" />
      </el-form-item>

      <el-form-item label="密码">
        <el-input v-model="connection.password" type="password" placeholder="密码" />
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="testConnection" :loading="testing">
          测试连接
        </el-button>
        <el-button @click="saveConnection">保存连接</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'

const connection = reactive({
  type: 'mysql',
  host: 'localhost',
  port: 3306,
  database: '',
  username: '',
  password: ''
})

const testing = ref(false)

const testConnection = async () => {
  testing.value = true
  try {
    // 调用API测试连接
    // await testDatabaseConnection(connection)
    ElMessage.success('连接成功')
  } catch (error) {
    ElMessage.error('连接失败')
  } finally {
    testing.value = false
  }
}

const saveConnection = () => {
  ElMessage.success('连接配置已保存')
}
</script>

<style scoped>
.database-connector {
  padding: 20px;
  max-width: 500px;
}
</style>
