import { ProjectRepository } from '@/domain/ports/repositories/project_repository';
import { TaskQueue } from '@/domain/ports/queue/task_queue';

export interface BackupProjectCommand {
  projectId: string;
  options?: {
    includeData?: boolean;
    includeRules?: boolean;
    storageLocation?: string;
  };
}

export class BackupProjectHandler {
  constructor(
    private readonly projectRepository: ProjectRepository,
    private readonly taskQueue: TaskQueue,
  ) {}

  async execute(command: BackupProjectCommand): Promise<{ jobId: string }> {
    // Verify project exists
    const project = await this.projectRepository.getProject(command.projectId);
    if (!project) {
      throw new Error('Project not found');
    }

    // Create backup job
    const jobId = await this.taskQueue.enqueue('backup_project', {
      projectId: command.projectId,
      options: command.options,
    });

    return { jobId };
  }
}
