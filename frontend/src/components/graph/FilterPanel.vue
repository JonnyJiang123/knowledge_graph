<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Filter, Refresh, Search } from '@element-plus/icons-vue'
import type { GraphFilters } from '@/types/visualization'
import type { GraphData } from '@/types/graph'

const props = defineProps<{
  data: GraphData | null
  modelValue: GraphFilters
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', filters: GraphFilters): void
  (e: 'apply'): void
  (e: 'reset'): void
}>()

// 从图谱数据中提取可用的类型
const availableEntityTypes = computed(() => {
  if (!props.data) return []
  return [...new Set(props.data.categories)]
})

const availableRelationTypes = computed(() => {
  if (!props.data) return []
  return [...new Set(props.data.edges.map(e => e.relation))]
})

const localFilters = ref<GraphFilters>({ ...props.modelValue })

watch(() => props.modelValue, (newVal) => {
  localFilters.value = { ...newVal }
}, { deep: true })

function applyFilters() {
  emit('update:modelValue', { ...localFilters.value })
  emit('apply')
}

function resetFilters() {
  localFilters.value = {
    entityTypes: [],
    relationTypes: [],
    searchKeyword: '',
  }
  emit('reset')
}

function updateEntityTypes(types: string[]) {
  localFilters.value.entityTypes = types
}

function updateRelationTypes(types: string[]) {
  localFilters.value.relationTypes = types
}

const activeFilterCount = computed(() => {
  let count = 0
  if (localFilters.value.entityTypes.length > 0) count++
  if (localFilters.value.relationTypes.length > 0) count++
  if (localFilters.value.searchKeyword) count++
  return count
})
</script>

<template>
  <div class="filter-panel">
    <div class="panel-header">
      <div class="panel-title">
        <el-icon><Filter /></el-icon>
        <span>过滤器</span>
        <el-badge v-if="activeFilterCount > 0" :value="activeFilterCount" type="primary" />
      </div>
      <el-button
        link
        type="primary"
        size="small"
        @click="resetFilters"
      >
        <el-icon><Refresh /></el-icon>
        重置
      </el-button>
    </div>

    <div class="panel-content">
      <!-- 关键词搜索 -->
      <div class="filter-section">
        <div class="section-label">搜索节点</div>
        <el-input
          v-model="localFilters.searchKeyword"
          placeholder="输入节点名称..."
          clearable
          @keyup.enter="applyFilters"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>

      <!-- 实体类型过滤 -->
      <div class="filter-section">
        <div class="section-label">
          实体类型
          <el-tag size="small" type="info">{{ localFilters.entityTypes.length }}/{{ availableEntityTypes.length }}</el-tag>
        </div>
        <el-checkbox-group
          v-model="localFilters.entityTypes"
          class="checkbox-list"
          @change="applyFilters"
        >
          <el-checkbox
            v-for="type in availableEntityTypes"
            :key="type"
            :label="type"
          >
            {{ type }}
          </el-checkbox>
        </el-checkbox-group>
        <el-empty
          v-if="availableEntityTypes.length === 0"
          description="暂无实体类型"
          :image-size="60"
        />
      </div>

      <!-- 关系类型过滤 -->
      <div class="filter-section">
        <div class="section-label">
          关系类型
          <el-tag size="small" type="info">{{ localFilters.relationTypes.length }}/{{ availableRelationTypes.length }}</el-tag>
        </div>
        <el-checkbox-group
          v-model="localFilters.relationTypes"
          class="checkbox-list"
          @change="applyFilters"
        >
          <el-checkbox
            v-for="type in availableRelationTypes"
            :key="type"
            :label="type"
          >
            {{ type }}
          </el-checkbox>
        </el-checkbox-group>
        <el-empty
          v-if="availableRelationTypes.length === 0"
          description="暂无关系类型"
          :image-size="60"
        />
      </div>
    </div>

    <div class="panel-footer">
      <el-button
        type="primary"
        style="width: 100%"
        @click="applyFilters"
      >
        应用过滤
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.filter-panel {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: white;
  border-right: 1px solid var(--el-border-color-light);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid var(--el-border-color-light);
}

.panel-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 500;
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.filter-section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.section-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.checkbox-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.checkbox-list :deep(.el-checkbox) {
  margin-right: 0;
  height: auto;
  padding: 4px 0;
}

.panel-footer {
  padding: 16px;
  border-top: 1px solid var(--el-border-color-light);
}
</style>
