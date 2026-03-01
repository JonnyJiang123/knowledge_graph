import { KnowledgeExtractor } from '@/domain/services/extraction/knowledge_extractor';
import { EntityRepository } from '@/domain/ports/repositories/entity_repository';
import { GraphEntity, GraphRelation } from '@/domain/entities/graph';
import { v4 as uuidv4 } from 'uuid';

export class ExtractionPipeline {
  constructor(
    private readonly knowledgeExtractor: KnowledgeExtractor,
    private readonly entityRepository: EntityRepository,
  ) {}

  async execute(
    file: any, // UploadFile type
    projectId: string,
  ): Promise<{ entities: GraphEntity[]; relations: GraphRelation[] }> {
    // Read file content
    const content = await file.text();

    // Extract knowledge
    const extractionResult = await this.knowledgeExtractor.extract(content);

    // Convert extracted entities to domain entities
    const entities: GraphEntity[] = [];
    for (const extractedEntity of extractionResult.entities) {
      const entity: GraphEntity = {
        id: uuidv4(),
        project_id: projectId,
        external_id: extractedEntity.text,
        type: extractedEntity.type,
        labels: [extractedEntity.type],
        properties: {
          name: extractedEntity.text,
          confidence: extractedEntity.confidence,
        },
        created_at: new Date(),
        updated_at: new Date(),
      };
      entities.push(entity);
    }

    // Convert extracted relations to domain relations
    const relations: GraphRelation[] = [];
    for (const extractedRelation of extractionResult.relations) {
      // Find source and target entities
      const sourceEntity = entities.find(e => e.external_id === extractedRelation.source.text);
      const targetEntity = entities.find(e => e.external_id === extractedRelation.target.text);

      if (sourceEntity && targetEntity) {
        const relation: GraphRelation = {
          id: uuidv4(),
          project_id: projectId,
          source_id: sourceEntity.id,
          target_id: targetEntity.id,
          type: extractedRelation.type,
          properties: {},
          created_at: new Date(),
          updated_at: new Date(),
        };
        relations.push(relation);
      }
    }

    // Save entities and relations to database
    for (const entity of entities) {
      await this.entityRepository.createEntity(entity);
    }

    for (const relation of relations) {
      await this.entityRepository.createRelation(relation);
    }

    return { entities, relations };
  }
}
