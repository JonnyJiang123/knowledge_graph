import client from './client'
import type { Project, ProjectCreate, ProjectUpdate, ProjectListResponse } from '@/types'

// 项目 API
export const projectsApi = {
  // 创建项目
  async create(data: ProjectCreate): Promise<Project> {
    const response = await client.post<Project>('/projects', data)
    return response.data
  },

  // 获取项目列表
  async list(): Promise<ProjectListResponse> {
    const response = await client.get<ProjectListResponse>('/projects')
    return response.data
  },

  // 获取单个项目
  async get(id: string): Promise<Project> {
    const response = await client.get<Project>(`/projects/${id}`)
    return response.data
  },

  // 更新项目
  async update(id: string, data: ProjectUpdate): Promise<Project> {
    const response = await client.patch<Project>(`/projects/${id}`, data)
    return response.data
  },

  // 删除项目
  async delete(id: string): Promise<void> {
    await client.delete(`/projects/${id}`)
  },
}
