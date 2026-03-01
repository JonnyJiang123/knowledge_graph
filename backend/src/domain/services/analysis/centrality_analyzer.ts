import { GraphEntity, GraphRelation } from '@/domain/entities/graph';

export interface CentralityResult {
  entityId: string;
  centrality: number;
  entity: GraphEntity;
}

export class CentralityAnalyzer {
  /**
   * Calculate degree centrality for entities in a graph
   * Degree centrality is the number of connections an entity has
   */
  calculateDegreeCentrality(
    entities: GraphEntity[],
    relations: GraphRelation[],
  ): CentralityResult[] {
    const centralityMap = new Map<string, number>();

    // Initialize centrality for all entities to 0
    entities.forEach(entity => {
      centralityMap.set(entity.id, 0);
    });

    // Count connections for each entity
    relations.forEach(relation => {
      // Increment centrality for source entity
      if (centralityMap.has(relation.source_id)) {
        centralityMap.set(relation.source_id, centralityMap.get(relation.source_id)! + 1);
      }

      // Increment centrality for target entity
      if (centralityMap.has(relation.target_id)) {
        centralityMap.set(relation.target_id, centralityMap.get(relation.target_id)! + 1);
      }
    });

    // Convert map to array and sort by centrality (highest first)
    return Array.from(centralityMap.entries())
      .map(([entityId, centrality]) => {
        const entity = entities.find(e => e.id === entityId);
        return {
          entityId,
          centrality,
          entity: entity!,
        };
      })
      .sort((a, b) => b.centrality - a.centrality);
  }

  /**
   * Calculate betweenness centrality for entities in a graph
   * Betweenness centrality measures how often an entity lies on the shortest path between other entities
   */
  calculateBetweennessCentrality(
    entities: GraphEntity[],
    relations: GraphRelation[],
  ): CentralityResult[] {
    const betweennessMap = new Map<string, number>();
    const entityIds = entities.map(e => e.id);

    // Initialize betweenness for all entities to 0
    entityIds.forEach(id => {
      betweennessMap.set(id, 0);
    });

    // Create adjacency list for the graph
    const adjacencyList = new Map<string, string[]>();
    relations.forEach(relation => {
      if (!adjacencyList.has(relation.source_id)) {
        adjacencyList.set(relation.source_id, []);
      }
      adjacencyList.get(relation.source_id)!.push(relation.target_id);

      if (!adjacencyList.has(relation.target_id)) {
        adjacencyList.set(relation.target_id, []);
      }
      adjacencyList.get(relation.target_id)!.push(relation.source_id);
    });

    // Calculate shortest paths between all pairs of nodes
    for (const sourceId of entityIds) {
      const shortestPaths = this.findShortestPaths(sourceId, adjacencyList);

      // Calculate betweenness based on shortest paths
      for (const targetId of entityIds) {
        if (sourceId === targetId) continue;

        const path = shortestPaths.get(targetId);
        if (path && path.length > 2) {
          // Path has intermediate nodes
          // Remove source and target from path
          const intermediateNodes = path.slice(1, -1);
          intermediateNodes.forEach(nodeId => {
            betweennessMap.set(nodeId, betweennessMap.get(nodeId)! + 1);
          });
        }
      }
    }

    // Convert map to array and sort by betweenness (highest first)
    return Array.from(betweennessMap.entries())
      .map(([entityId, betweenness]) => {
        const entity = entities.find(e => e.id === entityId);
        return {
          entityId,
          centrality: betweenness,
          entity: entity!,
        };
      })
      .sort((a, b) => b.centrality - a.centrality);
  }

  /**
   * Find shortest paths from a source node to all other nodes using BFS
   */
  private findShortestPaths(
    sourceId: string,
    adjacencyList: Map<string, string[]>,
  ): Map<string, string[]> {
    const shortestPaths = new Map<string, string[]>();
    const queue: string[] = [sourceId];
    const visited = new Set<string>([sourceId]);

    shortestPaths.set(sourceId, [sourceId]);

    while (queue.length > 0) {
      const currentId = queue.shift()!;
      const neighbors = adjacencyList.get(currentId) || [];

      for (const neighborId of neighbors) {
        if (!visited.has(neighborId)) {
          visited.add(neighborId);
          const path = [...shortestPaths.get(currentId)!];
          path.push(neighborId);
          shortestPaths.set(neighborId, path);
          queue.push(neighborId);
        }
      }
    }

    return shortestPaths;
  }

  /**
   * Get top N central entities based on the specified centrality measure
   */
  getTopCentralEntities(
    entities: GraphEntity[],
    relations: GraphRelation[],
    measure: 'degree' | 'betweenness',
    limit: number = 10,
  ): CentralityResult[] {
    let centralityResults: CentralityResult[];

    switch (measure) {
      case 'degree':
        centralityResults = this.calculateDegreeCentrality(entities, relations);
        break;
      case 'betweenness':
        centralityResults = this.calculateBetweennessCentrality(entities, relations);
        break;
      default:
        centralityResults = [];
    }

    return centralityResults.slice(0, limit);
  }
}
