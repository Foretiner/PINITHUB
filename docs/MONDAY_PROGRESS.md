# Monday progress: setup and face service

Plan date: Monday, 26 October 2026. The PDF schedules Phase 0 and Phase 1 today.

## Phase 0 — setup and foundations

- [x] Project structure exists: `apps/web`, `apps/api`, `services/face`, and `prisma`.
- [x] Local Git repository initialized; the public remote is https://github.com/Foretiner/PINITHUB.
- [x] Local PostgreSQL/pgvector starts with Docker Compose; the API health check returned `database: ok`.
- [x] The README now documents Prisma generation, migration, API health, web startup, and the expected unavailable capture result.
- [x] CI workflow is configured for Python tests, API tests, Prisma Client generation, and TypeScript/Vite builds. It uses frozen pnpm installs and a placeholder database URL for client generation.
- [ ] Supabase project with pgvector: not configured; requires a Supabase project/account and credentials. Current database is local PostgreSQL/pgvector.
- [x] CI green on GitHub: the workflow passed after upload; see https://github.com/Foretiner/PINITHUB/actions/runs/40287486500.
- [ ] Licence register: started in `LICENCES.md`; no face detector, recognition model, liveness model, or evaluation dataset is approved yet.
- [ ] Under-one-hour setup acceptance: README steps are documented; a fresh-machine timing review has not been performed.

## Phase 1 — face service

- [x] Service has an authenticated internal endpoint, validates image format, size, and dimensions, handles uploads in memory, and fails closed.
- [ ] Face-specific quality checks, detection, alignment, embedding, and cross-frame consistency are not implemented.
- [ ] Golden identity tests and the 15-frame / under-2-second CPU benchmark are not run.
- [ ] Phase 1 is blocked on selecting a legally reviewed model and properly licensed/consented evaluation data. No weights or biometric samples are included.

## Local verification during this work

- API unit tests: 4 passed.
- Web TypeScript check and production build: passed.
- API TypeScript check: passed after fixing the Express route parameter type guard.
- Python syntax compilation: passed.
- Full Python test execution could not be repeated in this environment because pytest is absent from the active Python installation; the temporary test dependency folder has an incompatible `pydantic_core` binary.
- Prisma Client regeneration hit a Windows `EPERM` while replacing its query-engine DLL during local checks; GitHub Actions generated Prisma Client successfully.

