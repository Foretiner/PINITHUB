# Results

No biometric model has been approved or run. This file is a template until evaluation is performed with consented or properly licensed data.

| Measure | Value | Sample size | 95% CI | Dataset/model version | Threshold |
|---|---:|---:|---:|---|---|
| Login FMR / FNMR | Not measured | - | - | - | - |
| Duplicate FPIR / FNIR | Not measured | - | - | - | - |
| PAD APCER by attack / BPCER | Not measured | - | - | - | - |
| Search p95 / recall at 1M | Not measured | - | - | Synthetic vectors for speed only | - |

Do not fill these cells with estimates, synthetic biometric scores, or results from a non-representative sample. `verify_eval.py`, `dedup_eval.py`, and `pad_eval.py` calculate rates with Wilson 95% intervals from supplied labelled CSV results. Thresholds must be selected on a development split and reported on an independent evaluation split.

For duplicate search, report HNSW recall against an exhaustive exact baseline at each gallery size. Approximate-neighbor search can omit a true match; do not equate exact scoring of retrieved candidates with an exhaustive gallery search or claim a mathematical zero-duplicate guarantee.
