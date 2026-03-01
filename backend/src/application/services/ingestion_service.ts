import { IngestDataHandler } from '../commands/ingest_data';
import { ExtractKnowledgeHandler } from '../commands/extract_knowledge';
import { BuildGraphHandler } from '../commands/build_graph';

export class IngestionService {
  constructor(
    private readonly ingestDataHandler: IngestDataHandler,
    private readonly extractKnowledgeHandler: ExtractKnowledgeHandler,
    private readonly buildGraphHandler: BuildGraphHandler,
  ) {}

  async processData(
    projectId: string,
    dataSource: 'file' | 'database',
    sourcePath?: string,
    databaseConfig?: {
      type: string;
      connectionString: string;
      table: string;
    },
    options?: {
      format?: string;
      delimiter?: string;
      encoding?: string;
      extract?: boolean;
      build?: boolean;
      entityTypes?: string[];
      relationTypes?: string[];
      confidenceThreshold?: number;
      mergeEntities?: boolean;
      validateRelations?: boolean;
    },
  ): Promise<{ jobId: string; extractJobId?: string; buildJobId?: string }> {
    // Ingest data
    const ingestResult = await this.ingestDataHandler.execute({
      projectId,
      dataSource,
      sourcePath,
      databaseConfig,
      options,
    });

    const result: { jobId: string; extractJobId?: string; buildJobId?: string } = {
      jobId: ingestResult.jobId,
    };

    // Extract knowledge if requested
    if (options?.extract) {
      const extractResult = await this.extractKnowledgeHandler.execute({
        projectId,
        dataPath: sourcePath!,
        options: {
          entityTypes: options.entityTypes,
          relationTypes: options.relationTypes,
          confidenceThreshold: options.confidenceThreshold,
        },
      });
      result.extractJobId = extractResult.jobId;

      // Build graph if requested
      if (options?.build) {
        const buildResult = await this.buildGraphHandler.execute({
          projectId,
          extractionJobId: extractResult.jobId,
          options: {
            mergeEntities: options.mergeEntities,
            validateRelations: options.validateRelations,
          },
        });
        result.buildJobId = buildResult.jobId;
      }
    }

    return result;
  }
}
