// 可视化相关类型定义

export type LayoutMode = 'force' | 'hierarchical' | 'circular'

export interface GraphFilters {
  entityTypes: string[]
  relationTypes: string[]
  minDegree?: number
  maxDegree?: number
  searchKeyword?: string
}

export interface GraphData {
  nodes: GraphNode[]
  edges: GraphEdge[]
  categories: GraphCategory[]
}

export interface GraphNode {
  id: string
  name: string
  category: number
  symbolSize: number
  value: Record<string, unknown>
  x?: number
  y?: number
  fixed?: boolean
  draggable?: boolean
}

export interface GraphEdge {
  source: string
  target: string
  relation: string
  value?: number
  lineStyle?: {
    width?: number
    curveness?: number
  }
}

export interface GraphCategory {
  name: string
  itemStyle?: {
    color?: string
  }
}

export interface FetchOptions {
  layout?: LayoutMode
  filters?: Partial<GraphFilters>
  limit?: number
}

export interface CentralityResult {
  nodeId: string
  score: number
  rank: number
}

export interface CentralityAnalysisResponse {
  algorithm: 'pagerank' | 'betweenness'
  results: CentralityResult[]
  timestamp: string
}

export interface GraphStats {
  nodeCount: number
  edgeCount: number
  categoryCount: number
  density: number
}
