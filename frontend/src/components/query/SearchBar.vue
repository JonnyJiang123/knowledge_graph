<script setup lang="ts">
import { ref, computed } from 'vue'
import { Search, Clock, Delete } from '@element-plus/icons-vue'
import type { SearchParams, SearchRecord } from '@/types/query'

const props = defineProps<{
  modelValue: string
  entityTypes?: string[]
  availableTypes?: string[]
  history?: SearchRecord[]
  loading?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: string): void
  (e: 'search', params: SearchParams): void
  (e: 'clear-history'): void
}>()

const selectedTypes = ref<string[]>(props.entityTypes ?? [])
const showHistory = ref(false)

const hasInput = computed(() => props.modelValue.trim().length > 0)

function handleSearch() {
  if (!hasInput.value) return
  
  emit('search', {
    keyword: props.modelValue.trim(),
    entityTypes: selectedTypes.value.length > 0 ? selectedTypes.value : undefined,
    limit: 20,
    offset: 0,
  })
  showHistory.value = false
}

function handleInput(value: string) {
  emit('update:modelValue', value)
  showHistory.value = value.length === 0 && (props.history?.length ?? 0) > 0
}

function handleHistoryClick(record: SearchRecord) {
  emit('update:modelValue', record.query)
  showHistory.value = false
  emit('search', {
    keyword: record.query,
    entityTypes: selectedTypes.value.length > 0 ? selectedTypes.value : undefined,
    limit: 20,
    offset: 0,
  })
}

// function clearInput() {
//   emit('update:modelValue', '')
//   showHistory.value = (props.history?.length ?? 0) > 0
// }

function handleKeyDown(event: Event | KeyboardEvent) {
  if ('key' in event && event.key === 'Enter') {
    handleSearch()
  }
}
</script>

<template>
  <div class="search-bar">
    <div class="search-input-wrapper">
      <el-input
        :model-value="modelValue"
        placeholder="搜索实体..."
        size="large"
        clearable
        @update:model-value="handleInput"
        @keydown="handleKeyDown"
        @focus="showHistory = (history?.length ?? 0) > 0 && !hasInput"
        @blur="showHistory = false"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
        <template #append>
          <el-button
            type="primary"
            :loading="loading"
            :disabled="!hasInput"
            @click="handleSearch"
          >
            搜索
          </el-button>
        </template>
      </el-input>

      <!-- 搜索历史下拉 -->
      <transition name="fade">
        <div v-if="showHistory && history && history.length > 0" class="history-dropdown">
          <div class="history-header">
            <span class="history-title">
              <el-icon><Clock /></el-icon>
              搜索历史
            </span>
            <el-button
              link
              type="danger"
              size="small"
              @click="emit('clear-history')"
            >
              <el-icon><Delete /></el-icon>
              清空
            </el-button>
          </div>
          <div
            v-for="record in history.slice(0, 8)"
            :key="record.id"
            class="history-item"
            @mousedown.prevent="handleHistoryClick(record)"
          >
            <span class="history-query">{{ record.query }}</span>
            <span class="history-count">{{ record.resultCount }} 结果</span>
          </div>
        </div>
      </transition>
    </div>

    <!-- 实体类型选择器 -->
    <div v-if="availableTypes && availableTypes.length > 0" class="type-filter">
      <span class="filter-label">实体类型:</span>
      <el-checkbox-group v-model="selectedTypes" size="small">
        <el-checkbox-button
          v-for="type in availableTypes"
          :key="type"
          :label="type"
        >
          {{ type }}
        </el-checkbox-button>
      </el-checkbox-group>
    </div>
  </div>
</template>

<style scoped>
.search-bar {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.search-input-wrapper {
  position: relative;
}

.history-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 4px;
  background: white;
  border: 1px solid var(--el-border-color-light);
  border-radius: 4px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  z-index: 100;
  max-height: 300px;
  overflow-y: auto;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  background: var(--el-fill-color-light);
}

.history-title {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 12px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.history-item:hover {
  background: var(--el-fill-color-light);
}

.history-query {
  color: var(--el-text-color-primary);
  font-size: 14px;
}

.history-count {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.type-filter {
  display: flex;
  align-items: center;
  gap: 12px;
}

.filter-label {
  font-size: 14px;
  color: var(--el-text-color-secondary);
  white-space: nowrap;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
