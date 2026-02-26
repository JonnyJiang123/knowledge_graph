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
