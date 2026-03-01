import { GraphEntityResponse } from '../entities/graph';

export interface PathStep {
  entity: GraphEntityResponse;
  relationType?: string;
}

export class PathResult {
  private readonly steps: PathStep[];
  private readonly length: number;

  constructor(steps: PathStep[]) {
    this.steps = steps;
    this.length = steps.length - 1; // Number of relations
  }

  getSteps(): PathStep[] {
    return [...this.steps];
  }

  getLength(): number {
    return this.length;
  }

  getStartEntity(): GraphEntityResponse {
    return this.steps[0].entity;
  }

  getEndEntity(): GraphEntityResponse {
    return this.steps[this.steps.length - 1].entity;
  }
}
