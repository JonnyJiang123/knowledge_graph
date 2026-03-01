import { ProjectRepository } from '@/domain/ports/repositories/project_repository';
import { EntityRepository } from '@/domain/ports/repositories/entity_repository';

export interface MergeEntitiesCommand {
  projectId: string;
  entityIds: string[];
  targetEntityId: string;
  options?: {
    keepProperties?: string[];
    mergeRelations?: boolean;
  };
}

export class MergeEntitiesHandler {
  constructor(
    private readonly projectRepository: ProjectRepository,
    private readonly entityRepository: EntityRepository,
  ) {}

  async execute(command: MergeEntitiesCommand): Promise<{ mergedEntityId: string }> {
    // Verify project exists
    const project = await this.projectRepository.getProject(command.projectId);
    if (!project) {
      throw new Error('Project not found');
    }

    // Verify all entities exist
    for (const entityId of command.entityIds) {
      const entity = await this.entityRepository.getEntity(entityId, command.projectId);
      if (!entity) {
        throw new Error(`Entity ${entityId} not found`);
      }
    }

    // Verify target entity exists
    const targetEntity = await this.entityRepository.getEntity(
      command.targetEntityId,
      command.projectId,
    );
    if (!targetEntity) {
      throw new Error(`Target entity ${command.targetEntityId} not found`);
    }

    // TODO: Implement entity merging logic
    // 1. Get all entities to merge
    // 2. Combine properties
    // 3. Update relations to point to target entity
    // 4. Delete merged entities
    // 5. Return target entity ID

    return { mergedEntityId: command.targetEntityId };
  }
}
