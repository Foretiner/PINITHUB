# Architecture

## Current status

This repository contains a prototype web capture screen, Express session API, FastAPI upload-validation service, PostgreSQL schema/migration, CSV evaluation tools, and Python checks. It still does not make a biometric identity decision. A licensed face provider, measured presentation-attack detection, encrypted templates, the serialized 1:N decision transaction, passkey flows, review/deletion endpoints, and deployment setup remain prerequisites.

## Intended request path

1. The browser obtains explicit biometric consent and requests a short-lived registration session.
2. The API issues a nonce and randomized liveness challenge. The browser uploads camera frames only; it must never submit an embedding or template.
3. The API sends frames to the private face service. That service validates the capture, runs liveness, and computes an embedding in memory.
4. In one serialized database transaction, the API searches the active gallery, rechecks candidates exactly, and makes a clear match / review / no-match decision using thresholds established by evaluation.
5. Only a no-match result creates a subject and stores protected template/search data. Grey-zone cases are held for review; a match is refused with generic wording.
6. Passkeys may be registered only after account registration and are used for authentication, never duplicate detection.

## Trust boundaries

- Browser: untrusted; camera capture and passkey ceremony only.
- Public API: validates sessions, limits attempts, makes decisions; never returns match scores.
- Face service: private network only, authenticated API calls; no image persistence.
- Database: no public client roles on biometric data; server-only access and row-level policies.
- Review console: least privilege and audited access; two-person approval for grey-zone decisions.

## What the prototype actually does

The web screen requests consent, previews the camera, and sends three in-memory frames to the API. The API persists a short-lived consented session, hashes its nonce, checks the nonce and expiry, and forwards frames to the internal service. The service validates image bytes and fails closed. The API then returns unavailable because no approved provider or duplicate-search transaction exists. No account or biometric template is created.

## Duplicate-search guarantee

The helper uses HNSW to retrieve a bounded candidate list. HNSW is approximate; exact distance calculation for returned candidates does not recover a true nearest face omitted by the approximate index. This design cannot honestly promise zero duplicate false negatives. Before production, measure recall against exhaustive exact search at target gallery sizes and define an exact fallback or a weaker, evidence-based guarantee for uncertain cases.
