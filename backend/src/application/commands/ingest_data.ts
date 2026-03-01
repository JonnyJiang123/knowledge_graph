import { ProjectRepository } from '@/domain/ports/repositories/project_repository';
import { TaskQueue } from '@/domain/ports/queue/task_queue';

export interface IngestDataCommand {
  projectId: string;
  dataSource: 'file' | 'database';
  sourcePath?: string; // For file source
  databaseConfig?: {
    type: string;
    connectionString: string;
    table: string;
  }; // For database source
  options?: {
    format?: string;
    delimiter?: string;
    encoding?: string;
  };
}

export class IngestDataHandler {
  constructor(
    private readonly projectRepository: ProjectRepository,
    private readonly taskQueue: TaskQueue,
  ) {}

  async execute(command: IngestDataCommand): Promise<{ jobId: string }> {
    // Verify project exists
    const project = await this.projectRepository.getProject(command.projectId);
    if (!project) {
      throw new Error('Project not found');
    }

    // Create ingestion job
    const jobId = await this.taskQueue.enqueue('ingest_data', {
      projectId: command.projectId,
      dataSource: command.dataSource,
      sourcePath: command.sourcePath,
      databaseConfig: command.databaseConfig,
      options: command.options,
    });

    return { jobId };
  }
}
