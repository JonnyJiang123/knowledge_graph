import { GraphEntity, GraphRelation } from '@/domain/entities/graph';

export interface EntityRepository {
  createEntity(entity: GraphEntity): Promise<GraphEntity>;
  getEntity(id: string, projectId: string): Promise<GraphEntity | null>;
  updateEntity(entity: GraphEntity): Promise<GraphEntity>;
  deleteEntity(id: string, projectId: string): Promise<boolean>;
  listEntities(
    projectId: string,
    type?: string,
    limit?: number,
    offset?: number,
  ): Promise<GraphEntity[]>;
  createRelation(relation: GraphRelation): Promise<GraphRelation>;
  getRelation(id: string, projectId: string): Promise<GraphRelation | null>;
  updateRelation(relation: GraphRelation): Promise<GraphRelation>;
  deleteRelation(id: string, projectId: string): Promise<boolean>;
  listRelations(
    projectId: string,
    type?: string,
    limit?: number,
    offset?: number,
  ): Promise<GraphRelation[]>;
  findNeighbors(
    entityId: string,
    projectId: string,
    depth: number,
  ): Promise<{ entities: GraphEntity[]; relations: GraphRelation[] }>;
  searchEntities(projectId: string, query: string, type?: string): Promise<GraphEntity[]>;
}
