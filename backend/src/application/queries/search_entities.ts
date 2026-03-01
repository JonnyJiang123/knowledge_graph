import { ProjectRepository } from '@/domain/ports/repositories/project_repository';
import { EntityRepository } from '@/domain/ports/repositories/entity_repository';
import { GraphEntity } from '@/domain/entities/graph';

export interface SearchEntitiesQuery {
  projectId: string;
  query: string;
  type?: string;
  limit?: number;
  offset?: number;
}

export class SearchEntitiesHandler {
  constructor(
    private readonly projectRepository: ProjectRepository,
    private readonly entityRepository: EntityRepository,
  ) {}

  async execute(query: SearchEntitiesQuery): Promise<{ entities: GraphEntity[]; total: number }> {
    // Verify project exists
    const project = await this.projectRepository.getProject(query.projectId);
    if (!project) {
      throw new Error('Project not found');
    }

    // Search entities
    const entities = await this.entityRepository.searchEntities(
      query.projectId,
      query.query,
      query.type,
    );

    // Apply limit and offset
    const total = entities.length;
    const paginatedEntities = entities.slice(query.offset || 0).slice(0, query.limit || 100);

    return { entities: paginatedEntities, total };
  }
}
