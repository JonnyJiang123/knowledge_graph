export type Industry = 'FINANCE' | 'HEALTHCARE'

export interface GraphProject {
  id: string
  name: string
  industry: Industry
  status: string
  owner_id: string
  description?: string | null
  metadata?: Record<string, unknown>
  created_at?: string
  updated_at?: string
}

export interface GraphProjectListResponse {
  items: GraphProject[]
  total: number
}

export interface GraphProjectCreatePayload {
  name: string
  industry: Industry
  description?: string
  metadata?: Record<string, unknown>
}

export interface GraphEntityPayload {
  external_id: string
  type: string
  labels?: string[]
  properties?: Record<string, unknown>
}

export interface GraphRelationPayload {
  source_id: string
  target_id: string
  type: string
  properties?: Record<string, unknown>
}

export interface NeighborQueryParams {
  entityId: string
  depth?: number
  limit?: number | null
}

export interface NeighborEntity {
  id: string
  project_id: string
  external_id?: string
  type?: string
  labels?: string[]
  properties?: Record<string, unknown>
}

export interface NeighborRelation {
  id: string
  project_id: string
  source_id: string
  target_id: string
  type?: string
  properties?: Record<string, unknown>
}

export interface NeighborResponse {
  entities: NeighborEntity[]
  relations: NeighborRelation[]
}

export interface GraphEntityDraft extends GraphEntityPayload {
  id: string
  status?: 'draft' | 'saved'
}

export interface GraphRelationDraft extends GraphRelationPayload {
  id: string
  status?: 'draft' | 'saved'
}

export interface NeighborRun {
  id: string
  projectId: string
  entityId: string
  depth: number
  limit?: number | null
  result: NeighborResponse
  createdAt: string
}

// ==================== 查询与可视化类型 ====================

export interface GraphData {
  nodes: GraphNode[]
  edges: GraphEdge[]
  categories: string[]
}

export interface GraphNode {
  id: string
  name: string
  category: number
  symbolSize: number
  value: Record<string, any>
  x?: number
  y?: number
}

export interface GraphEdge {
  source: string
  target: string
  relation: string
  value?: number
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

export interface SearchEntity {
  id: string
  name: string
  type: string
  labels: string[]
  properties: Record<string, any>
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
}
