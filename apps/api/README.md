# API service

Express + TypeScript API scaffold. It exposes a database readiness endpoint and a short-lived consent-gated capture-session endpoint. The frame route deliberately fails closed until a licensed face provider and serialized 1:N search are implemented. It does not create accounts, accept client embeddings, issue login sessions, or return similarity scores.

Run `pnpm install` and `pnpm dev` from this directory after configuring the repository environment. A reachable PostgreSQL database with the migration applied is required for session creation.
