import client from './client'
import type {
  GraphProject,
  GraphProjectCreatePayload,
  GraphProjectListResponse,
  GraphEntityPayload,
  GraphRelationPayload,
  NeighborQueryParams,
  NeighborResponse,
  SearchParams,
  PathParams,
  SearchEntity,
  PathResult,
  GraphData,
} from '@/types/graph'
import type { CentralityAnalysisResponse } from '@/types/visualization'

const BASE_URL = '/graph/projects'

export async function fetchGraphProjects() {
  const { data } = await client.get<GraphProjectListResponse>(BASE_URL)
  return data
}

export async function createGraphProject(payload: GraphProjectCreatePayload) {
  const { data } = await client.post<GraphProject>(BASE_URL, payload)
  return data
}

export async function getGraphProject(projectId: string) {
  const { data } = await client.get<GraphProject>(`${BASE_URL}/${projectId}`)
  return data
}

export async function createGraphEntity(projectId: string, payload: GraphEntityPayload) {
  const { data } = await client.post(`${BASE_URL}/${projectId}/entities`, payload)
  return data
}

export async function createGraphRelation(projectId: string, payload: GraphRelationPayload) {
  const { data } = await client.post(`${BASE_URL}/${projectId}/relations`, payload)
  return data
}

export async function fetchNeighbors(
  projectId: string,
  params: NeighborQueryParams,
) {
  const { data } = await client.get<NeighborResponse>(`${BASE_URL}/${projectId}/neighbors`, {
    params: {
      entity_id: params.entityId,
      depth: params.depth,
      limit: params.limit,
    },
  })
  return data
}

// ==================== 查询与可视化 API ====================

export async function searchEntities(params: SearchParams): Promise<SearchEntity[]> {
  const { data } = await client.get<SearchEntity[]>('/graph/search', {
    params: {
      q: params.keyword,
      types: params.entityTypes?.join(','),
      limit: params.limit ?? 20,
      offset: params.offset ?? 0,
    },
  })
  return data
}

export async function findPaths(params: PathParams): Promise<PathResult[]> {
  const { data } = await client.post<PathResult[]>('/graph/paths', {
    start_id: params.startId,
    end_id: params.endId,
    max_depth: params.maxDepth ?? 5,
    find_all: params.findAll ?? false,
  })
  return data
}

export async function getVisualizationData(projectId: string): Promise<GraphData> {
  const { data } = await client.get<GraphData>('/visualization/graph', {
    params: { project_id: projectId }
  })
  return data.data
}

export async function runCentralityAnalysis(
  projectId: string,
  algorithm: 'pagerank' | 'betweenness' | 'degree'
): Promise<CentralityAnalysisResponse> {
  const { data } = await client.get<CentralityAnalysisResponse>('/visualization/centrality', {
    params: {
      project_id: projectId,
      algorithm
    }
  })
  return data
}
