import { EntityRepository } from '@/domain/ports/repositories/entity_repository';
import { GraphEntity, GraphRelation } from '@/domain/entities/graph';
import { Neo4jClient } from './client';

export class Neo4jEntityRepository implements EntityRepository {
  async createEntity(entity: GraphEntity): Promise<GraphEntity> {
    const query = `
      MERGE (p:Project {id: $projectId})
      CREATE (e:Entity {
        id: $id,
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
      id: entity.id,
      projectId: entity.project_id,
      externalId: entity.external_id,
      type: entity.type,
      labels: entity.labels,
      properties: entity.properties,
    };

    const result = await Neo4jClient.executeQuery(query, params);
    if (result.length === 0) {
      throw new Error('Failed to create entity');
    }

    const entityNode = result[0].get('e');
    return this.mapToEntity(entityNode);
  }

  async getEntity(id: string, projectId: string): Promise<GraphEntity | null> {
    const query = `
      MATCH (e:Entity {id: $id, projectId: $projectId})
      RETURN e
    `;

    const params = { id, projectId };
    const result = await Neo4jClient.executeQuery(query, params);

    if (result.length === 0) {
      return null;
    }

    const entityNode = result[0].get('e');
    return this.mapToEntity(entityNode);
  }

  async updateEntity(entity: GraphEntity): Promise<GraphEntity> {
    const query = `
      MATCH (e:Entity {id: $id, projectId: $projectId})
      SET e.externalId = $externalId,
          e.type = $type,
          e.labels = $labels,
          e.properties = $properties,
          e.updatedAt = datetime()
      RETURN e
    `;

    const params = {
      id: entity.id,
      projectId: entity.project_id,
      externalId: entity.external_id,
      type: entity.type,
      labels: entity.labels,
      properties: entity.properties,
    };

    const result = await Neo4jClient.executeQuery(query, params);
    if (result.length === 0) {
      throw new Error('Failed to update entity');
    }

    const entityNode = result[0].get('e');
    return this.mapToEntity(entityNode);
  }

  async deleteEntity(id: string, projectId: string): Promise<boolean> {
    const query = `
      MATCH (e:Entity {id: $id, projectId: $projectId})
      DETACH DELETE e
      RETURN count(e) as deleted
    `;

    const params = { id, projectId };
    const result = await Neo4jClient.executeQuery(query, params);

    return result.length > 0 && result[0].get('deleted').toNumber() > 0;
  }

  async listEntities(
    projectId: string,
    type?: string,
    limit?: number,
    offset?: number,
  ): Promise<GraphEntity[]> {
    let query = `
      MATCH (e:Entity {projectId: $projectId})
    `;

    if (type) {
      query += ` WHERE e.type = $type`;
    }

    query += ` RETURN e`;

    if (limit) {
      query += ` LIMIT $limit`;
    }

    if (offset) {
      query += ` SKIP $offset`;
    }

    const params: any = { projectId };
    if (type) params.type = type;
    if (limit) params.limit = limit;
    if (offset) params.offset = offset;

    const result = await Neo4jClient.executeQuery(query, params);
    return result.map((record: any) => this.mapToEntity(record.get('e')));
  }

  async createRelation(relation: GraphRelation): Promise<GraphRelation> {
    const query = `
      MATCH (source:Entity {id: $sourceId, projectId: $projectId})
      MATCH (target:Entity {id: $targetId, projectId: $projectId})
      CREATE (source)-[r:RELATION {
        id: $id,
        projectId: $projectId,
        type: $type,
        properties: $properties,
        createdAt: datetime(),
        updatedAt: datetime()
      }]->(target)
      RETURN r, source, target
    `;

    const params = {
      id: relation.id,
      projectId: relation.project_id,
      sourceId: relation.source_id,
      targetId: relation.target_id,
      type: relation.type,
      properties: relation.properties,
    };

    const result = await Neo4jClient.executeQuery(query, params);
    if (result.length === 0) {
      throw new Error('Failed to create relation');
    }

    const relationNode = result[0].get('r');
    return this.mapToRelation(relationNode, relation.source_id, relation.target_id);
  }

  async getRelation(id: string, projectId: string): Promise<GraphRelation | null> {
    const query = `
      MATCH (source)-[r:RELATION {id: $id, projectId: $projectId}]->(target)
      RETURN r, source, target
    `;

    const params = { id, projectId };
    const result = await Neo4jClient.executeQuery(query, params);

    if (result.length === 0) {
      return null;
    }

    const relationNode = result[0].get('r');
    const sourceNode = result[0].get('source');
    const targetNode = result[0].get('target');

    return this.mapToRelation(relationNode, sourceNode.properties.id, targetNode.properties.id);
  }

  async updateRelation(relation: GraphRelation): Promise<GraphRelation> {
    const query = `
      MATCH (source)-[r:RELATION {id: $id, projectId: $projectId}]->(target)
      SET r.type = $type,
          r.properties = $properties,
          r.updatedAt = datetime()
      RETURN r
    `;

    const params = {
      id: relation.id,
      projectId: relation.project_id,
      type: relation.type,
      properties: relation.properties,
    };

    const result = await Neo4jClient.executeQuery(query, params);
    if (result.length === 0) {
      throw new Error('Failed to update relation');
    }

    const relationNode = result[0].get('r');
    return this.mapToRelation(relationNode, relation.source_id, relation.target_id);
  }

  async deleteRelation(id: string, projectId: string): Promise<boolean> {
    const query = `
      MATCH ()-[r:RELATION {id: $id, projectId: $projectId}]->()
      DELETE r
      RETURN count(r) as deleted
    `;

    const params = { id, projectId };
    const result = await Neo4jClient.executeQuery(query, params);

    return result.length > 0 && result[0].get('deleted').toNumber() > 0;
  }

  async listRelations(
    projectId: string,
    type?: string,
    limit?: number,
    offset?: number,
  ): Promise<GraphRelation[]> {
    let query = `
      MATCH (source)-[r:RELATION {projectId: $projectId}]->(target)
    `;

    if (type) {
      query += ` WHERE r.type = $type`;
    }

    query += ` RETURN r, source, target`;

    if (limit) {
      query += ` LIMIT $limit`;
    }

    if (offset) {
      query += ` SKIP $offset`;
    }

    const params: any = { projectId };
    if (type) params.type = type;
    if (limit) params.limit = limit;
    if (offset) params.offset = offset;

    const result = await Neo4jClient.executeQuery(query, params);
    return result.map((record: any) => {
      const relationNode = record.get('r');
      const sourceNode = record.get('source');
      const targetNode = record.get('target');
      return this.mapToRelation(relationNode, sourceNode.properties.id, targetNode.properties.id);
    });
  }

  async findNeighbors(
    entityId: string,
    projectId: string,
    depth: number,
  ): Promise<{ entities: GraphEntity[]; relations: GraphRelation[] }> {
    const query = `
      MATCH (start:Entity {id: $entityId, projectId: $projectId})
      MATCH path = (start)-[*1..${depth}]-(neighbor:Entity {projectId: $projectId})
      WITH DISTINCT neighbor, relationships(path) as rels
      UNWIND rels as rel
      RETURN collect(DISTINCT neighbor) as entities, collect(DISTINCT rel) as relations
    `;

    const params = { entityId, projectId };
    const result = await Neo4jClient.executeQuery(query, params);

    if (result.length === 0) {
      return { entities: [], relations: [] };
    }

    const entities = result[0].get('entities').map((entity: any) => this.mapToEntity(entity));
    const relations = result[0].get('relations').map((relation: any) => {
      // We need to get source and target IDs from the relationship
      // This is a simplified approach, in a real implementation we would match the nodes
      return this.mapToRelation(relation, '', '');
    });

    return { entities, relations };
  }

  async searchEntities(projectId: string, query: string, type?: string): Promise<GraphEntity[]> {
    const searchQuery = `
      MATCH (e:Entity {projectId: $projectId})
      WHERE e.properties CONTAINS $query OR e.externalId CONTAINS $query
      ${type ? 'AND e.type = $type' : ''}
      RETURN e
      LIMIT 100
    `;

    const params: any = { projectId, query };
    if (type) params.type = type;

    const result = await Neo4jClient.executeQuery(searchQuery, params);
    return result.map((record: any) => this.mapToEntity(record.get('e')));
  }

  private mapToEntity(node: any): GraphEntity {
    const properties = node.properties;
    return {
      id: properties.id,
      project_id: properties.projectId,
      external_id: properties.externalId,
      type: properties.type,
      labels: properties.labels || [],
      properties: properties.properties || {},
      created_at: new Date(properties.createdAt.toString()),
      updated_at: new Date(properties.updatedAt.toString()),
    };
  }

  private mapToRelation(relation: any, sourceId: string, targetId: string): GraphRelation {
    const properties = relation.properties;
    return {
      id: properties.id,
      project_id: properties.projectId,
      source_id: sourceId,
      target_id: targetId,
      type: properties.type,
      properties: properties.properties || {},
      created_at: new Date(properties.createdAt.toString()),
      updated_at: new Date(properties.updatedAt.toString()),
    };
  }
}
