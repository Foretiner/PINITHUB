# Biometric Identity Service

A development prototype for the PinITHUB “one person, one account” project. It is fail-closed: until a reviewed face provider, measured liveness, and a transactionally safe gallery decision are implemented, it cannot enroll or authenticate anyone.

## Current status

| Area | Current state |
|---|---|
| Web | Consent acknowledgement, camera preview, challenge display, in-memory sample capture |
| API | Health check, expiring consent session, nonce verification, in-memory frame forwarding, upload limits |
| Face service | Internal token check, image validation, challenge processing, experimental anti-spoof provider, and local SCRFD + ArcFace ONNX inference |
| Database | Supabase migrations deployed; API health previously returned `database: ok` |
| Evaluation | CSV tools for FMR/FNMR, FPIR/FNIR and APCER/BPCER with Wilson 95% intervals; no results measured |
| Phase 4 policy | Pure `MATCH` / `GREY_ZONE` / `NO_MATCH` / `RETRY` policy is implemented; thresholds must come from benchmark development scores and it is not yet connected to biometric enrollment |
| Not implemented / not connected | Face embeddings are not connected to account enrollment/search; thresholds and PAD are unmeasured; template encryption is not in app flow; exact reranking and serialized 1:N registration, login, passkeys, review decisions, deletion, deployment |

The local setup and camera capture work. The face service now runs an experimental research analysis, but the API deliberately returns “Biometric enrollment is temporarily unavailable” and creates no account. Do not use real biometric data outside the approved, consented research protocol.

Current Mon–Wed checklist and evidence status: [`docs/WEDNESDAY_DELIVERABLES.md`](docs/WEDNESDAY_DELIVERABLES.md). Model/dataset terms: [`docs/LICENCES.md`](docs/LICENCES.md). A short status video is available in the local project output folder; it is not a camera or identity-performance demo.

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

6. Optional: start the face service in a fourth PowerShell window. This enables only local research analysis; it does not enable enrollment:

```powershell
cd C:\path\to\bio-identity\services\face
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
.\download_models.ps1
uvicorn app.main:app --reload --port 8001
```

Then check `http://localhost:8001/health`. With both local model assets and requirements installed, it reports `ready: true`, `mode: research-only`, and `biometricDecisionsEnabled: false`. `ready` means only that dependencies and checksummed model files are present. The candidate has not been calibrated on this project or evaluated against the planned presentation attacks. The web/API flow still does not create an account.

## Checks

- Python: `python -m pytest -q services/face/test_main.py evaluation/test_metrics.py` from the project root.
- API unit checks: `pnpm --filter pinithub-bio-api test`.
- JavaScript builds: `pnpm build` from the project root.
- CI runs Python tests, API tests, Prisma Client generation, and TypeScript/Vite builds on pushes and pull requests.

## Model and data policy

The research-only experiment downloads model assets with `services/face/download_models.ps1`; it verifies checksums and stores binaries under an ignored directory. The pretrained InsightFace buffalo_l SCRFD and ArcFace models are restricted to non-commercial research. The anti-spoof candidate was pretrained upstream on CelebA-Spoof, whose agreement limits use to non-commercial research/education. Do not use these models or derived weights in a commercial/production system. Dataset images are not included or downloaded by the setup script. No dataset images or model binaries belong in Git.

## Before real identity use

Complete the release blockers in `docs/THREAT_MODEL.md`: model and PAD review, independent accuracy/fairness evaluation, calibrated thresholds and confidence intervals, encryption and key management, race-safe 1:N search, passkeys and recovery, deletion and audit controls, operational security, and legal/privacy review. The DPDP Act and other applicable rules require a current review; this README is not legal advice.

## Evaluation workflow

Before any participant trials, read `evaluation/PAD_PROTOCOL.md`. It defines consent, local-only handling, one result per capture session, required attack categories, and the command to calculate APCER/BPCER with 95% intervals. The supplied CSV is an empty template; it contains no measured results. For recognition, `evaluation/arcface_golden.py` scores genuine/impostor image pairs from a licensed/consented image set; `evaluation/derive_thresholds.py` derives provisional 1:1 cutoffs from a development score file; `evaluation/time_arcface_15.py` times exactly 15 local face frames. Do not use scraped images, synthetic faces, or blank frames as accuracy evidence. Thresholds need independent validation and the 1:N margin needs gallery data.

