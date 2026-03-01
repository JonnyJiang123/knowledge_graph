import { SearchEntitiesHandler } from '../queries/search_entities';
import { NaturalLanguageQueryHandler } from '../queries/natural_language_query';
import { FindPathsHandler } from '../queries/find_paths';
import { GetGraphVisualizationHandler } from '../queries/get_graph_visualization';

export class QueryService {
  constructor(
    private readonly searchEntitiesHandler: SearchEntitiesHandler,
    private readonly naturalLanguageQueryHandler: NaturalLanguageQueryHandler,
    private readonly findPathsHandler: FindPathsHandler,
    private readonly getGraphVisualizationHandler: GetGraphVisualizationHandler,
  ) {}

  async searchEntities(
    projectId: string,
    query: string,
    type?: string,
    limit?: number,
    offset?: number,
  ) {
    return this.searchEntitiesHandler.execute({
      projectId,
      query,
      type,
      limit,
      offset,
    });
  }

  async naturalLanguageQuery(
    projectId: string,
    query: string,
    options?: {
      limit?: number;
    },
  ) {
    return this.naturalLanguageQueryHandler.execute({
      projectId,
      query,
      options,
    });
  }

  async findPaths(
    projectId: string,
    sourceEntityId: string,
    targetEntityId: string,
    maxDepth?: number,
    limit?: number,
  ) {
    return this.findPathsHandler.execute({
      projectId,
      sourceEntityId,
      targetEntityId,
      maxDepth,
      limit,
    });
  }

  async getGraphVisualization(
    projectId: string,
    options?: {
      entityIds?: string[];
      relationTypes?: string[];
      depth?: number;
      limit?: number;
    },
  ) {
    return this.getGraphVisualizationHandler.execute({
      projectId,
      options,
    });
  }
}
