<script setup lang="ts">
import { computed } from 'vue'
import { InfoFilled, Position, Search, Link } from '@element-plus/icons-vue'
import type { GraphNode } from '@/types/graph'

const props = defineProps<{
  node: GraphNode | null
  categories: string[]
  visible?: boolean
  x?: number
  y?: number
}>()

const emit = defineEmits<{
  (e: 'view-details', nodeId: string): void
  (e: 'set-start', nodeId: string): void
  (e: 'set-end', nodeId: string): void
  (e: 'find-neighbors', nodeId: string): void
  (e: 'close'): void
}>()

const categoryName = computed(() => {
  if (!props.node) return ''
  return props.categories[props.node.category] ?? '未知类型'
})

const tooltipStyle = computed(() => ({
  left: `${props.x ?? 0}px`,
  top: `${props.y ?? 0}px`,
}))

const propertiesList = computed(() => {
  if (!props.node?.value) return []
  return Object.entries(props.node.value)
    .filter(([key]) => !['centrality', 'rank'].includes(key))
    .slice(0, 5)
})
</script>

<template>
  <transition name="fade">
    <div
      v-if="visible && node"
      class="node-tooltip"
      :style="tooltipStyle"
      @click.stop
    >
      <div class="tooltip-header">
        <div class="node-title">
          <el-icon :size="18"><InfoFilled /></el-icon>
          <span class="node-name">{{ node.name }}</span>
        </div>
        <el-button
          link
          size="small"
          @click="emit('close')"
        >
          ×
        </el-button>
      </div>

      <div class="tooltip-body">
        <div class="node-meta">
          <el-tag size="small" effect="plain">{{ categoryName }}</el-tag>
          <span v-if="node.value?.centrality" class="centrality-score">
            中心度: {{ (node.value.centrality as number).toFixed(3) }}
          </span>
        </div>

        <div v-if="propertiesList.length > 0" class="node-properties">
          <div
            v-for="[key, value] in propertiesList"
            :key="key"
            class="property-row"
          >
            <span class="property-key">{{ key }}:</span>
            <span class="property-value">{{ value }}</span>
          </div>
        </div>
      </div>

      <div class="tooltip-actions">
        <el-button
          size="small"
          type="primary"
          plain
          @click="emit('view-details', node.id)"
        >
          <el-icon><InfoFilled /></el-icon>
          查看详情
        </el-button>
        <el-button
          size="small"
          @click="emit('set-start', node.id)"
        >
          <el-icon><Position /></el-icon>
          设为起点
        </el-button>
        <el-button
          size="small"
          @click="emit('set-end', node.id)"
        >
          <el-icon><Position style="transform: rotate(180deg)" /></el-icon>
          设为终点
        </el-button>
        <el-button
          size="small"
          @click="emit('find-neighbors', node.id)"
        >
          <el-icon><Link /></el-icon>
          查找邻居
        </el-button>
      </div>
    </div>
  </transition>
</template>

<style scoped>
.node-tooltip {
  position: fixed;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  min-width: 280px;
  max-width: 350px;
  z-index: 1000;
  border: 1px solid var(--el-border-color-light);
}

.tooltip-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--el-border-color-lighter);
  background: var(--el-fill-color-light);
  border-radius: 8px 8px 0 0;
}

.node-title {
  display: flex;
  align-items: center;
  gap: 8px;
}

.node-name {
  font-size: 15px;
  font-weight: 500;
  color: var(--el-text-color-primary);
}

.tooltip-body {
  padding: 12px 16px;
}

.node-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.centrality-score {
  font-size: 12px;
  color: var(--el-text-color-secondary);
}

.node-properties {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.property-row {
  display: flex;
  gap: 8px;
  font-size: 13px;
}

.property-key {
  color: var(--el-text-color-secondary);
  min-width: 80px;
}

.property-value {
  color: var(--el-text-color-primary);
  flex: 1;
  word-break: break-all;
}

.tooltip-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid var(--el-border-color-lighter);
  background: var(--el-fill-color-light);
  border-radius: 0 0 8px 8px;
}

.tooltip-actions .el-button {
  flex: 1;
  min-width: fit-content;
}

.fade-enter-active,
.fade-leave-active {
  transition: all 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: scale(0.95) translateY(-10px);
}
</style>
