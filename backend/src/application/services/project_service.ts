import { ProjectRepository } from '@/domain/ports/repositories/project_repository';
import { GraphProject } from '@/domain/entities/graph';
import { v4 as uuidv4 } from 'uuid';

// Mock implementation for testing
export class MockProjectRepository implements ProjectRepository {
  private projects: GraphProject[] = [];

  async createProject(project: GraphProject): Promise<GraphProject> {
    this.projects.push(project);
    return project;
  }

  async getProject(id: string): Promise<GraphProject | null> {
    return this.projects.find(p => p.id === id) || null;
  }

  async updateProject(project: GraphProject): Promise<GraphProject> {
    const index = this.projects.findIndex(p => p.id === project.id);
    if (index !== -1) {
      this.projects[index] = project;
    }
    return project;
  }

  async deleteProject(id: string): Promise<boolean> {
    const initialLength = this.projects.length;
    this.projects = this.projects.filter(p => p.id !== id);
    return this.projects.length < initialLength;
  }

  async listProjects(ownerId?: string, limit?: number, offset?: number): Promise<GraphProject[]> {
    let filtered = this.projects;
    if (ownerId) {
      filtered = filtered.filter(p => p.owner_id === ownerId);
    }
    if (offset) {
      filtered = filtered.slice(offset);
    }
    if (limit) {
      filtered = filtered.slice(0, limit);
    }
    return filtered;
  }

  async existsProject(id: string): Promise<boolean> {
    return this.projects.some(p => p.id === id);
  }
}

export class ProjectService {
  constructor(
    private readonly projectRepository: ProjectRepository = new MockProjectRepository(),
  ) {}

  async createProject(name: string, description: string, ownerId: string): Promise<GraphProject> {
    const project: GraphProject = {
      id: uuidv4(),
      name,
      description,
      owner_id: ownerId,
      created_at: new Date(),
      updated_at: new Date(),
    };

    return this.projectRepository.createProject(project);
  }

  async getProject(id: string): Promise<GraphProject | null> {
    return this.projectRepository.getProject(id);
  }

  async updateProject(id: string, name?: string, description?: string): Promise<GraphProject> {
    const project = await this.projectRepository.getProject(id);
    if (!project) {
      throw new Error('Project not found');
    }

    const updatedProject: GraphProject = {
      ...project,
      name: name || project.name,
      description: description || project.description,
      updated_at: new Date(),
    };

    return this.projectRepository.updateProject(updatedProject);
  }

  async deleteProject(id: string): Promise<boolean> {
    return this.projectRepository.deleteProject(id);
  }

  async listProjects(ownerId?: string, limit?: number, offset?: number): Promise<GraphProject[]> {
    return this.projectRepository.listProjects(ownerId, limit, offset);
  }

  async existsProject(id: string): Promise<boolean> {
    return this.projectRepository.existsProject(id);
  }
}
