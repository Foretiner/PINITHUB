# Biometric Identity Service

A development prototype for the PinITHUB “one person, one account” project. It is fail-closed: until a reviewed face provider, measured liveness, and a transactionally safe gallery decision are implemented, it cannot enroll or authenticate anyone.

## Current status

| Area | Current state |
|---|---|
| Web | Consent acknowledgement, camera preview, challenge display, in-memory sample capture |
| API | Health check, expiring consent session, nonce verification, in-memory frame forwarding, upload limits |
| Face service | Internal token check, image format/dimension validation, memory-only handling; returns unavailable without provider |
| Database | Local PostgreSQL/pgvector schema and migration; Supabase project not connected |
| Evaluation | CSV tools for FMR/FNMR, FPIR/FNIR and APCER/BPCER with Wilson 95% intervals; no results measured |
| Not implemented / not connected | Licensed face model, measured PAD, template encryption in app flow, exact reranking and serialized 1:N registration, login, passkeys, review decisions, deletion, deployment |

The local setup and camera capture work. Face analysis does not: after capture the API deliberately returns “Biometric enrollment is temporarily unavailable” and creates no account. Do not use real biometric data in this prototype.

## Local development

Prerequisites: Python 3.11+, Node.js 24+, pnpm 10+, and Docker Desktop with Linux containers enabled. In the commands below, replace `C:\path\to\bio-identity` with your project folder. This copy is at `C:\Users\Dell\Documents\Codex\2026-10-26\pi\outputs\bio-identity`.

1. In PowerShell, go to the project root and create `.env` once:

```powershell
cd C:\path\to\bio-identity
Copy-Item .env.example .env
```

For a local-only demo, `.env.example` has the local PostgreSQL URL and development-only secrets. Do not use these secrets outside your computer.

2. Start PostgreSQL and install JavaScript packages:

```powershell
docker compose up -d postgres
pnpm install
```

3. Generate Prisma Client and apply the database migration. Set the local database URL in this PowerShell session because Prisma may not load the root `.env` for the schema under `prisma/`:

```powershell
$env:DATABASE_URL = "postgresql://postgres:postgres@localhost:5432/bioidentity"
pnpm --filter pinithub-bio-api db:generate
pnpm --filter pinithub-bio-api db:migrate
```

4. Start the API in this PowerShell window and leave it open:

```powershell
pnpm --filter pinithub-bio-api dev
```

Open another PowerShell window and check API and database health:

```powershell
Invoke-RestMethod http://localhost:3000/health
```

Expected response: `status: ok`, `database: ok`, `biometricDecisionsEnabled: False`.

5. Start the web app in a third PowerShell window:

```powershell
cd C:\path\to\bio-identity
pnpm --filter pinithub-bio-web dev
```

Open the `Local` URL printed by Vite, usually `http://localhost:5173`. Tick the consent box and select **Start camera**. Allow camera access if the browser asks.

6. Optional: start the face service in a fourth PowerShell window to check its health endpoint:

```powershell
cd C:\path\to\bio-identity\services\face
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
uvicorn app.main:app --reload --port 8001
```

Then check `http://localhost:8001/health`. It reports `ready: false` until a reviewed model provider is approved and integrated. Sample capture is only a plumbing preview, not a liveness or identity demo. The unavailable response after capture is expected; no account is created.

## Checks

- Python: `python -m pytest -q services/face/test_main.py evaluation/test_metrics.py` from the project root.
- API unit checks: `pnpm --filter pinithub-bio-api test`.
- JavaScript builds: `pnpm build` from the project root.
- CI runs Python tests, API tests, Prisma Client generation, and TypeScript/Vite builds on pushes and pull requests.

## Model and data policy

Do not download or ship pretrained weights until the exact model artefact, its licence, and training-data terms have been reviewed and recorded in `docs/LICENCES.md`. The InsightFace public model zoo explicitly limits its pretrained packs to non-commercial research; software package licensing does not automatically grant commercial rights to weights. No biometric dataset is included. Use only properly licensed public data, synthetic data for speed tests, or data from people who gave informed written consent.

## Before real identity use

Complete the release blockers in `docs/THREAT_MODEL.md`: model and PAD review, independent accuracy/fairness evaluation, calibrated thresholds and confidence intervals, encryption and key management, race-safe 1:N search, passkeys and recovery, deletion and audit controls, operational security, and legal/privacy review. The DPDP Act and other applicable rules require a current review; this README is not legal advice.
