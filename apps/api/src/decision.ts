export type Candidate = { subjectId: string; similarity: number };
export type Decision = 'MATCH' | 'GREY_ZONE' | 'NO_MATCH' | 'RETRY';
export type DecisionConfig = { matchThreshold: number; reviewThreshold: number; minMargin: number };

/**
 * Phase 4 decision policy. Thresholds must come from the benchmark development
 * split; this module deliberately has no fabricated defaults. Until configured,
 * it can be exercised with explicitly supplied thresholds in local evaluation.
 */
export function loadDecisionConfig(env: NodeJS.ProcessEnv = process.env): DecisionConfig {
  const matchThreshold = Number(env.BIO_MATCH_THRESHOLD);
  const reviewThreshold = Number(env.BIO_REVIEW_THRESHOLD);
  const minMargin = Number(env.BIO_MIN_MARGIN);
  if (![matchThreshold, reviewThreshold, minMargin].every(Number.isFinite) ||
      matchThreshold <= reviewThreshold || reviewThreshold < 0 || matchThreshold > 1 || minMargin < 0 || minMargin > 1) {
    throw new Error('Benchmark-derived biometric thresholds are unset or invalid');
  }
  return { matchThreshold, reviewThreshold, minMargin };
}

export function decide(candidates: Candidate[], captureQualityAccepted: boolean, config: DecisionConfig): Decision {
  if (!captureQualityAccepted) return 'RETRY';
  const sorted = [...candidates].sort((a, b) => b.similarity - a.similarity);
  const first = sorted[0];
  if (!first) return 'NO_MATCH';
  const margin = first.similarity - (sorted[1]?.similarity ?? -1);
  if (first.similarity >= config.matchThreshold && margin >= config.minMargin) return 'MATCH';
  if (first.similarity >= config.reviewThreshold) return 'GREY_ZONE';
  return 'NO_MATCH';
}
