import { createHash, randomBytes, timingSafeEqual } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import dotenv from 'dotenv';
import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import rateLimit from 'express-rate-limit';
import multer from 'multer';
import { PrismaClient } from '@prisma/client';
import { z } from 'zod';
dotenv.config({ path: fileURLToPath(new URL('../../../.env', import.meta.url)) });

const app = express();
const prisma = new PrismaClient();
const port = Number(process.env.PORT ?? 3000);
const allowedOrigin = process.env.WEB_ORIGIN ?? 'http://localhost:5173';
const maxFrames = 15;
const upload = multer({ storage: multer.memoryStorage(), limits: { files: maxFrames, fileSize: 5 * 1024 * 1024 } });

app.disable('x-powered-by');
app.use(helmet());
app.use(cors({ origin: allowedOrigin, credentials: true, methods: ['GET', 'POST', 'DELETE'] }));
app.use(express.json({ limit: '64kb' }));
app.use(rateLimit({ windowMs: 60_000, limit: 30, standardHeaders: 'draft-8', legacyHeaders: false }));

app.get('/health', async (_req, res) => {
  try {
    await prisma.$queryRaw`SELECT 1`;
    res.json({ status: 'ok', database: 'ok', biometricDecisionsEnabled: false });
  } catch {
    res.status(503).json({ status: 'not_ready' });
  }
});

// Creates only a short-lived capture session. It does not create a user or biometric subject.
app.post('/v1/bio/register/sessions', async (req, res, next) => {
  try {
    const input = z.object({ consent: z.literal(true), noticeVersion: z.string().min(1).max(40) }).safeParse(req.body);
    if (!input.success) return res.status(400).json({ error: 'CONSENT_REQUIRED' });
    const id = cryptoUuid();
    const nonce = randomBytes(32).toString('base64url');
    const choices = ['turn_left_then_blink', 'turn_right_then_blink', 'blink_then_turn_left'];
    const challenge = choices[randomBytes(1)[0] % choices.length];
    const expiresAt = new Date(Date.now() + 5 * 60_000);
    await prisma.enrollmentSession.deleteMany({ where: { expiresAt: { lt: new Date() } } });
    await prisma.enrollmentSession.create({ data: {
      id, nonceHash: createHash('sha256').update(nonce).digest('hex'),
      consentNoticeVersion: input.data.noticeVersion, challenge, status: 'OPEN', expiresAt,
    } });
    res.status(201).json({ sessionId: id, nonce, challenge, expiresAt: expiresAt.toISOString() });
  } catch (error) { next(error); }
});

// Files stay in memory and are forwarded only to the private face service. This route never creates an account.
app.post('/v1/bio/register/sessions/:id/frames', upload.array('frames', maxFrames), async (req, res) => {
  const body = req.body as Record<string, unknown> | undefined;
  if (body && ('template' in body || 'embedding' in body || 'vector' in body)) {
    return res.status(400).json({ error: 'CLIENT_TEMPLATES_NOT_ACCEPTED' });
  }
  const token = req.header('x-registration-nonce');
  const sessionId = req.params.id;
  if (!token || typeof sessionId !== 'string' || !/^[0-9a-f-]{36}$/.test(sessionId)) {
    return res.status(400).json({ error: 'INVALID_SESSION' });
  }
  const session = await prisma.enrollmentSession.findUnique({ where: { id: sessionId } });
  const presented = createHash('sha256').update(token).digest();
  const stored = session ? Buffer.from(session.nonceHash, 'hex') : Buffer.alloc(presented.length);
  if (!session || stored.length !== presented.length || !timingSafeEqual(stored, presented) || session.status !== 'OPEN' || session.expiresAt <= new Date()) {
    return res.status(400).json({ error: 'INVALID_SESSION' });
  }
  const files = (req.files ?? []) as Express.Multer.File[];
  if (files.length < 3 || files.some(file => !['image/jpeg', 'image/png', 'image/webp'].includes(file.mimetype))) {
    return res.status(400).json({ error: 'INVALID_CAPTURE' });
  }
  const serviceToken = process.env.FACE_SERVICE_TOKEN;
  if (!serviceToken) return res.status(503).json({ decision: 'RETRY', message: 'Biometric enrollment is temporarily unavailable.' });
  const form = new FormData();
  for (const [index, file] of files.entries()) form.append('frames', new Blob([new Uint8Array(file.buffer).buffer as ArrayBuffer], { type: file.mimetype }), `frame-${index}.jpg`);
  try {
    const faceResponse = await fetch(`${process.env.FACE_SERVICE_URL ?? 'http://localhost:8001'}/internal/face/analyse`, {
      method: 'POST', headers: { 'X-Face-Service-Token': serviceToken }, body: form, signal: AbortSignal.timeout(10_000),
    });
    if (!faceResponse.ok) return res.status(503).json({ decision: 'RETRY', message: 'Biometric enrollment is temporarily unavailable.' });
  } catch {
    return res.status(503).json({ decision: 'RETRY', message: 'Biometric enrollment is temporarily unavailable.' });
  }
  // A successful face response still cannot create an account until the serialized gallery transaction exists.
  return res.status(503).json({ decision: 'RETRY', message: 'Biometric enrollment is temporarily unavailable.' });
});

app.use((_err: unknown, _req: express.Request, res: express.Response, _next: express.NextFunction) => {
  // Never log request bodies, frames, tokens, scores, or credentials.
  if (_err instanceof multer.MulterError) {
    const status = _err.code === 'LIMIT_FILE_SIZE' ? 413 : 400;
    return res.status(status).json({ error: 'INVALID_UPLOAD' });
  }
  res.status(500).json({ error: 'INTERNAL_ERROR' });
});

function cryptoUuid(): string {
  const b = randomBytes(16);
  b[6] = (b[6] & 0x0f) | 0x40; b[8] = (b[8] & 0x3f) | 0x80;
  const h = b.toString('hex');
  return `${h.slice(0,8)}-${h.slice(8,12)}-${h.slice(12,16)}-${h.slice(16,20)}-${h.slice(20)}`;
}

const server = app.listen(port, () => console.log(`API listening on ${port}`));
async function shutdown() {
  server.close();
  await prisma.$disconnect();
}
process.on('SIGTERM', shutdown);
process.on('SIGINT', shutdown);







