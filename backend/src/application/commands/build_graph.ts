import { ProjectRepository } from '@/domain/ports/repositories/project_repository';
import { EntityRepository } from '@/domain/ports/repositories/entity_repository';
import { TaskQueue } from '@/domain/ports/queue/task_queue';

export interface BuildGraphCommand {
  projectId: string;
  extractionJobId: string;
  options?: {
    mergeEntities?: boolean;
    validateRelations?: boolean;
  };
}

export class BuildGraphHandler {
  constructor(
    private readonly projectRepository: ProjectRepository,
    private readonly entityRepository: EntityRepository,
    private readonly taskQueue: TaskQueue,
  ) {}

  async execute(command: BuildGraphCommand): Promise<{ jobId: string }> {
    // Verify project exists
    const project = await this.projectRepository.getProject(command.projectId);
    if (!project) {
      throw new Error('Project not found');
    }

    // Create build job
    const jobId = await this.taskQueue.enqueue('build_graph', {
      projectId: command.projectId,
      extractionJobId: command.extractionJobId,
      options: command.options,
    });

    return { jobId };
  }
}
