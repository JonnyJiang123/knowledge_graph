import client from './client'
import type {
  ExtractionJob,
  ExtractionParams,
  MergeParams,
  MergePreview,
} from '@/types/extraction'

export async function createExtractionJob(params: ExtractionParams): Promise<ExtractionJob> {
  const { data } = await client.post('/extraction/jobs', params)
  return data
}

export async function getExtractionJob(jobId: string): Promise<ExtractionJob> {
  const { data } = await client.get(`/extraction/jobs/${jobId}`)
  return data
}

export async function listExtractionJobs(projectId?: string): Promise<ExtractionJob[]> {
  const { data } = await client.get('/extraction/jobs', {
    params: projectId ? { project_id: projectId } : undefined,
  })
  return data
}

export async function cancelExtractionJob(jobId: string): Promise<void> {
  await client.post(`/extraction/jobs/${jobId}/cancel`)
}

export async function getMergePreview(params: MergeParams): Promise<MergePreview> {
  const { data } = await client.post('/extraction/merge/preview', params)
  return data
}

export async function mergeEntities(params: MergeParams): Promise<void> {
  await client.post('/extraction/merge', params)
}

export async function extractFromText(
  projectId: string,
  text: string,
  config?: ExtractionParams['config']
): Promise<ExtractionJob> {
  return createExtractionJob({
    projectId,
    source: 'text',
    content: text,
    config,
  })
}

export async function extractFromUrl(
  projectId: string,
  url: string,
  config?: ExtractionParams['config']
): Promise<ExtractionJob> {
  return createExtractionJob({
    projectId,
    source: 'url',
    content: url,
    config,
  })
}
