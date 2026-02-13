/// <reference types=\"vitest\" />
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createPinia, setActivePinia } from 'pinia'
import { useIngestionStore } from '../ingestion'
import * as ingestionApi from '@/api/ingestion'
import type {
  CleaningRuleTemplate,
  DataSource,
  FileUploadResponse,
  IngestionJob,
} from '@/types/ingestion'

vi.mock('@/api/ingestion', () => ({
  fetchCleaningRuleTemplates: vi.fn(),
  listDataSources: vi.fn(),
  createDataSource: vi.fn(),
  testMysqlConnection: vi.fn(),
  uploadFileArtifact: vi.fn(),
  previewCleaningResult: vi.fn(),
  submitMysqlImport: vi.fn(),
  fetchJobs: vi.fn(),
  getJob: vi.fn(),
}))

describe('useIngestionStore', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('fetches and caches cleaning rule templates', async () => {
    const templates: CleaningRuleTemplate[] = [
      { key: 'NOT_NULL', label: 'Not Null', description: 'Must provide value' },
    ]
    vi.mocked(ingestionApi.fetchCleaningRuleTemplates).mockResolvedValue(templates)

    const store = useIngestionStore()
    await store.fetchTemplates()
    expect(store.cleaningRuleTemplates).toEqual(templates)

    await store.fetchTemplates()
    expect(ingestionApi.fetchCleaningRuleTemplates).toHaveBeenCalledTimes(1)
  })

  it('saves new sources and prepends them to the list', async () => {
    const store = useIngestionStore()
    const payload = { projectId: 'proj-1', type: 'MYSQL', name: 'ODS' } as const
    const created: DataSource = {
      id: 'src-1',
      projectId: 'proj-1',
      name: 'ODS',
      type: 'MYSQL',
      status: 'ACTIVE',
      config: {},
    }
    vi.mocked(ingestionApi.createDataSource).mockResolvedValue(created)

    const result = await store.saveSource(payload)
    expect(result).toEqual(created)
    expect(store.sources[0]).toEqual(created)
  })

  it('uploads files, exposes preview rows, and tracks placeholder jobs', async () => {
    const store = useIngestionStore()
    const response: FileUploadResponse = {
      artifactId: 'art-1',
      jobId: 'job-1',
      mode: 'ASYNC',
      status: 'PENDING',
      previewRows: [{ id: 1 }],
    }
    vi.mocked(ingestionApi.uploadFileArtifact).mockResolvedValue(response)

    const file = new File(['id,name'], 'sample.csv', { type: 'text/csv' })
    await store.uploadFile({ projectId: 'proj-1', file })

    expect(store.previewRows).toEqual(response.previewRows)
    expect(store.jobs[0]?.id).toBe('job-1')
    expect(store.jobs[0]?.status).toBe('PENDING')
  })

  it('fetches jobs for a project and replaces the state', async () => {
    const store = useIngestionStore()
    const jobs: IngestionJob[] = [
      {
        id: 'job-2',
        projectId: 'proj-1',
        mode: 'SYNC',
        status: 'COMPLETED',
        progress: 100,
      },
    ]
    vi.mocked(ingestionApi.fetchJobs).mockResolvedValue(jobs)

    await store.fetchJobs('proj-1')
    expect(store.jobs).toEqual(jobs)
  })
})
