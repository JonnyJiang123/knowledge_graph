<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import { FullScreen, Download, ZoomIn, ZoomOut, Refresh, Rank } from '@element-plus/icons-vue'
import { useVisualizationStore } from '@/stores/visualization'
import { useQueryStore } from '@/stores/query'
import GraphCanvas from '@/components/graph/GraphCanvas.vue'
import FilterPanel from '@/components/graph/FilterPanel.vue'
import LayoutSwitcher from '@/components/graph/LayoutSwitcher.vue'
import NodeTooltip from '@/components/graph/NodeTooltip.vue'
import ExportDialog from '@/components/graph/ExportDialog.vue'

const route = useRoute()
const vizStore = useVisualizationStore()
const queryStore = useQueryStore()

const projectId = computed(() => route.params.projectId as string || 'default')
const graphCanvasRef = ref<InstanceType<typeof GraphCanvas>>()

const showFilters = ref(true)
const showExportDialog = ref(false)
const hoveredNodeId = ref<string | null>(null)
const tooltipPosition = ref({ x: 0, y: 0 })
const showTooltip = ref(false)

// 统计信息
const stats = computed(() => ({
  nodes: vizStore.nodeCount,
  edges: vizStore.edgeCount,
  selected: vizStore.selectedNodes.length,
}))

onMounted(async () => {
  await loadGraphData()
})

async function loadGraphData() {
  try {
    await vizStore.fetchGraphData(projectId.value, {
      layout: vizStore.layoutMode,
    })
  } catch (error) {
    console.error('Failed to load graph data:', error)
  }
}

function handleNodeClick(nodeId: string) {
  vizStore.toggleNodeSelection(nodeId)
}

function handleNodeHover(nodeId: string | null) {
  hoveredNodeId.value = nodeId
  showTooltip.value = !!nodeId
  
  if (nodeId && vizStore.graphData) {
    // 这里可以计算tooltip位置
    // 实际项目中应该根据鼠标位置或节点位置计算
  }
}

function handleCanvasClick() {
  vizStore.clearSelection()
  showTooltip.value = false
}

function handleTooltipAction(action: string, nodeId: string) {
  showTooltip.value = false
  
  switch (action) {
    case 'view-details':
      console.log('View details:', nodeId)
      // 导航到实体详情页
      break
    case 'set-start':
      console.log('Set as path start:', nodeId)
      // 设置路径起点
      break
    case 'set-end':
      console.log('Set as path end:', nodeId)
      // 设置路径终点
      break
    case 'find-neighbors':
      queryStore.searchEntities({ keyword: nodeId, limit: 10 })
      break
  }
}

function handleLayoutChange(mode: any) {
  vizStore.applyLayout(mode)
}

function handleFilterApply() {
  // 过滤器已经在store中更新
  console.log('Filters applied:', vizStore.filters)
}

function handleFilterReset() {
  vizStore.resetFilters()
}

function handleCentralityAnalysis() {
  vizStore.runCentralityAnalysis(projectId.value, 'pagerank')
}

const hoveredNode = computed(() => {
  if (!hoveredNodeId.value || !vizStore.graphData) return null
  return vizStore.graphData.nodes.find(n => n.id === hoveredNodeId.value) || null
})
</script>

<template>
  <div class="graph-visualization">
    <!-- 侧边栏过滤器 -->
    <aside v-show="showFilters" class="filter-sidebar">
      <FilterPanel
        :data="vizStore.graphData"
        v-model="vizStore.filters"
        @apply="handleFilterApply"
        @reset="handleFilterReset"
      />
    </aside>

    <!-- 主视图区域 -->
    <main class="main-content">
      <!-- 顶部工具栏 -->
      <div class="toolbar">
        <div class="toolbar-left">
          <el-button
            :type="showFilters ? 'primary' : 'default'"
            size="small"
            @click="showFilters = !showFilters"
          >
            过滤器
          </el-button>
          <LayoutSwitcher
            v-model="vizStore.layoutMode"
            @change="handleLayoutChange"
          />
        </div>

        <div class="toolbar-center">
          <div class="stats-bar">
            <el-tag size="small">节点: {{ stats.nodes }}</el-tag>
            <el-tag size="small" type="success">边: {{ stats.edges }}</el-tag>
            <el-tag v-if="stats.selected > 0" size="small" type="warning">
              选中: {{ stats.selected }}
            </el-tag>
          </div>
        </div>

        <div class="toolbar-right">
          <el-tooltip content="缩小">
            <el-button circle size="small" @click="graphCanvasRef?.zoomOut">
              <el-icon><ZoomOut /></el-icon>
            </el-button>
          </el-tooltip>
          <el-tooltip content="放大">
            <el-button circle size="small" @click="graphCanvasRef?.zoomIn">
              <el-icon><ZoomIn /></el-icon>
            </el-button>
          </el-tooltip>
          <el-tooltip content="重置视图">
            <el-button circle size="small" @click="graphCanvasRef?.resetZoom">
              <el-icon><Refresh /></el-icon>
            </el-button>
          </el-tooltip>
          <el-tooltip content="适应窗口">
            <el-button circle size="small" @click="graphCanvasRef?.fitView">
              <el-icon><FullScreen /></el-icon>
            </el-button>
          </el-tooltip>
          <el-divider direction="vertical" />
          <el-button size="small" @click="handleCentralityAnalysis">
            <el-icon><Rank /></el-icon>
            中心度分析
          </el-button>
          <el-button type="primary" size="small" @click="showExportDialog = true">
            <el-icon><Download /></el-icon>
            导出
          </el-button>
        </div>
      </div>

      <!-- 图谱画布 -->
      <div class="canvas-container">
        <GraphCanvas
          ref="graphCanvasRef"
          :data="vizStore.graphData || { nodes: [], edges: [], categories: [] }"
          :layout-mode="vizStore.layoutMode"
          :selected-nodes="vizStore.selectedNodes"
          :zoom-level="vizStore.zoomLevel"
          :loading="vizStore.loading"
          @node-click="handleNodeClick"
          @node-hover="handleNodeHover"
          @canvas-click="handleCanvasClick"
          @update:zoom-level="vizStore.setZoomLevel($event)"
        />

        <!-- 节点提示 -->
        <NodeTooltip
          :node="hoveredNode"
          :categories="vizStore.graphData?.categories || []"
          :visible="showTooltip"
          :x="tooltipPosition.x"
          :y="tooltipPosition.y"
          @view-details="handleTooltipAction('view-details', $event)"
          @set-start="handleTooltipAction('set-start', $event)"
          @set-end="handleTooltipAction('set-end', $event)"
          @find-neighbors="handleTooltipAction('find-neighbors', $event)"
          @close="showTooltip = false"
        />
      </div>

      <!-- 选中节点详情面板 -->
      <transition name="slide">
        <div v-if="vizStore.selectedNodeDetails" class="details-panel">
          <div class="details-header">
            <h4>{{ vizStore.selectedNodeDetails.node.name }}</h4>
            <el-button
              link
              size="small"
              @click="vizStore.clearSelection"
            >
              ×
            </el-button>
          </div>
          <div class="details-body">
            <div class="detail-row">
              <span class="detail-label">类型:</span>
              <el-tag size="small">
                {{ vizStore.graphData?.categories[vizStore.selectedNodeDetails.node.category] }}
              </el-tag>
            </div>
            <div class="detail-row">
              <span class="detail-label">ID:</span>
              <span class="detail-value">{{ vizStore.selectedNodeDetails.node.id }}</span>
            </div>
            <div class="detail-section">
              <div class="detail-section-title">
                邻居节点 ({{ vizStore.selectedNodeDetails.neighbors.length }})
              </div>
              <el-scrollbar max-height="200px">
                <div
                  v-for="neighbor in vizStore.selectedNodeDetails.neighbors"
                  :key="neighbor.node.id"
                  class="neighbor-item"
                >
                  <el-icon v-if="neighbor.direction === 'out'" color="#67C23A"><TopRight /></el-icon>
                  <el-icon v-else color="#F56C6C"><BottomLeft /></el-icon>
                  <span class="neighbor-name">{{ neighbor.node.name }}</span>
                  <el-tag size="small" type="info">{{ neighbor.relation }}</el-tag>
                </div>
              </el-scrollbar>
            </div>
          </div>
        </div>
      </transition>
    </main>

    <!-- 导出对话框 -->
    <ExportDialog
      v-model="showExportDialog"
      :data="vizStore.graphData"
      :chart-instance="graphCanvasRef?.getInstance?.()"
    />
  </div>
</template>

<style scoped>
.graph-visualization {
  display: flex;
  height: calc(100vh - 60px);
  overflow: hidden;
}

.filter-sidebar {
  width: 280px;
  flex-shrink: 0;
  border-right: 1px solid var(--el-border-color-light);
  background: white;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: white;
  border-bottom: 1px solid var(--el-border-color-light);
  gap: 16px;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.toolbar-center {
  flex: 1;
  display: flex;
  justify-content: center;
}

.stats-bar {
  display: flex;
  gap: 8px;
}

.canvas-container {
  flex: 1;
  position: relative;
  overflow: hidden;
  background: var(--el-fill-color-light);
}

.details-panel {
  position: absolute;
  right: 16px;
  top: 72px;
  width: 300px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--el-border-color-light);
}

.details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.details-header h4 {
  margin: 0;
  font-size: 15px;
}

.details-body {
  padding: 16px;
}

.detail-row {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
}

.detail-label {
  font-size: 13px;
  color: var(--el-text-color-secondary);
  min-width: 50px;
}

.detail-value {
  font-size: 13px;
  color: var(--el-text-color-primary);
  word-break: break-all;
}

.detail-section {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--el-border-color-lighter);
}

.detail-section-title {
  font-size: 13px;
  font-weight: 500;
  color: var(--el-text-color-primary);
  margin-bottom: 12px;
}

.neighbor-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 0;
  border-bottom: 1px solid var(--el-border-color-lighter);
}

.neighbor-name {
  flex: 1;
  font-size: 13px;
  color: var(--el-text-color-primary);
}

.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  opacity: 0;
  transform: translateX(100%);
}
</style>
