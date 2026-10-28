# Mon–Wed checklist and evidence

Date: Wednesday, 28 October 2026. Phase 6 evaluation is scheduled for Saturday, 31 October. Phase 0 is complete; Phase 1 implementation is in place but golden validation is pending; Phase 2 software implementation is complete; Phase 3 is in progress. The original plan PDF's Section 1.3 is not present in this checkout, so this is a repository-derived checklist, not a verbatim transcription.

## Mon–Wed checklist

### Monday — Phase 0 foundation

- [x] App, API, face service, Prisma schema, README run instructions, and CI workflow are in the repo.
- [x] Supabase migrations and API database health were confirmed by the user.
- [x] No model training or fine-tuning; pretrained models only.
- [x] `LICENCES.md` now records model/data terms, checksums, and unresolved benchmark rights.
- [ ] Fresh-machine setup time (target under one hour) has not been measured.

**Phase 0: complete.**

### Monday — Phase 1 face pipeline

- [x] Pretrained InsightFace buffalo_l SCRFD detector and ArcFace embedding model integrated for local CPU inference; hashes are pinned in `services/face/app/recognition.py` and `services/face/download_models.ps1`.
- [x] Added an authenticated local face-service embedding endpoint and golden-pair evaluation CLI. No embedding is written to disk or sent to the browser.
- [x] Added 15-frame CPU timing CLI; it requires 15 real, local face frames.
- [ ] Run same-person, different-person, and difficult-pair golden cases on consented captures or approved benchmark data.
- [ ] Run 15-frame timing on real captures and record hardware/model/latency.

**Phase 1: implementation complete; measured validation pending.**

### Tuesday — Phase 2 liveness

- [x] Liveness challenge and capture flow, local-only submission helper, PAD metrics calculator, and protocol implemented.
- [x] InsightFace and liveness assets pass local checksum verification.
- [ ] Capture at least 20 trials of each own-face attack: printed photo, phone screen, laptop screen, replay. No trials are recorded yet.
- [ ] Calculate APCER/BPCER and intervals in the Phase 6 evaluation on Saturday.

**Phase 2: software implementation complete; trial measurements pending Phase 6.**

### Wednesday — Phase 3 and Phase 4

- [x] API and web production builds pass; API tests pass 4/4.
- [x] Python face-service and evaluation tests pass 19/19.
- [x] ONNX CPU sessions load and model checksums pass. Blank-image input returns `RETRY / NO_FACE`; this is rejection-path smoke coverage, not an accuracy result.
- [x] Phase 4 decision function implements `MATCH`, `GREY_ZONE`, `NO_MATCH`, and `RETRY`.
- [x] Added a development-score threshold derivation CLI. It derives a provisional match cutoff from impostor scores, plus a review band. The 1:N margin must be based on gallery results; there are no biometric thresholds configured yet.
- [ ] Connect recognition to enrollment/search and validate the 1:N policy; API enrollment remains unavailable.
- [ ] Obtain authorized benchmark/capture scores and derive provisional thresholds.

**Phase 3: in progress.** Local detection and embedding work; enrollment/search integration and real-data measurements remain. Phase 4 policy code is implemented locally; operational account decisions remain unavailable.

## Requested results

### Phase 1 golden tests and 15-frame CPU timing

| Evidence | Result | Status |
|---|---|---|
| Same-person golden match | Not measured; no consented or approved benchmark image pairs are available in this workspace | Pending real data |
| Different-person golden non-match | Not measured | Pending real data |
| Difficult-pair / grey-zone case | Not measured | Pending real data |
| 15-frame CPU timing | Not measured; CLI is ready, but timing requires 15 real face frames | Pending capture |

Run `evaluation/arcface_golden.py` on a consented/authorized pair CSV to save pair scores and FMR/FNMR with 95% Wilson intervals. Run `evaluation/time_arcface_15.py` with exactly 15 local frame paths. Do not substitute dummy faces or blank frames for accuracy or timing evidence. Synthetic vectors are only for the 1M-vector speed test.

### Phase 2 attack results (no samples captured)

| Own-face attack | Required | Recorded | APCER |
|---|---:|---:|---|
| Printed photo | 20 | 0 | Not measured |
| Phone screen | 20 | 0 | Not measured |
| Laptop screen | 20 | 0 | Not measured |
| Replay video | 20 | 0 | Not measured |

Capture only your own face, locally, following `evaluation/PAD_PROTOCOL.md`. No face images are committed or uploaded. A bona-fide set is also needed to measure BPCER.

## Demo and repository

- Current 20-second status video: `output/video/PINITHUB_Status_2026-10-28.mp4`. It describes project status; it is not a live biometric camera demo.
- Repository: [Foretiner/PINITHUB](https://github.com/Foretiner/PINITHUB)
- Licence register: [`docs/LICENCES.md`](LICENCES.md)
- Source code, docs, tests, and evaluation tools are committed to the repository's `main` branch. Model weights, biometric captures, and the MP4 video are excluded. The video remains a local artifact.
- The repository is now public. Source code, docs, tests, and evaluation tools are on `main`; model weights and face images are excluded. The status MP4 remains a local artifact.
- Dataset decision: LFW/AgeDB include internet-sourced images with incomplete/limited rights; CFP-FP terms are unverified. The register records this conflict with “never use scraped photos.” Do not download/use a benchmark until the official terms/access agreement and this instruction can both be followed.

