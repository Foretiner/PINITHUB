import { createDecipheriv, createCipheriv, randomBytes } from 'node:crypto';

export type EncryptedTemplate = { ciphertext: Buffer; iv: Buffer; authTag: Buffer; wrappedKey: Buffer };

function masterKey(): Buffer {
  const encoded = process.env.TEMPLATE_KEY_BASE64;
  if (!encoded) throw new Error('TEMPLATE_KEY_BASE64 is required');
  const key = Buffer.from(encoded, 'base64');
  if (key.length !== 32) throw new Error('TEMPLATE_KEY_BASE64 must decode to 32 bytes');
  return key;
}

function aad(subjectId: string, modelVersion: string, purpose: string): Buffer {
  return Buffer.from(`${purpose}:${subjectId}:${modelVersion}`, 'utf8');
}

export function encryptTemplate(plaintext: Buffer, subjectId: string, modelVersion: string): EncryptedTemplate {
  const dataKey = randomBytes(32);
  const iv = randomBytes(12);
  const cipher = createCipheriv('aes-256-gcm', dataKey, iv);
  cipher.setAAD(aad(subjectId, modelVersion, 'template'));
  const ciphertext = Buffer.concat([cipher.update(plaintext), cipher.final()]);
  const authTag = cipher.getAuthTag();

  const wrapIv = randomBytes(12);
  const wrapper = createCipheriv('aes-256-gcm', masterKey(), wrapIv);
  wrapper.setAAD(aad(subjectId, modelVersion, 'data-key'));
  const wrapped = Buffer.concat([wrapper.update(dataKey), wrapper.final()]);
  const wrappedKey = Buffer.from(JSON.stringify({ iv: wrapIv.toString('base64'), tag: wrapper.getAuthTag().toString('base64'), value: wrapped.toString('base64') }));
  dataKey.fill(0);
  return { ciphertext, iv, authTag, wrappedKey };
}

export function decryptTemplate(value: EncryptedTemplate, subjectId: string, modelVersion: string): Buffer {
  const envelope = JSON.parse(value.wrappedKey.toString('utf8')) as { iv: string; tag: string; value: string };
  const unwrap = createDecipheriv('aes-256-gcm', masterKey(), Buffer.from(envelope.iv, 'base64'));
  unwrap.setAAD(aad(subjectId, modelVersion, 'data-key'));
  unwrap.setAuthTag(Buffer.from(envelope.tag, 'base64'));
  const dataKey = Buffer.concat([unwrap.update(Buffer.from(envelope.value, 'base64')), unwrap.final()]);
  try {
    const decipher = createDecipheriv('aes-256-gcm', dataKey, value.iv);
    decipher.setAAD(aad(subjectId, modelVersion, 'template'));
    decipher.setAuthTag(value.authTag);
    return Buffer.concat([decipher.update(value.ciphertext), decipher.final()]);
  } finally {
    dataKey.fill(0);
  }
}
