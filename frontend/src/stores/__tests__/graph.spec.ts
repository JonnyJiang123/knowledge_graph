import { setActivePinia, createPinia } from 'pinia'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useGraphStore } from '../graph'

const mockGraphApi = vi.hoisted(() => ({
  fetchGraphProjects: vi.fn(),
  createGraphProject: vi.fn(),
  createGraphEntity: vi.fn(),
  createGraphRelation: vi.fn(),
  fetchNeighbors: vi.fn(),
}))

vi.mock('@/api/graph', () => mockGraphApi)

describe('graph store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    Object.values(mockGraphApi).forEach((fn) => fn.mockReset())
  })

  it('initializes with default values', () => {
    const store = useGraphStore()
    expect(store.projects).toEqual([])
    expect(store.entityDrafts).toEqual([])
    expect(store.relationDrafts).toEqual([])
  })

  it('persists drafts sequentially and stops on failure', async () => {
    const store = useGraphStore()
    store.setCurrentProject('proj-1')
    store.addEntityDraft({ external_id: 'company-1', type: 'ENTERPRISE' })
    store.addRelationDraft({
      source_id: 'company-1',
      target_id: 'company-2',
      type: 'OWNS',
    })

    mockGraphApi.createGraphEntity.mockRejectedValueOnce(new Error('entity failed'))

    await expect(store.persistGraphDrafts()).rejects.toThrow('entity failed')
    expect(mockGraphApi.createGraphEntity).toHaveBeenCalledTimes(1)
    expect(mockGraphApi.createGraphRelation).not.toHaveBeenCalled()
  })

  it('persists remaining drafts after saved ones and returns summary', async () => {
    const store = useGraphStore()
    store.setCurrentProject('proj-1')
    store.addEntityDraft({ external_id: 'company-1', type: 'ENTERPRISE' })
    store.addRelationDraft({
      source_id: 'company-1',
      target_id: 'company-2',
      type: 'OWNS',
    })

    mockGraphApi.createGraphEntity.mockResolvedValue({ external_id: 'company-1' })
    mockGraphApi.createGraphRelation.mockResolvedValue({ id: 'rel-1' })

    const summary = await store.persistGraphDrafts()

    expect(summary).toEqual({ entities: 1, relations: 1 })
    expect(mockGraphApi.createGraphEntity).toHaveBeenCalledTimes(1)
    expect(mockGraphApi.createGraphRelation).toHaveBeenCalledTimes(1)
  })

  it('records neighbor runs with metadata from request parameters', async () => {
    const store = useGraphStore()
    mockGraphApi.fetchNeighbors.mockResolvedValue({
      entities: [],
      relations: [],
    })
    await store.fetchNeighbors('proj-1', { entityId: 'company-1', depth: 2, limit: 5 })
    expect(store.neighborRuns).toHaveLength(1)
    expect(store.neighborRuns[0]).toMatchObject({
      projectId: 'proj-1',
      entityId: 'company-1',
      depth: 2,
      limit: 5,
    })
  })
})
