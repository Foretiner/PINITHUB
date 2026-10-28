# Mon–Wed checklist and evidence

Date: Wednesday, 28 October 2026. Phase 6 evaluation is scheduled for Saturday, 31 October. This is a repository-derived checklist because the original plan PDF's Section 1.3 is not in this checkout.

## Mon–Wed checklist

### Monday — Phase 0 foundation

- [x] App, API, face service, Prisma schema, README run instructions, and CI workflow are in the repository.
- [x] Supabase migrations and API database health were confirmed by the user.
- [x] No training or fine-tuning is used; the project uses pretrained models.
- [x] `docs/LICENCES.md` records model/data terms, checksums, and benchmark-rights limits.
- [ ] Fresh-machine setup time (target under one hour) has not been measured.

**Phase 0: complete, except the optional fresh-machine timing measurement.**

### Monday — Phase 1 face pipeline

- [x] Pretrained InsightFace buffalo_l SCRFD detector and ArcFace embedding model integrated for local CPU inference; hashes are pinned in `services/face/app/recognition.py` and `services/face/download_models.ps1`.
- [x] Authenticated local face-service embedding endpoint and golden-pair evaluation CLI are implemented. Embeddings are not written to disk or sent to the browser.
- [x] Fifteen real camera frames processed successfully by the CPU timing CLI; measured results are below.
- [ ] Genuine/impostor/difficult-pair golden tests are not measured. No approved image-pair benchmark is available under the current no-scraped-photos instruction and documented dataset terms.

**Phase 1: pipeline and timing are complete; golden accuracy validation remains pending.**

### Tuesday — Phase 2 liveness

- [x] Liveness challenge and capture flow, local-only submission helper, PAD metrics calculator, and protocol are implemented.
- [x] InsightFace and liveness assets pass local checksum verification.
- [x] One own-face phone-screen session was submitted locally; it returned `RETRY` and is recorded as a non-acceptance.
- [ ] Required collection is at least 20 sessions per category. Current counts: print 0/20, phone 1/20, laptop 0/20, replay 0/20.
- [ ] Bona-fide PAD sessions are still needed to measure BPCER. Run the planned Phase 6 evaluation on Saturday, 31 October.

**Phase 2: software is implemented; the requested attack collection is incomplete.**

### Wednesday — Phase 3 and Phase 4

- [x] API and web production builds passed; API tests passed 4/4.
- [x] Python face-service and evaluation tests passed 19/19.
- [x] ONNX CPU sessions load and model checksums pass. Blank-image input returns `RETRY / NO_FACE`; this is a rejection-path smoke check, not an accuracy result.
- [x] Phase 4 policy code implements `MATCH`, `GREY_ZONE`, `NO_MATCH`, and `RETRY`.
- [x] Threshold-derivation CLI is implemented for future development impostor scores and 1:N gallery margin data.
- [ ] Connect recognition to enrollment/search and validate the 1:N policy; enrollment remains unavailable.
- [ ] Derive provisional numeric thresholds from authorized genuine/impostor scores. No scores are available yet, so no thresholds are configured and `biometricDecisionsEnabled` remains false.

**Phase 3: in progress. Phase 4 logic is implemented, but calibration and application integration remain.**

## Requested results

### Phase 1 golden tests and 15-frame CPU timing

| Evidence | Result | Status |
|---|---|---|
| Same-person golden match | Not measured; no approved genuine image-pair set | Pending |
| Different-person golden non-match | Not measured; no approved impostor image-pair set | Pending |
| Difficult-pair / grey-zone case | Not measured | Pending |
| 15-frame CPU timing | 15/15 frames succeeded; total 23.7053 s; mean 1,580.35 ms/frame; CPUExecutionProvider; Intel64 Family 6 Model 142 Stepping 12; Python 3.11.9 | Measured on local consented camera frames |

The 15 frames are local research data and are not committed. This timing measures the current model/runtime on the reported machine; it is not a benchmark accuracy result. Do not use dummy faces, blank frames, or synthetic vectors for accuracy tests. Synthetic vectors are permitted only for the 1M-vector speed test.

The benchmark register documents why LFW, CFP-FP, and AgeDB have not been downloaded: their image provenance/terms are unresolved or conflict with the instruction not to use scraped photos. No benchmark scores or ArcFace golden results are claimed.

### Phase 2 attack results

| Own-face attack | Target | Recorded | Outcome / APCER |
|---|---:|---:|---|
| Printed photo | 20 | 0 | Not measured |
| Phone screen | 20 | 1 | `RETRY` (reason blank), counted as non-acceptance; APCER 0/1 = 0%, 95% Wilson interval 0–79.35% |
| Laptop screen | 20 | 0 | Not measured |
| Replay video | 20 | 0 | Not measured |

This is one phone-screen observation, not evidence of reliable spoof detection. No bona-fide PAD sample is in the results file, so BPCER is not measured. The result row is in the local ignored file `evaluation/runs/pad_results.csv`; the face images remain local and are not published.

### Demo and repository

- A 20-second project status video is available locally at `output/video/PINITHUB_Status_2026-10-28.mp4`. It is a status/demo video, not a live biometric camera-performance recording.
- Public repository: [Foretiner/PINITHUB](https://github.com/Foretiner/PINITHUB).
- Licence register: [`docs/LICENCES.md`](LICENCES.md).
- Source code, docs, tests, and evaluation tools are on the repository's `main` branch. Face images, model weights, and video files are excluded.

## Completion status

Phase 0 is complete. Phase 1 implementation and the requested 15-frame timing are complete; golden accuracy tests remain pending. Phase 2 software and one phone-screen test are complete; the 20-per-category attack set and bona-fide PAD results are not complete. Phase 3 remains in progress. Phase 4 decision logic exists, but numerical thresholds and enrollment/search integration remain pending authorized identity scores.

