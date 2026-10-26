"""Calculate 1:1 verification FMR/FNMR from a consented, labelled CSV.

CSV columns: similarity,label where label is genuine or impostor.
Higher similarity means more likely to be the same person.
"""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from metrics import rate

parser = argparse.ArgumentParser()
parser.add_argument("csv_path", type=Path)
parser.add_argument("--threshold", type=float, required=True)
args = parser.parse_args()
counts = defaultdict(lambda: {"accept": 0, "total": 0})
with args.csv_path.open(newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        label = row["label"].strip().lower()
        if label not in {"genuine", "impostor"}:
            raise SystemExit("label must be genuine or impostor")
        score = float(row["similarity"])
        counts[label]["total"] += 1
        counts[label]["accept"] += score >= args.threshold
print(json.dumps({
    "threshold": args.threshold,
    "FMR": rate(counts["impostor"]["accept"], counts["impostor"]["total"]),
    "FNMR": rate(counts["genuine"]["total"] - counts["genuine"]["accept"], counts["genuine"]["total"]),
    "caveat": "Use independent people-level splits. This pairwise script does not estimate 1:N identification rates.",
}, indent=2))
