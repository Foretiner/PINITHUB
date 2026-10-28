# Wednesday progress: Phase 1 integration and Phase 3 readiness

Date: Wednesday, 28 October 2026.

## Completed locally

- API and web production builds passed.
- API unit tests passed 4/4.
- Face-service and evaluation tests passed 19/19; Python compile checks passed.
- Downloaded official InsightFace buffalo_l model pack; SCRFD and ArcFace ONNX files pass pinned SHA-256 checks. The pretrained weights are non-commercial research only and stay Git-ignored.
- Added SCRFD detection, five-point alignment, normalized 512-D ArcFace embeddings, an authenticated local embedding endpoint, golden-pair scoring, and 15-frame timing tools.
- Model sessions load on CPU. Blank image input returns `RETRY / NO_FACE`; this is a smoke test of the rejection path, not identity accuracy or CPU timing evidence.
- Phase 4 match/grey-zone/no-match policy and a provisional-threshold derivation script are implemented locally. No numerical thresholds are configured until genuine benchmark impostor scores and 1:N margin data exist.

## Phase status

- **Phase 0:** complete; fresh-machine setup time under one hour has not been measured.
- **Phase 1:** local pretrained pipeline and evaluation tools implemented; genuine/impostor golden tests and 15-frame real-image timing remain unmeasured.
- **Phase 2:** software implementation complete. At least 20 trials per own-face attack type and bona-fide BPCER sessions remain for Phase 6 on Saturday, 31 October.
- **Phase 3:** in progress. Recognition is not connected to account enrollment/search, and the API still fails closed.
- **Phase 4:** policy implemented; benchmark-derived thresholds and 1:N validation pending.

Do not invent scores or use synthetic/blank faces as accuracy evidence. Synthetic vectors are permitted only for the 1M-vector speed test. Keep all camera frames local; publish only de-identified outcome rows.
