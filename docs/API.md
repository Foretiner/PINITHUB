# API contract

Every client-facing response hides match scores and biometric representations. TLS and session/account authorization are required in deployment. Internal face-service routes must stay on a private network and require a service token.

## Implemented prototype routes

| Method | Path | Request / response | Behavior |
|---|---|---|---|
| GET | `/health` | `200 {status, database, biometricDecisionsEnabled:false}` or `503 {status:not_ready}` | Checks database connectivity; does not claim biometrics are ready |
| POST | `/v1/bio/register/sessions` | Request `{consent:true, noticeVersion:string}`; response `{sessionId, nonce, challenge, expiresAt}` | Persists a short-lived session and consent notice version; no account is created |
| POST | `/v1/bio/register/sessions/{id}/frames` | Multipart `frames` (3 to 15 images), `X-Registration-Nonce` header | Checks session/nonce and forwards in-memory frames to private face service; returns generic `503 RETRY` until provider and transaction are implemented |
| GET | `/health` (face service) | `{status:"ok", ready:false}` | Readiness remains false until a reviewed provider exists |
| POST | `/internal/face/analyse` | Multipart `frames`, `X-Face-Service-Token` | Validates bytes, size, format, and dimensions in memory; returns `503` because analysis is unavailable |

The prototype deliberately does not create a biometric subject, store an embedding, authenticate a person, return similarity scores, or implement account recovery.

## Planned before production

- 1:N registration with evaluated thresholds and a transaction-level advisory lock covering search and insert.
- 1:1 face login with liveness, passkeys, and recovery.
- Review queue with two distinct reviewers and audited access.
- Biometric deletion and consent withdrawal routes.
- Main PinITHUB authentication integration, rate limits by account/device/network, and operational security.
