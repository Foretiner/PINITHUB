# Tuesday progress: liveness v1 research integration

Plan date: Tuesday, 27 October 2026. The PDF assigns Phase 2 today.

## Implemented locally

- [x] API forwards the server-stored registration challenge to the private face service.
- [x] Face service authenticates its internal token, rejects unknown challenges, and validates image bytes, dimensions, format, size, and frame count in memory.
- [x] Added an experimental server-side pipeline using MediaPipe Face Landmarker and Open Model Zoo `anti-spoof-mn3` (CPU ONNX). It derives provisional head-turn/blink signals and combines them with the model's bona-fide score.
- [x] Added checksum verification for both model assets. Binaries are local and Git-ignored.
- [x] Added challenge policy tests and internal route tests. These check code paths, not biometric performance.
- [x] Added a local webcam capture helper, localhost-only session submission helper, research PAD protocol, empty results CSV template, and CLI for APCER/BPCER by attack type with 95% Wilson intervals. The metrics CLI enforces unique session rows and planned attack categories.
- [x] Supabase migrations and API health were previously confirmed by the user.
- [x] User approved CelebA-Spoof-related research use only. No dataset images were downloaded and no weights were fine-tuned; the upstream checkpoint is a baseline.

## Phase 2 software status: complete; performance evaluation is Phase 6

The liveness software and evaluation workflow are prepared. No bona-fide or presentation-attack trial has been recorded, so APCER/BPCER are unavailable pending Phase 6 on Saturday, 31 October. A synthetic no-face smoke test returned `RETRY`; that confirms only the no-face rejection path. Do not describe this as validated liveness.

The user approved research-only use. The baseline is already trained upstream; no local training or fine-tuning was done. Do not include dataset images/model binaries or derived weights in the public repository. This candidate cannot be used commercially or in production under the current data-use decision.

## Checks

- API unit tests: 4 passed. API TypeScript and web production builds passed; the web build includes 10-frame challenge capture.
- Face-service endpoint and liveness tests: passed in the previous work session (12 tests). Synthetic no-face model inference returned `RETRY`; health reported `biometricDecisionsEnabled: false`.
- Evaluation tests: 5 passed, including duplicate-session rejection and metric output. Liveness policy tests: 6 passed. Capture and submit helper CLI help checks passed; camera hardware capture was not run here.
- Running the CLI on `evaluation/pad_results_template.csv` returns null rates with zero sample counts, as expected.
- Python compile check and model checksums passed in the previous work session.

## Phase 6 evaluation checklist

1. Have consented participants complete bona-fide capture sessions and the four controlled attacks in `evaluation/PAD_PROTOCOL.md`: printed photo, phone screen, laptop screen, and replay.
2. Enter one outcome per session into a local copy of `evaluation/pad_results_template.csv`; keep names/images out of the CSV and public repo.
3. Calculate and independently review APCER/BPCER and confidence intervals; document sample counts, devices, conditions, retries, and limitations. Do not tune thresholds using the same final evaluation sessions.
4. Keep enrollment unavailable until the planned identity/gallery integration and independent validation are complete; decision policy code is implemented locally.

