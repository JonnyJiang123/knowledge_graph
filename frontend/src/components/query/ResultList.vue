<script setup lang="ts">
import { computed } from 'vue'
import { Document, ArrowUp, ArrowDown } from '@element-plus/icons-vue'
import type { SearchEntity, PathResult } from '@/types/query'

type SortField = 'relevance' | 'name' | 'type'
type SortOrder = 'asc' | 'desc'

const props = defineProps<{
  entities?: SearchEntity[]
  paths?: PathResult[]
  total: number
  pageSize?: number
  currentPage?: number
  sortField?: SortField
  sortOrder?: SortOrder
  loading?: boolean
}>()

const emit = defineEmits<{
  (e: 'page-change', page: number): void
  (e: 'sort-change', field: SortField, order: SortOrder): void
  (e: 'entity-click', entity: SearchEntity): void
  (e: 'path-click', path: PathResult): void
}>()

const isEntityMode = computed(() => props.entities !== undefined)
const currentItems = computed(() => props.entities ?? props.paths ?? [])

const totalPages = computed(() => 
  Math.ceil(props.total / (props.pageSize ?? 20))
)

function getEntityIcon(type: string): string {
  const iconMap: Record<string, string> = {
    'PERSON': 'User',
    'COMPANY': 'OfficeBuilding',
    'ORGANIZATION': 'OfficeBuilding',
    'PRODUCT': 'Box',
    'LOCATION': 'Location',
    'EVENT': 'Calendar',
  }
  return iconMap[type?.toUpperCase()] ?? 'Document'
}

function getEntityIconColor(type: string): string {
  const colorMap: Record<string, string> = {
    'PERSON': '#409EFF',
    'COMPANY': '#67C23A',
    'ORGANIZATION': '#67C23A',
    'PRODUCT': '#E6A23C',
    'LOCATION': '#909399',
    'EVENT': '#F56C6C',
  }
  return colorMap[type?.toUpperCase()] ?? '#909399'
}

function handleSort(field: SortField) {
  let newOrder: SortOrder = 'asc'
  if (props.sortField === field) {
    newOrder = props.sortOrder === 'asc' ? 'desc' : 'asc'
  }
  emit('sort-change', field, newOrder)
}

function getSortIcon(field: SortField) {
  if (props.sortField !== field) return null
  return props.sortOrder === 'asc' ? ArrowUp : ArrowDown
}
</script>

<template>
  <div class="result-list">
    <!-- 结果头部 -->
    <div class="result-header">
      <div class="result-count">
        找到 <strong>{{ total }}</strong> 个结果
      </div>
      <div v-if="isEntityMode" class="sort-options">
        <span class="sort-label">排序:</span>
        <el-button
          link
          :type="sortField === 'relevance' ? 'primary' : 'info'"
          size="small"
          @click="handleSort('relevance')"
        >
          相关度
          <el-icon v-if="getSortIcon('relevance')" class="sort-icon">
            <component :is="getSortIcon('relevance')" />
          </el-icon>
        </el-button>
        <el-button
          link
          :type="sortField === 'name' ? 'primary' : 'info'"
          size="small"
          @click="handleSort('name')"
        >
          名称
          <el-icon v-if="getSortIcon('name')" class="sort-icon">
            <component :is="getSortIcon('name')" />
          </el-icon>
        </el-button>
        <el-button
          link
          :type="sortField === 'type' ? 'primary' : 'info'"
          size="small"
          @click="handleSort('type')"
        >
          类型
          <el-icon v-if="getSortIcon('type')" class="sort-icon">
            <component :is="getSortIcon('type')" />
          </el-icon>
        </el-button>
      </div>
    </div>

    <!-- 结果内容 -->
    <div v-loading="loading" class="result-content">
      <el-empty v-if="currentItems.length === 0" description="暂无结果" />

      <!-- 实体结果卡片 -->
      <template v-else-if="isEntityMode">
        <div
          v-for="entity in entities"
          :key="entity.id"
          class="entity-card"
          @click="emit('entity-click', entity)"
        >
          <div class="entity-icon" :style="{ backgroundColor: getEntityIconColor(entity.type) + '20' }">
            <el-icon :size="24" :color="getEntityIconColor(entity.type)">
              <component :is="getEntityIcon(entity.type)" />
            </el-icon>
          </div>
          <div class="entity-info">
            <div class="entity-header">
              <span class="entity-name">{{ entity.name }}</span>
              <el-tag size="small" effect="plain">{{ entity.type }}</el-tag>
              <el-tag v-if="entity.score" size="small" type="warning">
                相关度: {{ (entity.score * 100).toFixed(1) }}%
              </el-tag>
            </div>
            <div class="entity-properties">
              <span
                v-for="(value, key) in entity.properties"
                :key="key"
                class="property-item"
              >
                {{ key }}: {{ value }}
              </span>
            </div>
            <div class="entity-labels">
              <el-tag
                v-for="label in entity.labels"
                :key="label"
                size="small"
                type="info"
                effect="plain"
              >
                {{ label }}
              </el-tag>
            </div>
          </div>
        </div>
      </template>

      <!-- 路径结果卡片 -->
      <template v-else>
        <div
          v-for="(path, index) in paths"
          :key="index"
          class="path-card"
          @click="emit('path-click', path)"
        >
          <div class="path-header">
            <span class="path-title">路径 {{ index + 1 }}</span>
            <el-tag size="small" type="success">{{ path.length }} 跳</el-tag>
          </div>
          <div class="path-nodes">
            <template v-for="(node, nodeIndex) in path.nodes" :key="node.id">
              <span class="path-node">{{ node.name }}</span>
              <el-icon v-if="nodeIndex < path.nodes.length - 1" class="path-arrow">
                <ArrowRight />
              </el-icon>
            </template>
          </div>
        </div>
      </template>
    </div>

    <!-- 分页 -->
    <div v-if="totalPages > 1" class="result-pagination">
      <el-pagination
        :current-page="currentPage ?? 1"
        :page-size="pageSize ?? 20"
        :total="total"
        layout="prev, pager, next, jumper"
        @current-change="emit('page-change', $event)"
      />
    </div>
  </div>
</template>

<style scoped>
.result-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 4px;
}

.result-count {
  font-size: 14px;
  color: var(--el-text-color-regular);
}

.result-count strong {
  color: var(--el-color-primary);
}

.sort-options {
  display: flex;
  align-items: center;
  gap: 8px;
}

.sort-label {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.sort-icon {
  margin-left: 4px;
  font-size: 12px;
}

.result-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-height: 200px;
}

.entity-card {
  display: flex;
  gap: 16px;
  padding: 16px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.entity-card:hover {
  border-color: var(--el-color-primary);
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.entity-icon {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  flex-shrink: 0;
}

.entity-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.entity-header {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.entity-name {
  font-size: 16px;
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.entity-properties {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.property-item {
  font-size: 13px;
  color: var(--el-text-color-secondary);
}

.entity-labels {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.path-card {
  padding: 16px;
  border: 1px solid var(--el-border-color-light);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.path-card:hover {
  border-color: var(--el-color-primary);
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
}

.path-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.path-title {
  font-size: 14px;
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.path-nodes {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.path-node {
  padding: 4px 12px;
  background: var(--el-fill-color-light);
  border-radius: 4px;
  font-size: 13px;
  color: var(--el-text-color-regular);
}

.path-arrow {
  color: var(--el-text-color-secondary);
}

.result-pagination {
  display: flex;
  justify-content: center;
  padding-top: 16px;
  border-top: 1px solid var(--el-border-color-light);
}
</style>
