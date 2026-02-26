import client from './client'
import type {
  GraphProject,
  GraphProjectCreatePayload,
  GraphProjectListResponse,
  GraphEntityPayload,
  GraphRelationPayload,
  NeighborQueryParams,
  NeighborResponse,
} from '@/types/graph'

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
