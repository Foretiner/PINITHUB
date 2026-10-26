"""Calculate 1:N FPIR/FNIR from gallery-search outcomes, one row per probe.

CSV columns: probe_id,probe_kind,max_similarity; probe_kind is enrolled or new.
max_similarity must be the top candidate score from the full search gallery.
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
        label = row["probe_kind"].strip().lower()
        if label not in {"enrolled", "new"}:
            raise SystemExit("probe_kind must be enrolled or new")
        score = float(row["max_similarity"])
        counts[label]["total"] += 1
        counts[label]["accept"] += score >= args.threshold
print(json.dumps({
    "threshold": args.threshold,
    "FPIR": rate(counts["new"]["accept"], counts["new"]["total"]),
    "FNIR": rate(counts["enrolled"]["total"] - counts["enrolled"]["accept"], counts["enrolled"]["total"]),
    "caveat": "One row must represent one probe searched against the complete gallery. Use independent people-level splits.",
}, indent=2))
