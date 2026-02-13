import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Project, ProjectCreate, ProjectUpdate } from '@/types'
import { projectsApi } from '@/api/projects'

// 项目 Store
export const useProjectStore = defineStore('project', () => {
  const projects = ref<Project[]>([])
  const currentProject = ref<Project | null>(null)
  const loading = ref(false)
  const error = ref<string | null>(null)

  // 获取项目列表
  async function fetchProjects(): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const response = await projectsApi.list()
      projects.value = response.items
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch projects'
    } finally {
      loading.value = false
    }
  }

  // 获取单个项目
  async function fetchProject(id: string): Promise<void> {
    loading.value = true
    error.value = null
    try {
      currentProject.value = await projectsApi.get(id)
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Failed to fetch project'
    } finally {
      loading.value = false
    }
  }

  // 创建项目
  async function createProject(data: ProjectCreate): Promise<Project> {
    loading.value = true
    error.value = null
    try {
      const project = await projectsApi.create(data)
      projects.value.push(project)
      return project
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Failed to create project'
      throw e
    } finally {
      loading.value = false
    }
  }

  // 更新项目
  async function updateProject(id: string, data: ProjectUpdate): Promise<void> {
    loading.value = true
    error.value = null
    try {
      const updated = await projectsApi.update(id, data)
      const index = projects.value.findIndex((p) => p.id === id)
      if (index !== -1) {
        projects.value[index] = updated
      }
      if (currentProject.value?.id === id) {
        currentProject.value = updated
      }
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Failed to update project'
      throw e
    } finally {
      loading.value = false
    }
  }

  // 删除项目
  async function deleteProject(id: string): Promise<void> {
    loading.value = true
    error.value = null
    try {
      await projectsApi.delete(id)
      projects.value = projects.value.filter((p) => p.id !== id)
      if (currentProject.value?.id === id) {
        currentProject.value = null
      }
    } catch (e: unknown) {
      error.value = e instanceof Error ? e.message : 'Failed to delete project'
      throw e
    } finally {
      loading.value = false
    }
  }

  return {
    projects,
    currentProject,
    loading,
    error,
    fetchProjects,
    fetchProject,
    createProject,
    updateProject,
    deleteProject,
  }
})
