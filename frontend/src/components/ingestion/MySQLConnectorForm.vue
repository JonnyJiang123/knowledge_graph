<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import type { MysqlConfig, MysqlTestResult } from '@/types/ingestion'

const props = defineProps<{
  modelValue: MysqlConfig
  loading?: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [value: MysqlConfig]
  test: []
}>()

const form = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

// 双向绑定各字段
const host = computed({
  get: () => form.value.host,
  set: (val) => emit('update:modelValue', { ...form.value, host: val }),
})
const port = computed({
  get: () => form.value.port,
  set: (val) => emit('update:modelValue', { ...form.value, port: val }),
})
const database = computed({
  get: () => form.value.database,
  set: (val) => emit('update:modelValue', { ...form.value, database: val }),
})
const username = computed({
  get: () => form.value.username,
  set: (val) => emit('update:modelValue', { ...form.value, username: val }),
})
const password = computed({
  get: () => form.value.password ?? '',
  set: (val) => emit('update:modelValue', { ...form.value, password: val }),
})
const table = computed({
  get: () => form.value.table ?? '',
  set: (val) => emit('update:modelValue', { ...form.value, table: val }),
})

const testResult = ref<MysqlTestResult | null>(null)

// 重置测试结果当配置变化
watch(
  () => [form.value.host, form.value.port, form.value.database, form.value.username],
  () => {
    testResult.value = null
  },
)

defineExpose({ testResult })

function handleTest() {
  emit('test')
}
</script>

<template>
  <div class="mysql-form">
    <el-form label-position="top">
      <el-row :gutter="16">
        <el-col :span="16">
          <el-form-item label="主机地址" required>
            <el-input v-model="host" placeholder="localhost" />
          </el-form-item>
        </el-col>
        <el-col :span="8">
          <el-form-item label="端口" required>
            <el-input-number
              v-model="port"
              :min="1"
              :max="65535"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="数据库名" required>
        <el-input v-model="database" placeholder="mydb" />
      </el-form-item>

      <el-row :gutter="16">
        <el-col :span="12">
          <el-form-item label="用户名" required>
            <el-input v-model="username" placeholder="root" />
          </el-form-item>
        </el-col>
        <el-col :span="12">
          <el-form-item label="密码">
            <el-input
              v-model="password"
              type="password"
              placeholder="可选"
              show-password
            />
          </el-form-item>
        </el-col>
      </el-row>

      <el-form-item label="表名（可选，默认导入所有表）">
        <el-input v-model="table" placeholder="users" />
      </el-form-item>

      <el-form-item>
        <el-button
          type="primary"
          :loading="loading"
          @click="handleTest"
        >
          测试连接
        </el-button>
      </el-form-item>

      <!-- 测试结果提示 -->
      <el-alert
        v-if="testResult"
        :type="testResult.ok ? 'success' : 'error'"
        :title="testResult.ok ? '连接成功' : '连接失败'"
        :description="testResult.message"
        show-icon
        :closable="false"
      />
    </el-form>
  </div>
</template>

<style scoped lang="scss">
.mysql-form {
  max-width: 500px;
}
</style>
