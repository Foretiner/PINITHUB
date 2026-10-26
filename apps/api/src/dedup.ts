import type { Prisma } from '@prisma/client';
import type { Candidate } from './decision.ts';

const DIMENSIONS = 512;

export function vectorLiteral(input: number[]): string {
  if (input.length !== DIMENSIONS || input.some(v => !Number.isFinite(v))) throw new Error('Invalid embedding');
  const norm = Math.sqrt(input.reduce((sum, value) => sum + value * value, 0));
  if (Math.abs(norm - 1) > 0.01) throw new Error('Embedding must be unit-normalized');
  return `[${input.join(',')}]`;
}

export async function acquireRegistrationLock(tx: Prisma.TransactionClient): Promise<void> {
  // A single gallery lock is intentionally conservative; partitioning requires a reviewed concurrency design.
  await tx.$queryRaw`SELECT pg_advisory_xact_lock(9472)`;
}

export async function nearestCandidates(
  tx: Prisma.TransactionClient,
  embedding: number[],
  modelVersion: string,
  limit = 10,
): Promise<Candidate[]> {
  const vector = vectorLiteral(embedding);
  await tx.$queryRaw`SELECT set_config('hnsw.ef_search', '200', true)`;
  const rows = await tx.$queryRaw<Array<{ subject_id: string; similarity: number }>>`
    SELECT subject_id::text AS subject_id, 1 - (embedding <=> ${vector}::vector) AS similarity
    FROM face_search_vectors
    WHERE model_version = ${modelVersion}
    ORDER BY embedding <=> ${vector}::vector
    LIMIT ${Math.min(Math.max(limit, 1), 50)}
  `;
  return rows.map(row => ({ subjectId: row.subject_id, similarity: Number(row.similarity) }));
}

