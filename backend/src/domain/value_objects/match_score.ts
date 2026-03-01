export class MatchScore {
  private readonly value: number;

  constructor(value: number) {
    if (value < 0 || value > 1) {
      throw new Error('Match score must be between 0 and 1');
    }
    this.value = value;
  }

  getValue(): number {
    return this.value;
  }

  isHigh(): boolean {
    return this.value >= 0.8;
  }

  isMedium(): boolean {
    return this.value >= 0.5 && this.value < 0.8;
  }

  isLow(): boolean {
    return this.value < 0.5;
  }
}
