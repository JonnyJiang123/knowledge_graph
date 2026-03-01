import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import * as graphApi from '@/api/graph'
import type {
  LayoutMode,
  GraphFilters,
  FetchOptions,
  CentralityResult,
  GraphData as VisualizationGraphData,
} from '@/types'
import type { GraphNode } from '@/types/graph'

export const useVisualizationStore = defineStore('visualization', () => {
  // State
  const layoutMode = ref<LayoutMode>('force')
  const filters = ref<GraphFilters>({
    entityTypes: [],
    relationTypes: [],
  })
  const zoomLevel = ref(1)
  const selectedNodes = ref<string[]>([])
  const graphData = ref<VisualizationGraphData | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)
  const centralityResults = ref<CentralityResult[]>([])

  // Getters
  const filteredNodes = computed(() => {
    if (!graphData.value) return []
    return graphData.value.nodes.filter(node => {
      if (filters.value.entityTypes.length > 0) {
        const category = graphData.value!.categories[node.category]
        if (category && !filters.value.entityTypes.includes(category)) {
          return false
        }
      }
      if (filters.value.searchKeyword) {
        const keyword = filters.value.searchKeyword.toLowerCase()
        if (!node.name.toLowerCase().includes(keyword)) {
          return false
        }
      }
      return true
    })
  })

  const filteredEdges = computed(() => {
    if (!graphData.value) return []
    const nodeIds = new Set(filteredNodes.value.map(n => n.id))
    return graphData.value.edges.filter(edge => {
      if (!nodeIds.has(edge.source) || !nodeIds.has(edge.target)) {
        return false
      }
      if (filters.value.relationTypes.length > 0) {
        if (!filters.value.relationTypes.includes(edge.relation)) {
          return false
        }
      }
      return true
    })
  })

  const nodeCount = computed(() => filteredNodes.value.length)
  const edgeCount = computed(() => filteredEdges.value.length)

  const selectedNodeDetails = computed(() => {
    if (!graphData.value || selectedNodes.value.length === 0) return null
    const node = graphData.value.nodes.find(n => n.id === selectedNodes.value[0])
    if (!node) return null

    const neighbors = graphData.value.edges
      .filter(e => e.source === node.id || e.target === node.id)
      .map(e => {
        const neighborId = e.source === node.id ? e.target : e.source
        return {
          node: graphData.value!.nodes.find(n => n.id === neighborId),
          relation: e.relation,
          direction: e.source === node.id ? 'out' : 'in',
        }
      })
      .filter(n => n.node) as { node: GraphNode; relation: string; direction: string }[]

    return {
      node,
      neighbors,
    }
  })

  // Actions
  async function fetchGraphData(projectId: string, options?: FetchOptions) {
    loading.value = true
    error.value = null
    try {
      const data = await graphApi.getVisualizationData(projectId)
      graphData.value = data as unknown as VisualizationGraphData
      if (options?.layout) {
        layoutMode.value = options.layout
      }
      return data
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch graph data'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function runCentralityAnalysis(projectId: string, algorithm: 'pagerank' | 'betweenness') {
    loading.value = true
    error.value = null
    try {
      const response = await graphApi.runCentralityAnalysis(projectId, algorithm)
      centralityResults.value = response.results
      
      // Update node sizes based on centrality
      if (graphData.value) {
        const maxScore = Math.max(...response.results.map(r => r.score), 1)
        graphData.value.nodes = graphData.value.nodes.map(node => {
          const result = response.results.find(r => r.nodeId === node.id)
          if (result) {
            return {
              ...node,
              symbolSize: 20 + (result.score / maxScore) * 50,
              value: {
                ...node.value,
                centrality: result.score,
                rank: result.rank,
              },
            }
          }
          return node
        })
      }
      
      return response
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Centrality analysis failed'
      throw err
    } finally {
      loading.value = false
    }
  }

  function applyLayout(mode: LayoutMode) {
    layoutMode.value = mode
  }

  function toggleNodeSelection(nodeId: string) {
    const index = selectedNodes.value.indexOf(nodeId)
    if (index > -1) {
      selectedNodes.value.splice(index, 1)
    } else {
      selectedNodes.value.push(nodeId)
    }
  }

  function selectSingleNode(nodeId: string) {
    selectedNodes.value = [nodeId]
  }

  function clearSelection() {
    selectedNodes.value = []
  }

  function setZoomLevel(level: number) {
    zoomLevel.value = Math.max(0.1, Math.min(5, level))
  }

  function zoomIn() {
    setZoomLevel(zoomLevel.value * 1.2)
  }

  function zoomOut() {
    setZoomLevel(zoomLevel.value / 1.2)
  }

  function resetZoom() {
    zoomLevel.value = 1
  }

  function updateFilters(newFilters: Partial<GraphFilters>) {
    filters.value = { ...filters.value, ...newFilters }
  }

  function resetFilters() {
    filters.value = {
      entityTypes: [],
      relationTypes: [],
    }
  }

  function clearGraphData() {
    graphData.value = null
    selectedNodes.value = []
    centralityResults.value = []
  }

  return {
    // State
    layoutMode,
    filters,
    zoomLevel,
    selectedNodes,
    graphData,
    loading,
    error,
    centralityResults,
    // Getters
    filteredNodes,
    filteredEdges,
    nodeCount,
    edgeCount,
    selectedNodeDetails,
    // Actions
    fetchGraphData,
    runCentralityAnalysis,
    applyLayout,
    toggleNodeSelection,
    selectSingleNode,
    clearSelection,
    setZoomLevel,
    zoomIn,
    zoomOut,
    resetZoom,
    updateFilters,
    resetFilters,
    clearGraphData,
  }
})
