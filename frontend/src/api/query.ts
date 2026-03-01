import client from './client'
import type {
  SearchParams,
  PathParams,
  SearchEntity,
  PathResult,
  NLQueryResponse,
  SavedQuery,
} from '@/types/query'

export async function searchEntities(projectId: string, params: SearchParams): Promise<{
  entities: SearchEntity[]
  total: number
  offset: number
  limit: number
  has_more: boolean
}> {
  const { data } = await client.post('/query/search', {
    project_id: projectId,
    keyword: params.keyword,
    entity_type: params.entityTypes?.[0],
    limit: params.limit ?? 20,
    offset: params.offset ?? 0,
  })
  return data
}

export async function findPaths(params: PathParams): Promise<PathResult[]> {
  const { data } = await client.post('/query/paths', {
    start_id: params.startId,
    end_id: params.endId,
    max_depth: params.maxDepth ?? 5,
    find_all: params.findAll ?? false,
  })
  return data
}

export async function naturalLanguageQuery(query: string): Promise<NLQueryResponse> {
  const { data } = await client.post('/query/nl', { query })
  return data
}

export async function saveQuery(
  name: string,
  params: SearchParams | PathParams | { query: string },
  type: 'entity' | 'path' | 'natural_language'
): Promise<SavedQuery> {
  const { data } = await client.post('/query/saved', {
    name,
    params,
    type,
  })
  return data
}

export async function getSavedQueries(): Promise<SavedQuery[]> {
  const { data } = await client.get('/query/saved')
  return data
}

export async function deleteSavedQuery(id: string): Promise<void> {
  await client.delete(`/query/saved/${id}`)
}

export async function executeSavedQuery(id: string): Promise<unknown> {
  const { data } = await client.post(`/query/saved/${id}/execute`)
  return data
}
