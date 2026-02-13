import { reactive, ref } from 'vue'
import { defineStore } from 'pinia'
import * as ingestionApi from '@/api/ingestion'
import type {
  CleaningRule,
  CleaningRuleTemplate,
  DataSource,
  DataSourcePayload,
  FileUploadPayload,
  FileUploadResponse,
  IngestionJob,
  MysqlConfig,
  MysqlImportPayload,
  PreviewPayload,
  WizardFormState,
} from '@/types/ingestion'

const DEFAULT_MYSQL_CONFIG: MysqlConfig = {
  host: '',
  port: 3306,
  database: '',
  username: '',
  password: '',
  table: '',
}

const normalizeError = (error: unknown) => {
  if (error instanceof Error) {
    return error.message
  }
  return typeof error === 'string' ? error : 'Unexpected error'
}

const createWizardState = (): WizardFormState => ({
  projectId: '',
  sourceType: 'FILE',
  selectedSourceId: undefined,
  mysql: { ...DEFAULT_MYSQL_CONFIG },
  cleaningRules: [],
})

export const useIngestionStore = defineStore('ingestion', () => {
  const sources = ref<DataSource[]>([])
  const cleaningRuleTemplates = ref<CleaningRuleTemplate[]>([])
  const jobs = ref<IngestionJob[]>([])
  const previewRows = ref<Array<Record<string, unknown>> | null>(null)
  const lastError = ref<string | null>(null)
  const loading = reactive({
    templates: false,
    sources: false,
    upload: false,
    jobs: false,
  })
  const wizardForm = ref<WizardFormState>(createWizardState())

  function setProject(projectId: string) {
    wizardForm.value.projectId = projectId
  }

  function resetWizard(projectId?: string) {
    wizardForm.value = createWizardState()
    if (projectId) {
      wizardForm.value.projectId = projectId
    }
  }

  function upsertJob(job: IngestionJob) {
    const idx = jobs.value.findIndex((entry) => entry.id === job.id)
    if (idx >= 0) {
      jobs.value[idx] = { ...jobs.value[idx], ...job }
    } else {
      jobs.value.unshift(job)
    }
  }

  async function fetchTemplates(force = false) {
    if (cleaningRuleTemplates.value.length && !force) {
      return cleaningRuleTemplates.value
    }
    loading.templates = true
    lastError.value = null
    try {
      const data = await ingestionApi.fetchCleaningRuleTemplates()
      cleaningRuleTemplates.value = data
      return data
    } catch (error) {
      lastError.value = normalizeError(error)
      throw error
    } finally {
      loading.templates = false
    }
  }

  async function fetchSources(projectId: string) {
    loading.sources = true
    lastError.value = null
    try {
      const data = await ingestionApi.listDataSources(projectId)
      sources.value = data
      return data
    } catch (error) {
      lastError.value = normalizeError(error)
      throw error
    } finally {
      loading.sources = false
    }
  }

  async function saveSource(payload: DataSourcePayload) {
    lastError.value = null
    try {
      const created = await ingestionApi.createDataSource(payload)
      sources.value = [created, ...sources.value]
      return created
    } catch (error) {
      lastError.value = normalizeError(error)
      throw error
    }
  }

  async function testMysql(payload: MysqlConfig & { projectId: string }) {
    lastError.value = null
    try {
      const result = await ingestionApi.testMysqlConnection(payload)
      return result
    } catch (error) {
      lastError.value = normalizeError(error)
      throw error
    }
  }

  function hydrateJobFromUpload(
    response: FileUploadResponse,
    projectId: string,
  ): IngestionJob | undefined {
    if (!response.jobId) return undefined
    return {
      id: response.jobId,
      projectId,
      mode: response.mode,
      status: response.status,
      progress: response.status === 'COMPLETED' ? 100 : 0,
    }
  }

  async function uploadFile(payload: FileUploadPayload) {
    loading.upload = true
    lastError.value = null
    try {
      const response = await ingestionApi.uploadFileArtifact(payload)
      previewRows.value = response.previewRows ?? null
      const job = hydrateJobFromUpload(response, payload.projectId)
      if (job) {
        upsertJob(job)
      }
      return response
    } catch (error) {
      lastError.value = normalizeError(error)
      throw error
    } finally {
      loading.upload = false
    }
  }

  async function requestPreview(payload: PreviewPayload) {
    lastError.value = null
    try {
      const rows = await ingestionApi.previewCleaningResult(payload)
      previewRows.value = rows
      return rows
    } catch (error) {
      lastError.value = normalizeError(error)
      throw error
    }
  }

  async function submitMysqlImport(payload: MysqlImportPayload) {
    lastError.value = null
    try {
      const job = await ingestionApi.submitMysqlImport(payload)
      upsertJob(job)
      return job
    } catch (error) {
      lastError.value = normalizeError(error)
      throw error
    }
  }

  async function fetchJobs(projectId: string) {
    loading.jobs = true
    lastError.value = null
    try {
      const data = await ingestionApi.fetchJobs(projectId)
      jobs.value = data
      return data
    } catch (error) {
      lastError.value = normalizeError(error)
      throw error
    } finally {
      loading.jobs = false
    }
  }

  async function refreshJob(jobId: string) {
    try {
      const job = await ingestionApi.getJob(jobId)
      upsertJob(job)
      return job
    } catch (error) {
      lastError.value = normalizeError(error)
      throw error
    }
  }

  function setCleaningRules(rules: CleaningRule[]) {
    wizardForm.value.cleaningRules = [...rules]
  }

  return {
    sources,
    cleaningRuleTemplates,
    jobs,
    previewRows,
    wizardForm,
    loading,
    lastError,
    setProject,
    resetWizard,
    setCleaningRules,
    fetchTemplates,
    fetchSources,
    saveSource,
    testMysql,
    uploadFile,
    requestPreview,
    submitMysqlImport,
    fetchJobs,
    refreshJob,
  }
})
