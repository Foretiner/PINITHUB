import { test } from 'node:test';
import assert from 'node:assert/strict';
import { decide, loadDecisionConfig } from './decision.ts';
import { decryptTemplate, encryptTemplate } from './crypto.ts';
import { vectorLiteral } from './dedup.ts';

const policy = { matchThreshold: 0.8, reviewThreshold: 0.65, minMargin: 0.05 };

test('decision policy sends poor capture to retry and ambiguous cases to review', () => {
  assert.equal(decide([{ subjectId: 'a', similarity: 0.99 }], false, policy), 'RETRY');
  assert.equal(decide([{ subjectId: 'a', similarity: 0.83 }, { subjectId: 'b', similarity: 0.81 }], true, policy), 'GREY_ZONE');
  assert.equal(decide([{ subjectId: 'a', similarity: 0.84 }, { subjectId: 'b', similarity: 0.70 }], true, policy), 'MATCH');
  assert.equal(decide([{ subjectId: 'a', similarity: 0.3 }, { subjectId: 'b', similarity: 0.29 }], true, policy), 'NO_MATCH');
});

test('decision config fails closed when calibration is missing', () => {
  assert.throws(() => loadDecisionConfig({}), /thresholds are unset or invalid/);
});

test('vector input must be finite, unit-normalized, and exactly 512 dimensions', () => {
  const unit = new Array<number>(512).fill(1 / Math.sqrt(512));
  assert.ok(vectorLiteral(unit).startsWith('['));
  assert.throws(() => vectorLiteral([1, 2, 3]));
  assert.throws(() => vectorLiteral(new Array<number>(512).fill(0.1)));
});

test('template encryption authenticates identity and model version', () => {
  process.env.TEMPLATE_KEY_BASE64 = Buffer.alloc(32, 7).toString('base64');
  const plain = Buffer.from('ephemeral template bytes');
  const encrypted = encryptTemplate(plain, 'subject-1', 'model-v1');
  assert.deepEqual(decryptTemplate(encrypted, 'subject-1', 'model-v1'), plain);
  assert.throws(() => decryptTemplate(encrypted, 'subject-2', 'model-v1'));
  assert.throws(() => decryptTemplate(encrypted, 'subject-1', 'model-v2'));
});



