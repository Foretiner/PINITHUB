# Results

Pretrained SCRFD and ArcFace models are integrated for local non-commercial research evaluation; they are not approved for account identity decisions. A blank image returns `RETRY / NO_FACE`, which checks only no-face rejection. No consented bona-fide or attack sessions and no licensed benchmark pairs are available here, so recognition and PAD performance remain unmeasured.

| Measure | Value | Sample size | 95% CI | Dataset/model version | Threshold |
|---|---:|---:|---:|---|---|
| Login FMR / FNMR | Not measured | - | - | - | - |
| Duplicate FPIR / FNIR | Not measured | - | - | - | - |
| PAD APCER by attack / BPCER | Not measured | - | - | - | - |
| Search p95 / recall at 1M | Not measured | - | - | Synthetic vectors for speed only | - |

Do not fill these cells with estimates, synthetic biometric scores, or results from a non-representative sample. `verify_eval.py`, `dedup_eval.py`, and `pad_eval.py` calculate rates with Wilson 95% intervals from supplied labelled CSV results. Thresholds must be selected on a development split and reported on an independent evaluation split.

For duplicate search, report HNSW recall against an exhaustive exact baseline at each gallery size. Approximate-neighbor search can omit a true match; do not equate exact scoring of retrieved candidates with an exhaustive gallery search or claim a mathematical zero-duplicate guarantee.
