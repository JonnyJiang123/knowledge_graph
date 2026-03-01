import { reactive, ref } from 'vue'
import { defineStore } from 'pinia'
import * as graphApi from '@/api/graph'
import type {
  GraphProject,
  GraphProjectCreatePayload,
  GraphEntityDraft,
  GraphEntityPayload,
  GraphRelationDraft,
  GraphRelationPayload,
  NeighborQueryParams,
  NeighborRun,
  NeighborResponse,
} from '@/types/graph'

const STORAGE_KEY = 'kg_neighbor_runs'

const normalizeError = (error: unknown) => {
  if (error instanceof Error) return error.message
  return typeof error === 'string' ? error : 'Unexpected error'
}

const createDraftId = () =>
  typeof crypto !== 'undefined' && crypto.randomUUID
    ? crypto.randomUUID()
    : `draft-${Math.random().toString(36).slice(2)}`

const loadNeighborRuns = (): NeighborRun[] => {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return []
    return JSON.parse(raw) as NeighborRun[]
  } catch {
    return []
  }
}

export const useGraphStore = defineStore('graph', () => {
  const projects = ref<GraphProject[]>([])
  const currentProjectId = ref<string>('')
  const entityDrafts = ref<GraphEntityDraft[]>([])
  const relationDrafts = ref<GraphRelationDraft[]>([])
  const neighborRuns = ref<NeighborRun[]>(loadNeighborRuns())
  const lastError = ref<string | null>(null)
  const loading = reactive({
    projects: false,
    persist: false,
    neighbors: false,
  })

  function persistNeighborRuns() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(neighborRuns.value))
    } catch {
      // ignore quota errors
    }
  }

  function setCurrentProject(projectId: string) {
    currentProjectId.value = projectId
  }

  function resetDrafts() {
    entityDrafts.value = []
    relationDrafts.value = []
  }

  function addEntityDraft(partial?: Partial<GraphEntityPayload>) {
    entityDrafts.value.push({
      id: createDraftId(),
      external_id: partial?.external_id ?? '',
      type: partial?.type ?? '',
      labels: partial?.labels ?? [],
      properties: partial?.properties ?? {},
      status: 'draft',
    })
  }

  function updateEntityDraft(id: string, patch: Partial<GraphEntityPayload>) {
    const draft = entityDrafts.value.find((entry) => entry.id === id)
    if (!draft) return
    Object.assign(draft, patch)
  }

  function removeEntityDraft(id: string) {
    entityDrafts.value = entityDrafts.value.filter((draft) => draft.id !== id)
  }

  function addRelationDraft(partial?: Partial<GraphRelationPayload>) {
    relationDrafts.value.push({
      id: createDraftId(),
      source_id: partial?.source_id ?? '',
      target_id: partial?.target_id ?? '',
      type: partial?.type ?? '',
      properties: partial?.properties ?? {},
      status: 'draft',
    })
  }

  function updateRelationDraft(id: string, patch: Partial<GraphRelationPayload>) {
    const draft = relationDrafts.value.find((entry) => entry.id === id)
    if (!draft) return
    Object.assign(draft, patch)
  }

  function removeRelationDraft(id: string) {
    relationDrafts.value = relationDrafts.value.filter((draft) => draft.id !== id)
  }

  async function loadProjects(force = false) {
    if (projects.value.length && !force) {
      return projects.value
    }
    loading.projects = true
    lastError.value = null
    try {
      const response = await graphApi.fetchGraphProjects()
      projects.value = response.items
      if (!currentProjectId.value && response.items.length > 0 && response.items[0]) {
        currentProjectId.value = response.items[0].id
      }
      return response.items
    } catch (error) {
      lastError.value = normalizeError(error)
      throw error
    } finally {
      loading.projects = false
    }
  }

  async function saveProject(payload: GraphProjectCreatePayload) {
    loading.persist = true
    lastError.value = null
    try {
      const project = await graphApi.createGraphProject(payload)
      projects.value = [project, ...projects.value]
      currentProjectId.value = project.id
      return project
    } catch (error) {
      lastError.value = normalizeError(error)
      throw error
    } finally {
      loading.persist = false
    }
  }

  async function persistEntityDraft(id: string) {
    const draft = entityDrafts.value.find((entry) => entry.id === id)
    if (!draft) throw new Error('Draft not found')
    if (!currentProjectId.value) throw new Error('Select a project first')
    loading.persist = true
    lastError.value = null
    try {
      const payload: GraphEntityPayload = {
        external_id: draft.external_id,
        type: draft.type,
        labels: draft.labels,
        properties: draft.properties,
      }
      const result = await graphApi.createGraphEntity(currentProjectId.value, payload)
      draft.status = 'saved'
      draft.external_id = result.external_id ?? draft.external_id
      return result
    } catch (error) {
      lastError.value = normalizeError(error)
      throw error
    } finally {
      loading.persist = false
    }
  }

  async function persistRelationDraft(id: string) {
    const draft = relationDrafts.value.find((entry) => entry.id === id)
    if (!draft) throw new Error('Draft not found')
    if (!currentProjectId.value) throw new Error('Select a project first')
    loading.persist = true
    lastError.value = null
    try {
      const payload: GraphRelationPayload = {
        source_id: draft.source_id,
        target_id: draft.target_id,
        type: draft.type,
        properties: draft.properties,
      }
      const result = await graphApi.createGraphRelation(currentProjectId.value, payload)
      draft.status = 'saved'
      return result
    } catch (error) {
      lastError.value = normalizeError(error)
      throw error
    } finally {
      loading.persist = false
    }
  }

  async function persistGraphDrafts() {
    let entitiesPersisted = 0
    let relationsPersisted = 0
    for (const draft of entityDrafts.value) {
      if (draft.status === 'saved') continue
      await persistEntityDraft(draft.id)
      entitiesPersisted += 1
    }
    for (const draft of relationDrafts.value) {
      if (draft.status === 'saved') continue
      await persistRelationDraft(draft.id)
      relationsPersisted += 1
    }
    return { entities: entitiesPersisted, relations: relationsPersisted }
  }

  async function fetchNeighbors(projectId: string, params: NeighborQueryParams) {
    loading.neighbors = true
    lastError.value = null
    try {
      const response = await graphApi.fetchNeighbors(projectId, params)
      recordNeighborRun(projectId, params, response)
      return response
    } catch (error) {
      lastError.value = normalizeError(error)
      throw error
    } finally {
      loading.neighbors = false
    }
  }

  function recordNeighborRun(
    projectId: string,
    params: NeighborQueryParams,
    result: NeighborResponse,
  ) {
    const run: NeighborRun = {
      id: createDraftId(),
      projectId,
      entityId: params.entityId,
      depth: params.depth ?? 1,
      limit: params.limit,
      result,
      createdAt: new Date().toISOString(),
    }
    neighborRuns.value = [run, ...neighborRuns.value].slice(0, 20)
    persistNeighborRuns()
  }

  function clearNeighborRuns() {
    neighborRuns.value = []
    persistNeighborRuns()
  }

  return {
    projects,
    currentProjectId,
    entityDrafts,
    relationDrafts,
    neighborRuns,
    loading,
    lastError,
    setCurrentProject,
    resetDrafts,
    addEntityDraft,
    updateEntityDraft,
    removeEntityDraft,
    addRelationDraft,
    updateRelationDraft,
    removeRelationDraft,
    loadProjects,
    saveProject,
    persistEntityDraft,
    persistRelationDraft,
    persistGraphDrafts,
    fetchNeighbors,
    clearNeighborRuns,
  }
})
