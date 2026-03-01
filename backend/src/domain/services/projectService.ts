import { GraphProjectCreate, GraphProjectResponse } from '../entities/graph';
import { GraphProjectModel } from '../../infrastructure/persistence/mysql/models/graphProject';

export class ProjectService {
  public async createProject(
    projectData: GraphProjectCreate,
    ownerId: string,
  ): Promise<GraphProjectResponse> {
    const project = await GraphProjectModel.create({
      name: projectData.name,
      description: projectData.description,
      owner_id: ownerId,
    });

    return this.mapToProjectResponse(project);
  }

  public async getProjectById(projectId: string): Promise<GraphProjectResponse | null> {
    const project = await GraphProjectModel.findByPk(projectId);

    if (!project) {
      return null;
    }

    return this.mapToProjectResponse(project);
  }

  public async getProjectsByOwner(ownerId: string): Promise<GraphProjectResponse[]> {
    const projects = await GraphProjectModel.findAll({
      where: { owner_id: ownerId },
      order: [['created_at', 'DESC']],
    });

    return projects.map(project => this.mapToProjectResponse(project));
  }

  public async updateProject(
    projectId: string,
    projectData: Partial<GraphProjectCreate>,
    ownerId: string,
  ): Promise<GraphProjectResponse | null> {
    const project = await GraphProjectModel.findOne({
      where: { id: projectId, owner_id: ownerId },
    });

    if (!project) {
      return null;
    }

    await project.update(projectData);

    return this.mapToProjectResponse(project);
  }

  public async deleteProject(projectId: string, ownerId: string): Promise<boolean> {
    const result = await GraphProjectModel.destroy({
      where: { id: projectId, owner_id: ownerId },
    });

    return result > 0;
  }

  public async checkProjectAccess(projectId: string, userId: string): Promise<boolean> {
    const project = await GraphProjectModel.findOne({
      where: { id: projectId, owner_id: userId },
    });

    return !!project;
  }

  private mapToProjectResponse(project: GraphProjectModel): GraphProjectResponse {
    return {
      id: project.id,
      name: project.name,
      description: project.description,
      owner_id: project.owner_id,
      created_at: project.created_at,
      updated_at: project.updated_at,
    };
  }
}
