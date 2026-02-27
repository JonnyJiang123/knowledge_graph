import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useQueryStore } from '../query'

const mockApi = vi.hoisted(() => ({
  searchEntities: vi.fn(),
  findPaths: vi.fn(),
  naturalLanguageQuery: vi.fn(),
  saveQuery: vi.fn(),
  getSavedQueries: vi.fn(),
}))

vi.mock('@/api/query', () => mockApi)

describe('Query Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    Object.values(mockApi).forEach((fn) => fn.mockReset())
  })

  it('initializes with default values', () => {
    const store = useQueryStore()
    expect(store.currentResults).toBeNull()
    expect(store.loading).toBe(false)
    expect(store.searchHistory).toEqual([])
    expect(store.savedQueries).toEqual([])
  })

  it('searches entities and updates results', async () => {
    const store = useQueryStore()
    const mockResults = {
      items: [
        { id: '1', name: '阿里巴巴', type: 'COMPANY' },
        { id: '2', name: '腾讯', type: 'COMPANY' },
      ],
      total: 2,
    }
    mockApi.searchEntities.mockResolvedValue(mockResults)

    await store.searchEntities({ keyword: '科技', limit: 20 })

    expect(mockApi.searchEntities).toHaveBeenCalledWith({ keyword: '科技', limit: 20 })
    expect(store.currentResults?.entities).toEqual(mockResults.items)
    expect(store.currentResults?.total).toBe(2)
    expect(store.loading).toBe(false)
  })

  it('finds paths between entities', async () => {
    const store = useQueryStore()
    const mockPaths = [
      {
        nodes: [
          { id: '1', name: '马云', type: 'PERSON' },
          { id: '2', name: '阿里巴巴', type: 'COMPANY' },
        ],
        edges: [{ source: '1', target: '2', relation: 'FOUNDED' }],
        length: 1,
      },
    ]
    mockApi.findPaths.mockResolvedValue(mockPaths)

    await store.findPaths({ startId: '1', endId: '2', maxDepth: 3 })

    expect(mockApi.findPaths).toHaveBeenCalledWith({ startId: '1', endId: '2', maxDepth: 3 })
    expect(store.currentResults?.paths).toEqual(mockPaths)
  })

  it('handles natural language query', async () => {
    const store = useQueryStore()
    const mockResult = {
      cypher: 'MATCH (e:Entity) WHERE e.name CONTAINS "科技" RETURN e',
      answer: '找到以下科技公司',
      results: [{ id: '1', name: '阿里巴巴' }],
    }
    mockApi.naturalLanguageQuery.mockResolvedValue(mockResult)

    await store.naturalLanguageQuery('查找所有科技公司')

    expect(mockApi.naturalLanguageQuery).toHaveBeenCalledWith('查找所有科技公司')
    expect(store.currentResults?.answer).toEqual(mockResult.answer)
    expect(store.currentResults?.cypher).toEqual(mockResult.cypher)
  })

  it('saves query to savedQueries', async () => {
    const store = useQueryStore()
    mockApi.saveQuery.mockResolvedValue({ id: 'q1', name: '科技公司查询', type: 'entity', params: { keyword: '科技' } })

    await store.saveQuery('科技公司查询', { keyword: '科技' })

    expect(mockApi.saveQuery).toHaveBeenCalledWith('科技公司查询', { keyword: '科技' }, 'entity')
  })
})
