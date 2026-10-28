# Wednesday progress: Phase 1 integration and Phase 3 readiness

Date: Wednesday, 28 October 2026.

## Completed locally

- API and web production builds passed; API tests passed 4/4.
- Face-service and evaluation tests passed 19/19; Python compile checks passed.
- Official InsightFace buffalo_l model pack downloaded. SCRFD and ArcFace ONNX files pass pinned SHA-256 checks. Pretrained weights remain Git-ignored and are restricted to non-commercial research.
- Added SCRFD detection, five-point alignment, normalized 512-D ArcFace embeddings, an authenticated local embedding endpoint, golden-pair scoring, and 15-frame timing tools.
- A 15-frame local camera timing run completed: 15/15 successful, 23.7053 seconds total, 1,580.35 ms mean per frame, CPUExecutionProvider, Intel64 Family 6 Model 142 Stepping 12, Python 3.11.9.
- One own-face phone-screen PAD session was submitted to the localhost service. It returned `RETRY` (reason blank), counted as non-acceptance; phone APCER is 0/1 with a 95% Wilson interval of 0–79.35%. No other attack or bona-fide PAD rows are recorded.
- Phase 4 match/grey-zone/no-match policy and a threshold-derivation script are implemented locally. No provisional numeric thresholds are configured because no authorized genuine/impostor score set or 1:N gallery margin data exists.

## Phase status

- **Phase 0:** complete; fresh-machine setup time under one hour has not been measured.
- **Phase 1:** local pretrained pipeline and CPU timing implemented/measured; genuine/impostor golden tests remain pending because no cleared image-pair set is available.
- **Phase 2:** software implemented; one phone-screen session recorded. The 20-per-category attack set and bona-fide BPCER set remain pending for Phase 6 on Saturday, 31 October.
- **Phase 3:** in progress. Recognition is not connected to account enrollment/search; the API remains fail-closed.
- **Phase 4:** policy implemented; calibrated numeric thresholds and 1:N validation remain pending.

Do not invent scores or use synthetic/blank faces as accuracy evidence. Synthetic vectors are permitted only for the 1M-vector speed test. Keep all camera frames local; publish only aggregate, de-identified outcomes.

