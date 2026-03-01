export interface NamedEntity {
  text: string;
  type: string;
  start: number;
  end: number;
  confidence?: number;
}

export interface NERExtractor {
  extractEntities(text: string): Promise<NamedEntity[]>;
  getSupportedEntityTypes(): string[];
}
