"""Derive provisional 1:1 score cutoffs from a development split's impostor pairs.

The exported cutoffs are research-only. Use a separate held-out evaluation split;
the review band and margin require validation in the application's 1:N gallery.
"""
import argparse
import csv
import json
from pathlib import Path

import numpy as np


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("scores_csv", type=Path, help="CSV columns: similarity,label; development split only")
    parser.add_argument("--target-fmr", type=float, required=True, help="Target false-match rate, e.g. 0.001")
    parser.add_argument("--min-margin", type=float, required=True, help="Margin separately justified by 1:N development results")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if not 0 < args.target_fmr < 1 or not 0 <= args.min_margin <= 1:
        parser.error("target FMR must be in (0,1); margin must be in [0,1]")
    with args.scores_csv.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if not rows or not {"similarity", "label"}.issubset(rows[0]):
        parser.error("CSV must have similarity,label columns")
    if any(r["label"].strip().lower() not in {"genuine", "impostor"} for r in rows):
        parser.error("labels must be genuine or impostor")
    impostors = np.asarray([float(r["similarity"]) for r in rows if r["label"].strip().lower() == "impostor"])
    genuine = np.asarray([float(r["similarity"]) for r in rows if r["label"].strip().lower() == "genuine"])
    if len(impostors) < int(np.ceil(1 / args.target_fmr)):
        parser.error(f"need at least {int(np.ceil(1 / args.target_fmr))} impostor pairs to support this empirical tail target; found {len(impostors)}")
    if len(genuine) == 0 or not np.isfinite(impostors).all() or not np.isfinite(genuine).all():
        parser.error("need finite genuine and impostor scores")
    match = float(np.quantile(impostors, 1 - args.target_fmr, method="higher"))
    review = float(np.quantile(impostors, 0.95, method="higher"))
    if review >= match:
        parser.error("data do not support a distinct review band at the chosen target FMR")
    result = {"BIO_MATCH_THRESHOLD": round(match, 8), "BIO_REVIEW_THRESHOLD": round(review, 8),
              "BIO_MIN_MARGIN": args.min_margin, "targetFMR": args.target_fmr,
              "developmentPairCounts": {"genuine": int(len(genuine)), "impostor": int(len(impostors))},
              "caveat": "Provisional 1:1 development cutoffs only. Validate on an independent set and recalibrate margin in the 1:N gallery before enabling identity decisions."}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
