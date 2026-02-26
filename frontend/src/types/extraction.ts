// 知识抽取相关类型定义

export type ExtractionJobStatus = 'pending' | 'running' | 'completed' | 'failed'

export interface ExtractionJob {
  id: string
  status: ExtractionJobStatus
  progress: number
  message?: string
  result?: ExtractionResult
  error?: string
  createdAt: string
  updatedAt: string
  startedAt?: string
  completedAt?: string
}

export interface ExtractionResult {
  entities: ExtractedEntity[]
  relations: ExtractedRelation[]
  statistics: {
    entityCount: number
    relationCount: number
    processingTime: number
  }
}

export interface ExtractedEntity {
  id: string
  name: string
  type: string
  confidence: number
  sourceText: string
  startPos: number
  endPos: number
}

export interface ExtractedRelation {
  id: string
  source: string
  target: string
  type: string
  confidence: number
  evidence?: string
}

export interface ExtractionParams {
  projectId: string
  source: 'text' | 'file' | 'url'
  content: string
  config?: ExtractionConfig
}

export interface ExtractionConfig {
  entityTypes?: string[]
  relationTypes?: string[]
  language?: string
  confidenceThreshold?: number
  useLLM?: boolean
  modelName?: string
}

export interface MergeParams {
  projectId: string
  sourceEntities: string[]
  targetEntity: string
  mergeRelations?: boolean
}

export interface MergePreview {
  sourceEntities: MergeEntityInfo[]
  targetEntity: MergeEntityInfo
  conflicts: MergeConflict[]
  affectedRelations: number
}

export interface MergeEntityInfo {
  id: string
  name: string
  type: string
  propertyCount: number
}

export interface MergeConflict {
  property: string
  sourceValues: unknown[]
  suggestion: unknown
}
