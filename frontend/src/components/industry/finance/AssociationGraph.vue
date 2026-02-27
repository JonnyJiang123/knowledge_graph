<template>
  <div ref="chartRef" class="association-graph"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as echarts from 'echarts'

const props = defineProps<{
  enterpriseId: string
  depth: number
  data: {
    nodes: any[]
    edges: any[]
  }
}>()

const emit = defineEmits<{
  nodeClick: [node: any]
}>()

const chartRef = ref<HTMLDivElement>()
let chart: echarts.ECharts | null = null

const initChart = () => {
  if (!chartRef.value) return

  chart = echarts.init(chartRef.value)

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: (params: any) => {
        if (params.dataType === 'node') {
          return `${params.data.name}<br/>类型: ${params.data.type}`
        }
        return params.data.relation_type
      }
    },
    series: [{
      type: 'graph',
      layout: 'force',
      data: props.data.nodes.map(node => ({
        id: node.id,
        name: node.name,
        symbolSize: node.id === props.enterpriseId ? 60 : 40,
        itemStyle: {
          color: getNodeColor(node.risk_level)
        },
        ...node
      })),
      links: props.data.edges.map(edge => ({
        source: edge.source,
        target: edge.target,
        label: {
          show: true,
          formatter: edge.relation_type
        },
        ...edge
      })),
      roam: true,
      label: {
        show: true,
        position: 'bottom'
      },
      force: {
        repulsion: 300,
        edgeLength: 150
      },
      emphasis: {
        focus: 'adjacency',
        lineStyle: {
          width: 4
        }
      }
    }]
  }

  chart.setOption(option)

  chart.on('click', (params: any) => {
    if (params.dataType === 'node') {
      emit('nodeClick', params.data)
    }
  })
}

const getNodeColor = (riskLevel: string) => {
  const colors: Record<string, string> = {
    'LOW': '#67c23a',
    'MEDIUM': '#e6a23c',
    'HIGH': '#f56c6c'
  }
  return colors[riskLevel] || '#909399'
}

const updateChart = () => {
  if (!chart) return

  chart.setOption({
    series: [{
      data: props.data.nodes,
      links: props.data.edges
    }]
  })
}

watch(() => props.data, updateChart, { deep: true })

onMounted(() => {
  initChart()
  window.addEventListener('resize', () => chart?.resize())
})

onUnmounted(() => {
  chart?.dispose()
})
</script>

<style scoped>
.association-graph {
  width: 100%;
  height: 500px;
}
</style>
