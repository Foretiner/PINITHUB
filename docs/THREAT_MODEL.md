# Threat model (initial)

## Assets

Biometric frames, embeddings/templates, account identifiers, consent records, passkey public credentials, session challenges, review decisions, and audit events.

## Threats and required controls

| Threat | Required control | Current state |
|---|---|---|
| Forged client-supplied embeddings | Accept frames only; derive all representations server-side | API rejects template/embedding/vector form fields; no embedding provider exists |
| Photo/video replay | Random server challenge, PAD, replay controls, attack-set measurement | Challenge is issued, but not verified; PAD is absent |
| Duplicate enrollments in parallel | Serialize search-and-insert transaction and enforce DB invariants | Lock/search helpers exist; no enrollment transaction calls them |
| Template disclosure | Per-template authenticated encryption, key separation/rotation, access controls | AES-GCM envelope helper exists; not yet connected to persistence; key rotation/KMS absent |
| Gallery vector leakage | Restricted DB access, keyed/rotated vectors, monitoring | RLS migration exists; no vectors are stored; vector rotation absent |
| Account enumeration | Generic client responses and rate limits | Global API rate limit and generic unavailable response; account/login routes absent |
| Reviewer abuse | Least privilege, dual control, immutable audit records | Schema only; review routes and access policies absent |
| Secret or image committed to Git | Ignore secrets/models/data; secret scanning in CI | Ignore rules exist; secret scanning not configured |
| Unlicensed model/data use | Record exact asset, checksum, licence grant and approval | Register lists an unapproved candidate; no weights/data included |
| False matches / disparate errors | Independent evaluation, confidence intervals, subgroup reporting, non-biometric path | CSV metrics tools exist; no biometric results or fairness analysis |

## Release blockers

Do not use this prototype for real identity decisions. Before deployment, obtain legal/privacy review; verify model and data rights; implement and independently evaluate PAD; calibrate thresholds on representative consented data; integrate encryption and key management; implement and test the race-safe 1:N transaction, passkeys/recovery, deletion, review controls, audit, and monitoring; and complete security testing.
