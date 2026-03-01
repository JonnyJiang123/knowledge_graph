import { v4 as uuidv4 } from 'uuid';
import { Neo4jClient } from '../../infrastructure/persistence/neo4j/client';
import {
  GraphEntityCreate,
  GraphEntityResponse,
  GraphRelationCreate,
  GraphRelationResponse,
  NeighborResponse,
} from '../entities/graph';

export class GraphService {
  public async createEntity(
    projectId: string,
    entityData: GraphEntityCreate,
    _ownerId: string,
  ): Promise<GraphEntityResponse> {
    const entityId = uuidv4();

    const query = `
      MERGE (p:Project {id: $projectId})
      CREATE (e:Entity {
        id: $entityId,
        projectId: $projectId,
        externalId: $externalId,
        type: $type,
        labels: $labels,
        properties: $properties,
        createdAt: datetime(),
        updatedAt: datetime()
      })
      CREATE (p)-[:CONTAINS]->(e)
      RETURN e
    `;

    const params = {
      projectId,
      entityId,
      externalId: entityData.external_id,
      type: entityData.type,
      labels: entityData.labels,
      properties: entityData.properties,
    };

    const result = await Neo4jClient.executeQuery(query, params);

    if (result.length === 0) {
      throw new Error('Failed to create entity');
    }

    const entity = result[0].get('e').properties;
    return this.mapToEntityResponse(entity);
  }

  public async createRelation(
    projectId: string,
    relationData: GraphRelationCreate,
    _ownerId: string,
  ): Promise<GraphRelationResponse> {
    const relationId = uuidv4();

    const query = `
      MATCH (p:Project {id: $projectId})
      MATCH (source:Entity {id: $sourceId, projectId: $projectId})
      MATCH (target:Entity {id: $targetId, projectId: $projectId})
      CREATE (source)-[r:RELATION {
        id: $relationId,
        projectId: $projectId,
        type: $type,
        properties: $properties,
        createdAt: datetime(),
        updatedAt: datetime()
      }]->(target)
      RETURN r
    `;

    const params = {
      projectId,
      relationId,
      sourceId: relationData.source_id,
      targetId: relationData.target_id,
      type: relationData.type,
      properties: relationData.properties,
    };

    const result = await Neo4jClient.executeQuery(query, params);

    if (result.length === 0) {
      throw new Error('Failed to create relation');
    }

    const relation = result[0].get('r').properties;
    return this.mapToRelationResponse(relation);
  }

  public async listNeighbors(
    projectId: string,
    entityId: string,
    depth: number = 1,
    limit?: number,
  ): Promise<NeighborResponse> {
    const query = `
      MATCH (p:Project {id: $projectId})
      MATCH (start:Entity {id: $entityId, projectId: $projectId})
      MATCH path = (start)-[*1..${depth}]-(neighbor:Entity)
      WHERE neighbor.projectId = $projectId
      WITH DISTINCT neighbor, [r in relationships(path) WHERE r.projectId = $projectId] as relations
      ${limit ? 'LIMIT $limit' : ''}
      RETURN collect(neighbor) as entities, collect(flatten(relations)) as allRelations
    `;

    const params = {
      projectId,
      entityId,
      limit,
    };

    const result = await Neo4jClient.executeQuery(query, params);

    if (result.length === 0) {
      return { entities: [], relations: [] };
    }

    const entities = result[0]
      .get('entities')
      .map((entity: any) => this.mapToEntityResponse(entity.properties));
    const relations = result[0]
      .get('allRelations')
      .flat()
      .map((relation: any) => this.mapToRelationResponse(relation.properties));

    return { entities, relations };
  }

  private mapToEntityResponse(entity: any): GraphEntityResponse {
    return {
      id: entity.id,
      project_id: entity.projectId,
      external_id: entity.externalId,
      type: entity.type,
      labels: entity.labels,
      properties: entity.properties,
      created_at: new Date(entity.createdAt),
      updated_at: new Date(entity.updatedAt),
    };
  }

  private mapToRelationResponse(relation: any): GraphRelationResponse {
    return {
      id: relation.id,
      project_id: relation.projectId,
      source_id: relation.startNodeId,
      target_id: relation.endNodeId,
      type: relation.type,
      properties: relation.properties,
      created_at: new Date(relation.createdAt),
      updated_at: new Date(relation.updatedAt),
    };
  }
}
