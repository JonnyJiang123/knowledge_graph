import { MatchScore } from '@/domain/value_objects/match_score';

export interface Symptom {
  id: string;
  name: string;
  description: string;
  severity: 'mild' | 'moderate' | 'severe';
}

export interface Disease {
  id: string;
  name: string;
  description: string;
  symptoms: string[]; // Array of symptom IDs
  treatments: string[];
}

export interface SymptomDiseaseMatch {
  disease: Disease;
  score: MatchScore;
  matchingSymptoms: Symptom[];
}

export class SymptomDiseaseMatcher {
  /**
   * Match symptoms to diseases based on symptom overlap
   */
  matchSymptomsToDiseases(symptoms: Symptom[], diseases: Disease[]): SymptomDiseaseMatch[] {
    const matches: SymptomDiseaseMatch[] = [];

    const symptomMap = new Map<string, Symptom>();
    symptoms.forEach(symptom => {
      symptomMap.set(symptom.id, symptom);
    });

    diseases.forEach(disease => {
      const matchingSymptoms: Symptom[] = [];

      // Find matching symptoms
      disease.symptoms.forEach(symptomId => {
        const symptom = symptomMap.get(symptomId);
        if (symptom) {
          matchingSymptoms.push(symptom);
        }
      });

      // Calculate match score
      const scoreValue = matchingSymptoms.length / disease.symptoms.length;
      const score = new MatchScore(scoreValue);

      // Only add matches with non-zero score
      if (scoreValue > 0) {
        matches.push({
          disease,
          score,
          matchingSymptoms,
        });
      }
    });

    // Sort matches by score (highest first)
    return matches.sort((a, b) => b.score.getValue() - a.score.getValue());
  }

  /**
   * Get top N disease matches for given symptoms
   */
  getTopMatches(
    symptoms: Symptom[],
    diseases: Disease[],
    limit: number = 5,
  ): SymptomDiseaseMatch[] {
    const matches = this.matchSymptomsToDiseases(symptoms, diseases);
    return matches.slice(0, limit);
  }

  /**
   * Calculate similarity between two symptoms
   */
  calculateSymptomSimilarity(symptom1: Symptom, symptom2: Symptom): number {
    // Simple string similarity using Levenshtein distance
    const distance = this.levenshteinDistance(
      symptom1.name.toLowerCase(),
      symptom2.name.toLowerCase(),
    );
    const maxLength = Math.max(symptom1.name.length, symptom2.name.length);
    return 1 - distance / maxLength;
  }

  /**
   * Calculate Levenshtein distance between two strings
   */
  private levenshteinDistance(a: string, b: string): number {
    const matrix: number[][] = [];

    // Initialize matrix
    for (let i = 0; i <= b.length; i++) {
      matrix[i] = [i];
    }
    for (let j = 0; j <= a.length; j++) {
      matrix[0][j] = j;
    }

    // Fill matrix
    for (let i = 1; i <= b.length; i++) {
      for (let j = 1; j <= a.length; j++) {
        if (b.charAt(i - 1) === a.charAt(j - 1)) {
          matrix[i][j] = matrix[i - 1][j - 1];
        } else {
          matrix[i][j] = Math.min(
            matrix[i - 1][j - 1] + 1, // substitution
            matrix[i][j - 1] + 1, // insertion
            matrix[i - 1][j] + 1, // deletion
          );
        }
      }
    }

    return matrix[b.length][a.length];
  }
}
