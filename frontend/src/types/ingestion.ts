export type DataSourceType = 'FILE' | 'MYSQL'
export type CleaningRuleType = 'NOT_NULL' | 'RANGE' | 'REGEX' | 'DEDUPE'
export type JobStatus = 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED'
export type ProcessingMode = 'SYNC' | 'ASYNC'

export interface CleaningRuleTemplate {
  key: string
  label: string
  description: string
  paramsSchema?: Record<string, unknown>
}

export interface CleaningRule {
  id?: string
  type: CleaningRuleType
  field: string
  params?: Record<string, unknown>
  severity?: 'INFO' | 'WARN' | 'ERROR'
}

export interface MysqlConfig {
  host: string
  port: number
  database: string
  username: string
  password?: string
  table?: string
  ssl?: boolean
}

export interface DataSource {
  id: string
  projectId: string
  name: string
  type: DataSourceType
  status: 'ACTIVE' | 'INACTIVE'
  config: Record<string, unknown>
  createdAt?: string
  lastUsedAt?: string | null
}

export interface DataSourcePayload {
  projectId: string
  type: DataSourceType
  name: string
  mysql?: MysqlConfig
}

export type FileFormat = 'CSV' | 'XLSX' | 'TXT' | 'PDF' | 'DOCX'

export interface UploadArtifact {
  id: string
  projectId: string
  sourceId?: string
  fileFormat: FileFormat
  originalFilename: string
  storedPath: string
  rowCount?: number
  sizeBytes?: number
  createdAt: string
}

export interface IngestionJob {
  id: string
  projectId: string
  artifactId?: string
  sourceId?: string
  mode: ProcessingMode
  status: JobStatus
  progress: number
  totalRows?: number
  processedRows?: number
  errorMessage?: string | null
  resultPath?: string | null
  createdAt?: string
  updatedAt?: string
}

export interface FileUploadResponse {
  artifactId: string
  jobId?: string | null
  mode: ProcessingMode
  status: JobStatus
  previewRows?: Array<Record<string, unknown>>
}

export interface FileUploadPayload {
  projectId: string
  sourceId?: string
  file: File
  rules?: CleaningRule[]
}

export interface PreviewPayload {
  projectId: string
  artifactId: string
  rules: CleaningRule[]
}

export interface MysqlImportPayload {
  projectId: string
  sourceId: string
  table?: string
  rules?: CleaningRule[]
}

export interface MysqlTestResult {
  ok: boolean
  message: string
  sampleRows?: Array<Record<string, unknown>>
}

export interface WizardFormState {
  projectId: string
  sourceType: DataSourceType
  selectedSourceId?: string
  mysql: MysqlConfig
  cleaningRules: CleaningRule[]
}
