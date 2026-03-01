import { GraphProject } from '@/domain/entities/graph';

export interface ProjectRepository {
  createProject(project: GraphProject): Promise<GraphProject>;
  getProject(id: string): Promise<GraphProject | null>;
  updateProject(project: GraphProject): Promise<GraphProject>;
  deleteProject(id: string): Promise<boolean>;
  listProjects(ownerId?: string, limit?: number, offset?: number): Promise<GraphProject[]>;
  existsProject(id: string): Promise<boolean>;
}
