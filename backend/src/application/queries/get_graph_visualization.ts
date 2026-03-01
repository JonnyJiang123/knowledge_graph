import { ProjectRepository } from '@/domain/ports/repositories/project_repository';
import { EntityRepository } from '@/domain/ports/repositories/entity_repository';
import { GraphEntity, GraphRelation } from '@/domain/entities/graph';

export interface GetGraphVisualizationQuery {
  projectId: string;
  options?: {
    entityIds?: string[];
    relationTypes?: string[];
    depth?: number;
    limit?: number;
  };
}

export interface GraphVisualizationData {
  nodes: Array<{
    id: string;
    label: string;
    type: string;
    properties: Record<string, any>;
  }>;
  edges: Array<{
    id: string;
    source: string;
    target: string;
    label: string;
    type: string;
    properties: Record<string, any>;
  }>;
}

export class GetGraphVisualizationHandler {
  constructor(
    private readonly projectRepository: ProjectRepository,
    private readonly entityRepository: EntityRepository,
  ) {}

  async execute(query: GetGraphVisualizationQuery): Promise<GraphVisualizationData> {
    // Verify project exists
    const project = await this.projectRepository.getProject(query.projectId);
    if (!project) {
      throw new Error('Project not found');
    }

    let entities: GraphEntity[] = [];
    let relations: GraphRelation[] = [];

    if (query.options?.entityIds && query.options.entityIds.length > 0) {
      // Get specified entities and their neighbors
      for (const entityId of query.options.entityIds) {
        const entity = await this.entityRepository.getEntity(entityId, query.projectId);
        if (entity) {
          entities.push(entity);

          const depth = query.options?.depth || 1;
          const neighbors = await this.entityRepository.findNeighbors(
            entityId,
            query.projectId,
            depth,
          );
          entities.push(...neighbors.entities);
          relations.push(...neighbors.relations);
        }
      }
    } else {
      // Get all entities (with limit)
      const limit = query.options?.limit || 100;
      entities = await this.entityRepository.listEntities(query.projectId, undefined, limit);

      // Get relations for these entities
      for (const entity of entities) {
        const neighbors = await this.entityRepository.findNeighbors(entity.id, query.projectId, 1);
        relations.push(...neighbors.relations);
      }
    }

    // Filter relations by type if specified
    if (query.options?.relationTypes && query.options.relationTypes.length > 0) {
      relations = relations.filter(rel => query.options!.relationTypes!.includes(rel.type));
    }

    // Convert to visualization format
    const nodes = entities.map(entity => ({
      id: entity.id,
      label: entity.properties.name || entity.id,
      type: entity.type,
      properties: entity.properties,
    }));

    const edges = relations.map(relation => ({
      id: relation.id,
      source: relation.source_id,
      target: relation.target_id,
      label: relation.type,
      type: relation.type,
      properties: relation.properties,
    }));

    return { nodes, edges };
  }
}
