import { ProjectRepository } from '@/domain/ports/repositories/project_repository';
import { GraphProject } from '@/domain/entities/graph';
import { GraphProjectModel } from './models/graphProject';

export class MySQLProjectRepository implements ProjectRepository {
  async createProject(project: GraphProject): Promise<GraphProject> {
    const projectModel = new GraphProjectModel({
      id: project.id,
      name: project.name,
      description: project.description,
      owner_id: project.owner_id,
      created_at: project.created_at,
      updated_at: project.updated_at,
    });

    await projectModel.save();
    return this.mapToDomain(projectModel);
  }

  async getProject(id: string): Promise<GraphProject | null> {
    const projectModel = await GraphProjectModel.findByPk(id);
    if (!projectModel) {
      return null;
    }
    return this.mapToDomain(projectModel);
  }

  async updateProject(project: GraphProject): Promise<GraphProject> {
    const projectModel = await GraphProjectModel.findByPk(project.id);
    if (!projectModel) {
      throw new Error('Project not found');
    }

    projectModel.name = project.name;
    projectModel.description = project.description;

    await projectModel.save();
    return this.mapToDomain(projectModel);
  }

  async deleteProject(id: string): Promise<boolean> {
    const result = await GraphProjectModel.destroy({ where: { id } });
    return result > 0;
  }

  async listProjects(ownerId?: string, limit?: number, offset?: number): Promise<GraphProject[]> {
    const query: any = {};
    if (ownerId) {
      query.where = { owner_id: ownerId };
    }
    if (limit) {
      query.limit = limit;
    }
    if (offset) {
      query.offset = offset;
    }

    const projectModels = await GraphProjectModel.findAll(query);
    return projectModels.map((model: GraphProjectModel) => this.mapToDomain(model));
  }

  async existsProject(id: string): Promise<boolean> {
    const count = await GraphProjectModel.count({ where: { id } });
    return count > 0;
  }

  private mapToDomain(model: GraphProjectModel): GraphProject {
    return {
      id: model.id,
      name: model.name,
      description: model.description,
      owner_id: model.owner_id,
      created_at: model.created_at,
      updated_at: model.updated_at,
    };
  }
}
