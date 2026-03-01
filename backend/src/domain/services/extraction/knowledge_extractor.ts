import { NamedEntity } from '@/domain/ports/nlp/ner_extractor';

export interface ExtractionResult {
  entities: NamedEntity[];
  relations: {
    source: NamedEntity;
    target: NamedEntity;
    type: string;
  }[];
}

export class KnowledgeExtractor {
  constructor(
    private readonly tokenizer: any, // Will be replaced with Tokenizer port
    private readonly nerExtractor: any, // Will be replaced with NERExtractor port
  ) {}

  async extract(text: string): Promise<ExtractionResult> {
    // Step 1: Tokenize the text
    await this.tokenizer.tokenize(text);

    // Step 2: Extract named entities
    const entities = await this.nerExtractor.extractEntities(text);

    // Step 3: Extract relations (simplified implementation)
    const relations = this.extractRelations(entities, text);

    return {
      entities,
      relations,
    };
  }

  private extractRelations(
    entities: NamedEntity[],
    _text: string,
  ): {
    source: NamedEntity;
    target: NamedEntity;
    type: string;
  }[] {
    // Simplified relation extraction logic
    // In a real implementation, this would use dependency parsing or pattern matching
    const relations: {
      source: NamedEntity;
      target: NamedEntity;
      type: string;
    }[] = [];

    // Example: Find relations between adjacent entities
    for (let i = 0; i < entities.length - 1; i++) {
      const source = entities[i];
      const target = entities[i + 1];

      // Simple heuristic: if entities are close together, assume a relation
      if (target.start - source.end < 50) {
        relations.push({
          source,
          target,
          type: 'RELATED_TO',
        });
      }
    }

    return relations;
  }
}
