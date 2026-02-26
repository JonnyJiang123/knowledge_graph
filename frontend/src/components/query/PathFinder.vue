<script setup lang="ts">
import { ref, computed } from 'vue'
import { Connection, ArrowRight } from '@element-plus/icons-vue'
import type { PathParams } from '@/types/query'

const props = defineProps<{
  loading?: boolean
  entityOptions?: Array<{ id: string; name: string; type: string }>
}>()

const emit = defineEmits<{
  (e: 'search', params: PathParams): void
}>()

const startId = ref('')
const endId = ref('')
const maxDepth = ref(3)
const findAll = ref(false)

const canSearch = computed(() => startId.value && endId.value)

const startOptions = computed(() => {
  if (!props.entityOptions) return []
  return props.entityOptions.filter(e => e.id !== endId.value)
})

const endOptions = computed(() => {
  if (!props.entityOptions) return []
  return props.entityOptions.filter(e => e.id !== startId.value)
})

function handleSearch() {
  if (!canSearch.value) return
  emit('search', {
    startId: startId.value,
    endId: endId.value,
    maxDepth: maxDepth.value,
    findAll: findAll.value,
  })
}

function swapEntities() {
  const temp = startId.value
  startId.value = endId.value
  endId.value = temp
}
</script>

<template>
  <div class="path-finder">
    <div class="path-header">
      <div class="path-title">
        <el-icon><Connection /></el-icon>
        <span>路径查找</span>
      </div>
    </div>

    <div class="path-content">
      <!-- 起点选择 -->
      <div class="entity-selector">
        <div class="selector-label">起点实体</div>
        <el-select
          v-model="startId"
          placeholder="选择或搜索起点实体"
          filterable
          clearable
          style="width: 100%"
        >
          <el-option
            v-for="entity in startOptions"
            :key="entity.id"
            :label="entity.name"
            :value="entity.id"
          >
            <span>{{ entity.name }}</span>
            <el-tag size="small" type="info" class="entity-type">{{ entity.type }}</el-tag>
          </el-option>
        </el-select>
      </div>

      <!-- 交换按钮 -->
      <div class="swap-wrapper">
        <el-button
          circle
          size="small"
          :disabled="!startId && !endId"
          @click="swapEntities"
        >
          <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>

      <!-- 终点选择 -->
      <div class="entity-selector">
        <div class="selector-label">终点实体</div>
        <el-select
          v-model="endId"
          placeholder="选择或搜索终点实体"
          filterable
          clearable
          style="width: 100%"
        >
          <el-option
            v-for="entity in endOptions"
            :key="entity.id"
            :label="entity.name"
            :value="entity.id"
          >
            <span>{{ entity.name }}</span>
            <el-tag size="small" type="info" class="entity-type">{{ entity.type }}</el-tag>
          </el-option>
        </el-select>
      </div>
    </div>

    <!-- 路径选项 -->
    <div class="path-options">
      <div class="option-row">
        <span class="option-label">最大深度:</span>
        <el-slider
          v-model="maxDepth"
          :min="1"
          :max="10"
          :step="1"
          show-stops
          style="flex: 1"
        />
        <span class="option-value">{{ maxDepth }} 跳</span>
      </div>

      <div class="option-row">
        <span class="option-label">查找模式:</span>
        <el-radio-group v-model="findAll">
          <el-radio-button :label="false">最短路径</el-radio-button>
          <el-radio-button :label="true">所有路径</el-radio-button>
        </el-radio-group>
      </div>
    </div>

    <!-- 搜索按钮 -->
    <el-button
      type="primary"
      size="large"
      :loading="loading"
      :disabled="!canSearch"
      style="width: 100%"
      @click="handleSearch"
    >
      查找路径
    </el-button>
  </div>
</template>

<style scoped>
.path-finder {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.path-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.path-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.path-content {
  display: flex;
  align-items: flex-end;
  gap: 12px;
}

.entity-selector {
  flex: 1;
}

.selector-label {
  font-size: 12px;
  color: var(--el-text-color-secondary);
  margin-bottom: 8px;
}

.entity-type {
  margin-left: 8px;
  font-size: 11px;
}

.swap-wrapper {
  display: flex;
  align-items: center;
  padding-bottom: 8px;
}

.swap-wrapper .el-icon {
  transform: rotate(90deg);
}

.path-options {
  display: flex;
  flex-direction: column;
  gap: 16px;
  padding: 16px;
  background: var(--el-fill-color-light);
  border-radius: 4px;
}

.option-row {
  display: flex;
  align-items: center;
  gap: 16px;
}

.option-label {
  font-size: 14px;
  color: var(--el-text-color-regular);
  white-space: nowrap;
  min-width: 80px;
}

.option-value {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  min-width: 60px;
  text-align: right;
}
</style>
