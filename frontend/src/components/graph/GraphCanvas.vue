<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import * as echarts from 'echarts'
import type { ECharts, EChartsOption } from 'echarts'
import type { GraphData, LayoutMode } from '@/types/visualization'
import type { GraphNode, GraphEdge } from '@/types/graph'

const props = defineProps<{
  data: GraphData
  layoutMode: LayoutMode
  selectedNodes: string[]
  zoomLevel: number
  loading?: boolean
}>()

const emit = defineEmits<{
  (e: 'node-click', nodeId: string): void
  (e: 'node-hover', nodeId: string | null): void
  (e: 'canvas-click'): void
  (e: 'update:zoomLevel', level: number): void
}>()

const chartRef = ref<HTMLDivElement>()
let chartInstance: ECharts | null = null

// 初始化图表
function initChart() {
  if (!chartRef.value) return
  
  chartInstance = echarts.init(chartRef.value)
  
  // 绑定事件
  chartInstance.on('click', (params: any) => {
    if (params.dataType === 'node') {
      emit('node-click', params.data.id)
    } else {
      emit('canvas-click')
    }
  })
  
  chartInstance.on('mouseover', (params: any) => {
    if (params.dataType === 'node') {
      emit('node-hover', params.data.id)
    }
  })
  
  chartInstance.on('mouseout', () => {
    emit('node-hover', null)
  })

  chartInstance.on('finished', () => {
    if (chartInstance) {
      const option = chartInstance.getOption()
      if (option.series && option.series[0]?.zoom) {
        emit('update:zoomLevel', option.series[0].zoom)
      }
    }
  })

  updateChart()
}

// 获取布局配置
function getLayoutConfig(): any {
  switch (props.layoutMode) {
    case 'force':
      return {
        layout: 'force',
        force: {
          repulsion: 1000,
          gravity: 0.1,
          edgeLength: 150,
          layoutAnimation: true,
        },
      }
    case 'hierarchical':
      return {
        layout: 'none',
        // 使用层次布局的坐标计算
        nodes: props.data.nodes.map((node, index) => ({
          ...node,
          x: node.x ?? (index % 5) * 200,
          y: node.y ?? Math.floor(index / 5) * 100,
        })),
      }
    case 'circular':
      return {
        layout: 'circular',
        circular: {
          rotateLabel: true,
        },
      }
    default:
      return {
        layout: 'force',
        force: {
          repulsion: 1000,
          gravity: 0.1,
          edgeLength: 150,
        },
      }
  }
}

// 生成图表配置
function getChartOption(): EChartsOption {
  const layoutConfig = getLayoutConfig()
  
  // 准备节点数据
  const nodes = props.data.nodes.map(node => ({
    id: node.id,
    name: node.name,
    category: node.category,
    symbolSize: node.symbolSize,
    value: node.value,
    x: node.x,
    y: node.y,
    fixed: node.fixed,
    draggable: true,
    itemStyle: {
      borderWidth: props.selectedNodes.includes(node.id) ? 3 : 1,
      borderColor: props.selectedNodes.includes(node.id) ? '#F56C6C' : '#fff',
      shadowBlur: props.selectedNodes.includes(node.id) ? 10 : 0,
      shadowColor: '#F56C6C',
    },
    label: {
      show: true,
      position: 'bottom',
      formatter: '{b}',
      fontSize: 12,
    },
  }))

  // 准备边数据
  const edges = props.data.edges.map(edge => ({
    source: edge.source,
    target: edge.target,
    value: edge.value ?? 1,
    label: {
      show: true,
      formatter: edge.relation,
      fontSize: 10,
    },
    lineStyle: {
      curveness: 0.1,
      width: edge.value ? Math.max(1, edge.value) : 1,
    },
  }))

  return {
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        if (params.dataType === 'node') {
          return `<div style="font-weight:500">${params.data.name}</div>
                  <div style="font-size:12px;color:#999">类型: ${props.data.categories[params.data.category]}</div>`
        }
        return `${params.data.relation || '连接'}`
      },
    },
    animationDuration: 1500,
    animationEasingUpdate: 'quinticInOut',
    series: [
      {
        name: '知识图谱',
        type: 'graph',
        ...layoutConfig,
        data: layoutConfig.nodes || nodes,
        links: edges,
        categories: props.data.categories.map((name, index) => ({
          name,
          itemStyle: {
            color: getCategoryColor(index),
          },
        })),
        roam: true,
        zoom: props.zoomLevel,
        label: {
          show: true,
          position: 'right',
          formatter: '{b}',
        },
        lineStyle: {
          color: 'source',
          curveness: 0.1,
        },
        emphasis: {
          focus: 'adjacency',
          lineStyle: {
            width: 4,
          },
        },
        edgeSymbol: ['circle', 'arrow'],
        edgeSymbolSize: [4, 10],
      },
    ],
  }
}

// 获取类别颜色
function getCategoryColor(index: number): string {
  const colors = [
    '#5470c6',
    '#91cc75',
    '#fac858',
    '#ee6666',
    '#73c0de',
    '#3ba272',
    '#fc8452',
    '#9a60b4',
    '#ea7ccc',
  ]
  return colors[index % colors.length]
}

// 更新图表
function updateChart() {
  if (!chartInstance) return
  const option = getChartOption()
  chartInstance.setOption(option, true)
}

// 处理窗口大小变化
function handleResize() {
  chartInstance?.resize()
}

// 缩放控制
function zoomIn() {
  if (!chartInstance) return
  const option = chartInstance.getOption()
  const currentZoom = (option.series as any)[0]?.zoom ?? 1
  const newZoom = Math.min(currentZoom * 1.2, 5)
  chartInstance.setOption({
    series: [{ zoom: newZoom }],
  })
  emit('update:zoomLevel', newZoom)
}

function zoomOut() {
  if (!chartInstance) return
  const option = chartInstance.getOption()
  const currentZoom = (option.series as any)[0]?.zoom ?? 1
  const newZoom = Math.max(currentZoom / 1.2, 0.1)
  chartInstance.setOption({
    series: [{ zoom: newZoom }],
  })
  emit('update:zoomLevel', newZoom)
}

function resetZoom() {
  if (!chartInstance) return
  chartInstance.setOption({
    series: [{ zoom: 1, center: null }],
  })
  emit('update:zoomLevel', 1)
}

function fitView() {
  if (!chartInstance) return
  chartInstance.dispatchAction({
    type: 'restore',
  })
}

// 高亮节点
function highlightNode(nodeId: string) {
  if (!chartInstance) return
  chartInstance.dispatchAction({
    type: 'highlight',
    seriesIndex: 0,
    dataIndex: props.data.nodes.findIndex(n => n.id === nodeId),
  })
}

function downplayNode(nodeId: string) {
  if (!chartInstance) return
  chartInstance.dispatchAction({
    type: 'downplay',
    seriesIndex: 0,
    dataIndex: props.data.nodes.findIndex(n => n.id === nodeId),
  })
}

// 监听数据变化
watch(() => props.data, updateChart, { deep: true })
watch(() => props.layoutMode, updateChart)
watch(() => props.selectedNodes, updateChart, { deep: true })

// 组件生命周期
onMounted(() => {
  nextTick(initChart)
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  chartInstance?.dispose()
  chartInstance = null
})

// 暴露方法
defineExpose({
  zoomIn,
  zoomOut,
  resetZoom,
  fitView,
  highlightNode,
  downplayNode,
  getInstance: () => chartInstance,
})
</script>

<template>
  <div
    ref="chartRef"
    v-loading="loading"
    class="graph-canvas"
  ></div>
</template>

<style scoped>
.graph-canvas {
  width: 100%;
  height: 100%;
  min-height: 400px;
}
</style>
