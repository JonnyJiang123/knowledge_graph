import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useVisualizationStore } from '../visualization'

const mockApi = vi.hoisted(() => ({
  getVisualizationData: vi.fn(),
  runCentralityAnalysis: vi.fn(),
}))

vi.mock('@/api/graph', () => mockApi)

describe('Visualization Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    Object.values(mockApi).forEach((fn) => fn.mockReset())
  })

  it('initializes with default values', () => {
    const store = useVisualizationStore()
    expect(store.layoutMode).toBe('force')
    expect(store.zoomLevel).toBe(1)
    expect(store.selectedNodes).toEqual([])
    expect(store.graphData).toBeNull()
  })

  it('fetches graph data', async () => {
    const store = useVisualizationStore()
    const mockData = {
      nodes: [
        { id: '1', name: '阿里巴巴', category: 0, symbolSize: 50 },
        { id: '2', name: '马云', category: 1, symbolSize: 40 },
      ],
      edges: [{ source: '1', target: '2', relation: 'FOUNDED' }],
      categories: ['COMPANY', 'PERSON'],
    }
    mockApi.getVisualizationData.mockResolvedValue(mockData)

    await store.fetchGraphData('proj-1')

    expect(mockApi.getVisualizationData).toHaveBeenCalled()
    expect(store.graphData).toEqual(mockData)
  })

  it('applies different layout modes', () => {
    const store = useVisualizationStore()
    
    store.applyLayout('hierarchical')
    expect(store.layoutMode).toBe('hierarchical')
    
    store.applyLayout('circular')
    expect(store.layoutMode).toBe('circular')
  })

  it('toggles node selection', () => {
    const store = useVisualizationStore()

    store.toggleNodeSelection('node-1')
    expect(store.selectedNodes).toContain('node-1')

    store.toggleNodeSelection('node-2')
    expect(store.selectedNodes).toContain('node-2')

    // Toggle off
    store.toggleNodeSelection('node-1')
    expect(store.selectedNodes).not.toContain('node-1')
  })

  it('runs centrality analysis', async () => {
    const store = useVisualizationStore()
    const mockResult = {
      algorithm: 'pagerank',
      results: [
        { nodeId: '1', score: 0.85, rank: 1 },
        { nodeId: '2', score: 0.65, rank: 2 },
      ],
    }
    mockApi.runCentralityAnalysis.mockResolvedValue(mockResult)

    await store.runCentralityAnalysis('proj-1', 'pagerank')

    expect(mockApi.runCentralityAnalysis).toHaveBeenCalled()
    expect(store.centralityResults).toEqual(mockResult.results)
  })

  it('filters nodes correctly', () => {
    const store = useVisualizationStore()
    store.graphData = {
      nodes: [
        { id: '1', name: '阿里巴巴', category: 0 },
        { id: '2', name: '马云', category: 1 },
        { id: '3', name: '腾讯', category: 0 },
      ],
      edges: [],
      categories: ['COMPANY', 'PERSON'],
    }

    store.filters.entityTypes = ['COMPANY']
    const filtered = store.filteredNodes

    expect(filtered).toHaveLength(2)
    expect(filtered.map((n) => n.id)).toContain('1')
    expect(filtered.map((n) => n.id)).toContain('3')
  })
})
