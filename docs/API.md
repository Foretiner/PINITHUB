# API contract

Every client-facing response hides match scores and biometric representations. TLS and session/account authorization are required in deployment. Internal face-service routes must stay on a private network and require a service token.

## Implemented prototype routes

| Method | Path | Request / response | Behavior |
|---|---|---|---|
| GET | `/health` (API) | `200 {status, database, biometricDecisionsEnabled:false}` or `503 {status:not_ready}` | Checks database connectivity; never enables biometric decisions |
| POST | `/v1/bio/register/sessions` | Request `{consent:true, noticeVersion:string}`; response `{sessionId, nonce, challenge, expiresAt}` | Persists a short-lived session and consent notice version; creates no account |
| POST | `/v1/bio/register/sessions/{id}/frames` | Multipart `frames` (3 to 15 images), `X-Registration-Nonce` header | Checks session/nonce and forwards frames plus server-persisted challenge to the private face service; API still returns generic unavailable/retry and creates no account |
| GET | `/health` (face service) | `{status:"ok", ready:boolean, recognitionReady:boolean, mode:"research-only", biometricDecisionsEnabled:false}` | `ready` means liveness runtime/assets are present; `recognitionReady` means the local SCRFD/ArcFace assets pass checksums |
| POST | `/internal/face/analyse` | Multipart `frames`, `challenge`, `X-Face-Service-Token` | Validates images in memory and runs an experimental MediaPipe landmark + anti-spoof candidate provider. Result is research-only; no identity action is enabled |
| POST | `/internal/face/embedding` | Multipart `frame`, `X-Face-Service-Token` | Research-only local SCRFD detection, five-point alignment, and ArcFace embedding. Returns to authenticated internal caller only; no storage |

The prototype does not create a biometric subject, store an embedding, authenticate a person, return scores to the browser, or implement account recovery. The Phase 4 match/grey-zone/no-match policy is implemented for evaluation, but no benchmark-derived thresholds are configured and the policy is not wired to account enrollment. The PAD heuristics and threshold remain uncalibrated. There are no measured APCER/BPCER results or controlled attack evaluations. A response marked `LIVE` is not a validated liveness claim.

## Planned before production

- 1:N registration with evaluated thresholds and a transaction-level advisory lock covering search and insert.
- 1:1 face login with independently validated liveness, passkeys, and recovery.
- Review queue with two distinct reviewers and audited access.
- Biometric deletion and consent withdrawal routes.
- Main PinITHUB authentication integration, rate limits by account/device/network, and operational security.
- Commercial/production model and dataset rights review; current CelebA-Spoof-derived candidate is research-only.
