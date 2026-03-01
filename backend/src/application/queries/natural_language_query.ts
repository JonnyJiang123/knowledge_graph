import { ProjectRepository } from '@/domain/ports/repositories/project_repository';
import { EntityRepository } from '@/domain/ports/repositories/entity_repository';
import { GraphEntity, GraphRelation } from '@/domain/entities/graph';

export interface NaturalLanguageQuery {
  projectId: string;
  query: string;
  options?: {
    limit?: number;
  };
}

export class NaturalLanguageQueryHandler {
  constructor(
    private readonly projectRepository: ProjectRepository,
    private readonly entityRepository: EntityRepository,
  ) {}

  async execute(
    query: NaturalLanguageQuery,
  ): Promise<{ entities: GraphEntity[]; relations: GraphRelation[] }> {
    // Verify project exists
    const project = await this.projectRepository.getProject(query.projectId);
    if (!project) {
      throw new Error('Project not found');
    }

    // TODO: Implement NL to Cypher translation
    // For now, we'll just search entities
    const entities = await this.entityRepository.searchEntities(query.projectId, query.query);

    // Get relations between found entities
    const relations: GraphRelation[] = [];
    for (let i = 0; i < entities.length; i++) {
      const entity = entities[i];
      const neighbors = await this.entityRepository.findNeighbors(entity.id, query.projectId, 1);
      relations.push(...neighbors.relations);
    }

    return { entities, relations };
  }
}
