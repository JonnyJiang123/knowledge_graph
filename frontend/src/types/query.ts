// 查询相关类型定义

export interface SearchRecord {
  id: string
  query: string
  timestamp: string
  resultCount: number
}

export interface SavedQuery {
  id: string
  name: string
  params: SearchParams | PathParams | { query: string }
  type: 'entity' | 'path' | 'natural_language'
  createdAt: string
}

export interface SearchParams {
  keyword: string
  entityTypes?: string[]
  limit?: number
  offset?: number
}

export interface PathParams {
  startId: string
  endId: string
  maxDepth?: number
  findAll?: boolean
}

export interface QueryResult {
  entities?: SearchEntity[]
  paths?: PathResult[]
  answer?: string
  cypher?: string
  total: number
}

export interface SearchEntity {
  id: string
  name: string
  type: string
  labels: string[]
  properties: Record<string, unknown>
  score?: number
}

export interface PathResult {
  nodes: PathNode[]
  edges: PathEdge[]
  length: number
}

export interface PathNode {
  id: string
  name: string
  type: string
}

export interface PathEdge {
  source: string
  target: string
  relation: string
  properties?: Record<string, unknown>
}

export interface NLQueryResponse {
  query: string
  cypher: string
  answer: string
  results: unknown[]
}
