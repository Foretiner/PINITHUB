# Monday progress: setup and face service

Plan date: Monday, 26 October 2026. The PDF schedules Phase 0 and Phase 1 today.

## Phase 0 — setup and foundations

- [x] Project structure exists: `apps/web`, `apps/api`, `services/face`, and `prisma`.
- [x] Local Git repository initialized; the public remote is https://github.com/Foretiner/PINITHUB.
- [x] Local PostgreSQL/pgvector starts with Docker Compose; the API health check returned `database: ok`.
- [x] The README now documents Prisma generation, migration, API health, web startup, and the expected unavailable capture result.
- [x] CI workflow is configured for Python tests, API tests, Prisma Client generation, and TypeScript/Vite builds. It uses frozen pnpm installs and a placeholder database URL for client generation.
- [x] Supabase project with pgvector: connected on Tuesday, 27 October; migrations deployed and API health reported `database: ok`.
- [x] CI green on GitHub: the workflow passed after upload; see https://github.com/Foretiner/PINITHUB/actions/runs/40287486500.
- [x] Licence register records SCRFD/ArcFace, PAD model, and benchmark dataset terms; evaluation dataset use still depends on verified access terms.
- [ ] Under-one-hour setup acceptance: README steps are documented; a fresh-machine timing review has not been performed.

## Phase 1 — face service

- [x] Service has an authenticated internal endpoint, validates image format, size, and dimensions, handles uploads in memory, and fails closed.
- [x] Pretrained SCRFD detection, five-landmark alignment, and ArcFace 512-D embedding are implemented in `services/face/app/recognition.py`; model hashes are checked and assets remain Git-ignored.
- [x] Local face-service recognition endpoint and golden pair/15-frame timing tools are implemented.
- [ ] Golden identity tests and the 15-frame / under-2-second CPU benchmark need authorized real face frames/pairs before reporting.
- [ ] Enrollment integration and production identity decisions remain disabled until benchmark data, thresholds, and independent validation are complete. No weights or biometric samples are included in Git.

## Local verification during this work

- API unit tests: 4 passed.
- Web TypeScript check and production build: passed.
- API TypeScript check: passed after fixing the Express route parameter type guard.
- Python syntax compilation: passed.
- Full Python test execution could not be repeated in this environment because pytest is absent from the active Python installation; the temporary test dependency folder has an incompatible `pydantic_core` binary.
- Prisma Client regeneration hit a Windows `EPERM` while replacing its query-engine DLL during local checks; GitHub Actions generated Prisma Client successfully.
