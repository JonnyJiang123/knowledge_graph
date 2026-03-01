import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import * as queryApi from '@/api/query'
import type {
  SearchRecord,
  SavedQuery,
  SearchParams,
  PathParams,
  QueryResult,
} from '@/types'

const STORAGE_KEY = 'kg_search_history'
const MAX_HISTORY = 20

export const useQueryStore = defineStore('query', () => {
  // State
  const searchHistory = ref<SearchRecord[]>(loadSearchHistory())
  const savedQueries = ref<SavedQuery[]>([])
  const currentResults = ref<QueryResult | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // Getters
  const hasResults = computed(() => {
    if (!currentResults.value) return false
    return (currentResults.value.entities?.length ?? 0) > 0 ||
           (currentResults.value.paths?.length ?? 0) > 0 ||
           Boolean(currentResults.value.answer)
  })

  const entityResults = computed(() => currentResults.value?.entities ?? [])
  const pathResults = computed(() => currentResults.value?.paths ?? [])

  // Actions
  async function searchEntities(projectId: string, params: SearchParams) {
    loading.value = true
    error.value = null
    try {
      const response = await queryApi.searchEntities(projectId, params)
      currentResults.value = {
        entities: response.entities,
        total: response.total,
      }
      addToHistory({
        query: params.keyword,
        resultCount: response.total,
      })
      return response
    } catch (err) {
      error.value = err instanceof Error ? err.message : '搜索失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function findPaths(params: PathParams) {
    loading.value = true
    error.value = null
    try {
      const paths = await queryApi.findPaths(params)
      currentResults.value = {
        paths,
        total: paths.length,
      }
      addToHistory({
        query: `路径: ${params.startId} → ${params.endId}`,
        resultCount: paths.length,
      })
      return paths
    } catch (err) {
      error.value = err instanceof Error ? err.message : '路径查找失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function naturalLanguageQuery(query: string) {
    loading.value = true
    error.value = null
    try {
      const response = await queryApi.naturalLanguageQuery(query)
      currentResults.value = {
        answer: response.answer,
        cypher: response.cypher,
        total: response.results.length,
      }
      addToHistory({
        query,
        resultCount: response.results.length,
      })
      return response
    } catch (err) {
      error.value = err instanceof Error ? err.message : '自然语言查询失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  async function saveQuery(name: string, params: SearchParams | PathParams | { query: string }) {
    let type: SavedQuery['type']
    if ('keyword' in params) {
      type = 'entity'
    } else if ('startId' in params) {
      type = 'path'
    } else {
      type = 'natural_language'
    }

    try {
      const saved = await queryApi.saveQuery(name, params, type)
      savedQueries.value.push(saved)
      return saved
    } catch (err) {
      error.value = err instanceof Error ? err.message : '保存查询失败'
      throw err
    }
  }

  async function loadSavedQueries() {
    try {
      const queries = await queryApi.getSavedQueries()
      savedQueries.value = queries
      return queries
    } catch (err) {
      error.value = err instanceof Error ? err.message : '加载保存的查询失败'
      throw err
    }
  }

  async function deleteSavedQuery(id: string) {
    try {
      await queryApi.deleteSavedQuery(id)
      savedQueries.value = savedQueries.value.filter(q => q.id !== id)
    } catch (err) {
      error.value = err instanceof Error ? err.message : '删除查询失败'
      throw err
    }
  }

  function addToHistory(record: Omit<SearchRecord, 'id' | 'timestamp'>) {
    const newRecord: SearchRecord = {
      id: generateId(),
      timestamp: new Date().toISOString(),
      ...record,
    }
    searchHistory.value = [newRecord, ...searchHistory.value].slice(0, MAX_HISTORY)
    persistSearchHistory()
  }

  function clearHistory() {
    searchHistory.value = []
    persistSearchHistory()
  }

  function clearResults() {
    currentResults.value = null
    error.value = null
  }

  // Helpers
  function loadSearchHistory(): SearchRecord[] {
    try {
      const raw = localStorage.getItem(STORAGE_KEY)
      if (!raw) return []
      return JSON.parse(raw) as SearchRecord[]
    } catch {
      return []
    }
  }

  function persistSearchHistory() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(searchHistory.value))
    } catch {
      // ignore quota errors
    }
  }

  function generateId(): string {
    return typeof crypto !== 'undefined' && crypto.randomUUID
      ? crypto.randomUUID()
      : `rec-${Math.random().toString(36).slice(2)}`
  }

  return {
    // State
    searchHistory,
    savedQueries,
    currentResults,
    loading,
    error,
    // Getters
    hasResults,
    entityResults,
    pathResults,
    // Actions
    searchEntities,
    findPaths,
    naturalLanguageQuery,
    saveQuery,
    loadSavedQueries,
    deleteSavedQuery,
    clearHistory,
    clearResults,
  }
})
