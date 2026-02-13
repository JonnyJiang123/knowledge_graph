import type {
  CleaningRuleTemplate,
  DataSource,
  DataSourcePayload,
  FileUploadPayload,
  FileUploadResponse,
  IngestionJob,
  MysqlConfig,
  MysqlImportPayload,
  MysqlTestResult,
  PreviewPayload,
} from '@/types/ingestion'
import client from './client'

export async function fetchCleaningRuleTemplates() {
  const { data } = await client.get<CleaningRuleTemplate[]>('/ingestion/templates/cleaning')
  return data
}

export async function listDataSources(projectId: string) {
  const { data } = await client.get<DataSource[]>('/ingestion/sources', {
    params: { project_id: projectId },
  })
  return data
}

export async function createDataSource(payload: DataSourcePayload) {
  const { data } = await client.post<DataSource>('/ingestion/sources', payload)
  return data
}

export async function testMysqlConnection(payload: MysqlConfig & { projectId: string }) {
  const { projectId, ...rest } = payload
  const body = { ...rest, project_id: projectId }
  const { data } = await client.post<MysqlTestResult>('/ingestion/sources/mysql/test', body)
  return data
}

export async function uploadFileArtifact(payload: FileUploadPayload) {
  const formData = new FormData()
  formData.append('project_id', payload.projectId)
  if (payload.sourceId) {
    formData.append('source_id', payload.sourceId)
  }
  formData.append('file', payload.file)
  if (payload.rules?.length) {
    formData.append('rules', JSON.stringify(payload.rules))
  }

  const { data } = await client.post<FileUploadResponse>('/ingestion/upload/file', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function previewCleaningResult(payload: PreviewPayload) {
  const { data } = await client.post<Record<string, unknown>[]>(
    '/ingestion/preview',
    payload,
  )
  return data
}

export async function submitMysqlImport(payload: MysqlImportPayload) {
  const { data } = await client.post<IngestionJob>('/ingestion/mysql/import', payload)
  return data
}

export async function fetchJobs(projectId: string) {
  const { data } = await client.get<IngestionJob[]>('/ingestion/jobs', {
    params: { project_id: projectId },
  })
  return data
}

export async function getJob(jobId: string) {
  const { data } = await client.get<IngestionJob>(`/ingestion/jobs/${jobId}`)
  return data
}
