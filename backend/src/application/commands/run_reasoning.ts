import { ProjectRepository } from '@/domain/ports/repositories/project_repository';
import { EntityRepository } from '@/domain/ports/repositories/entity_repository';
import { TaskQueue } from '@/domain/ports/queue/task_queue';
import { RuleEngine, RuleExecutionResult } from '@/domain/services/reasoning/rule_engine';

export interface RunReasoningCommand {
  projectId: string;
  ruleIds?: string[]; // If not provided, run all enabled rules
  entityIds?: string[]; // If not provided, run on all entities
  options?: {
    async?: boolean;
    timeout?: number;
  };
}

export class RunReasoningHandler {
  constructor(
    private readonly projectRepository: ProjectRepository,
    private readonly entityRepository: EntityRepository,
    private readonly taskQueue: TaskQueue,
    private readonly ruleEngine: RuleEngine,
  ) {}

  async execute(
    command: RunReasoningCommand,
  ): Promise<{ jobId?: string; results?: RuleExecutionResult[] }> {
    // Verify project exists
    const project = await this.projectRepository.getProject(command.projectId);
    if (!project) {
      throw new Error('Project not found');
    }

    // Check if we should run asynchronously
    if (command.options?.async) {
      // Create reasoning job
      const jobId = await this.taskQueue.enqueue('run_reasoning', {
        projectId: command.projectId,
        ruleIds: command.ruleIds,
        entityIds: command.entityIds,
        options: command.options,
      });

      return { jobId };
    } else {
      // Run synchronously
      // TODO: Implement synchronous reasoning execution
      // For now, return empty results
      return { results: [] };
    }
  }
}
