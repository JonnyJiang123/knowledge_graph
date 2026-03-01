export interface Rule {
  id: string;
  name: string;
  description: string;
  condition: string; // JSON string or DSL
  action: string; // JSON string or DSL
  priority: number;
  enabled: boolean;
}

export interface RuleExecutionResult {
  ruleId: string;
  ruleName: string;
  executed: boolean;
  triggered: boolean;
  result?: any;
  error?: string;
}

export class RuleEngine {
  private rules: Rule[] = [];

  addRule(rule: Rule): void {
    this.rules.push(rule);
    // Sort by priority (highest first)
    this.rules.sort((a, b) => b.priority - a.priority);
  }

  removeRule(ruleId: string): void {
    this.rules = this.rules.filter(rule => rule.id !== ruleId);
  }

  updateRule(rule: Rule): void {
    const index = this.rules.findIndex(r => r.id === rule.id);
    if (index !== -1) {
      this.rules[index] = rule;
      // Re-sort after update
      this.rules.sort((a, b) => b.priority - a.priority);
    }
  }

  getRules(): Rule[] {
    return [...this.rules];
  }

  async executeRules(data: any): Promise<RuleExecutionResult[]> {
    const results: RuleExecutionResult[] = [];

    for (const rule of this.rules) {
      if (!rule.enabled) {
        results.push({
          ruleId: rule.id,
          ruleName: rule.name,
          executed: false,
          triggered: false,
        });
        continue;
      }

      try {
        const conditionMet = await this.evaluateCondition(rule.condition, data);

        results.push({
          ruleId: rule.id,
          ruleName: rule.name,
          executed: true,
          triggered: conditionMet,
          result: conditionMet ? await this.executeAction(rule.action, data) : undefined,
        });
      } catch (error) {
        results.push({
          ruleId: rule.id,
          ruleName: rule.name,
          executed: true,
          triggered: false,
          error: error instanceof Error ? error.message : String(error),
        });
      }
    }

    return results;
  }

  private async evaluateCondition(condition: string, data: any): Promise<boolean> {
    // Simplified condition evaluation
    // In a real implementation, this would use a proper DSL parser
    try {
      // For demonstration, we'll just check if the condition is a valid JSON
      // and try to evaluate it as a simple expression
      const conditionObj = JSON.parse(condition);
      // Simple example: check if a property exists and meets a condition
      if (conditionObj.property && conditionObj.operator && conditionObj.value) {
        const { property, operator, value } = conditionObj;
        const propertyValue = this.getProperty(data, property);

        switch (operator) {
          case '==':
            return propertyValue === value;
          case '!=':
            return propertyValue !== value;
          case '>':
            return propertyValue > value;
          case '<':
            return propertyValue < value;
          case '>=':
            return propertyValue >= value;
          case '<=':
            return propertyValue <= value;
          case 'contains':
            return Array.isArray(propertyValue)
              ? propertyValue.includes(value)
              : String(propertyValue).includes(String(value));
          default:
            return false;
        }
      }
      return false;
    } catch (error) {
      return false;
    }
  }

  private async executeAction(action: string, data: any): Promise<any> {
    // Simplified action execution
    // In a real implementation, this would use a proper DSL parser
    try {
      const actionObj = JSON.parse(action);
      // Simple example: return a message or modify data
      if (actionObj.type === 'message') {
        return actionObj.message;
      } else if (actionObj.type === 'setProperty') {
        const { property, value } = actionObj;
        this.setProperty(data, property, value);
        return data;
      }
      return null;
    } catch (error) {
      throw new Error(
        `Failed to execute action: ${error instanceof Error ? error.message : String(error)}`,
      );
    }
  }

  private getProperty(obj: any, path: string): any {
    return path.split('.').reduce((current, key) => {
      return current && current[key] !== undefined ? current[key] : undefined;
    }, obj);
  }

  private setProperty(obj: any, path: string, value: any): void {
    const keys = path.split('.');
    const lastKey = keys.pop();
    if (!lastKey) return;

    const parent = keys.reduce((current, key) => {
      if (!current[key]) {
        current[key] = {};
      }
      return current[key];
    }, obj);

    parent[lastKey] = value;
  }
}
