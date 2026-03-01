import { ProjectRepository } from '@/domain/ports/repositories/project_repository';
import { Rule } from '@/domain/services/reasoning/rule_engine';

export interface CreateRuleCommand {
  projectId: string;
  name: string;
  description: string;
  condition: string;
  action: string;
  priority: number;
  enabled: boolean;
}

export class CreateRuleHandler {
  constructor(private readonly projectRepository: ProjectRepository) {}

  async execute(command: CreateRuleCommand): Promise<Rule> {
    // Verify project exists
    const project = await this.projectRepository.getProject(command.projectId);
    if (!project) {
      throw new Error('Project not found');
    }

    // Generate rule ID
    const ruleId = `rule-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

    // Create rule
    const rule: Rule = {
      id: ruleId,
      name: command.name,
      description: command.description,
      condition: command.condition,
      action: command.action,
      priority: command.priority,
      enabled: command.enabled,
    };

    // TODO: Persist rule to database
    // For now, we'll just return the rule

    return rule;
  }
}
