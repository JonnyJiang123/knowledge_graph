import { ProjectRepository } from '@/domain/ports/repositories/project_repository';
import { TaskQueue } from '@/domain/ports/queue/task_queue';
import { KnowledgeExtractor } from '@/domain/services/extraction/knowledge_extractor';

export interface ExtractKnowledgeCommand {
  projectId: string;
  dataPath: string;
  options?: {
    entityTypes?: string[];
    relationTypes?: string[];
    confidenceThreshold?: number;
  };
}

export class ExtractKnowledgeHandler {
  constructor(
    private readonly projectRepository: ProjectRepository,
    private readonly taskQueue: TaskQueue,
    private readonly knowledgeExtractor: KnowledgeExtractor,
  ) {}

  async execute(command: ExtractKnowledgeCommand): Promise<{ jobId: string }> {
    // Verify project exists
    const project = await this.projectRepository.getProject(command.projectId);
    if (!project) {
      throw new Error('Project not found');
    }

    // Create extraction job
    const jobId = await this.taskQueue.enqueue('extract_knowledge', {
      projectId: command.projectId,
      dataPath: command.dataPath,
      options: command.options,
    });

    return { jobId };
  }
}
