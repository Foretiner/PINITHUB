"""Calculate APCER by attack type and BPCER from labelled PAD outcomes.

CSV columns: label,prediction,attack_type; labels are bona_fide or attack;
predictions are live or spoof.
"""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from metrics import rate

parser = argparse.ArgumentParser()
parser.add_argument("csv_path", type=Path)
args = parser.parse_args()
attacks = defaultdict(lambda: {"accepted": 0, "total": 0})
bonafide = {"rejected": 0, "total": 0}
with args.csv_path.open(newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        label = row["label"].strip().lower()
        prediction = row["prediction"].strip().lower()
        if label == "attack" and prediction in {"live", "spoof"}:
            kind = row["attack_type"].strip() or "unspecified"
            attacks[kind]["total"] += 1
            attacks[kind]["accepted"] += prediction == "live"
        elif label == "bona_fide" and prediction in {"live", "spoof"}:
            bonafide["total"] += 1
            bonafide["rejected"] += prediction == "spoof"
        else:
            raise SystemExit("invalid label/prediction combination")
print(json.dumps({
    "APCER_by_attack_type": {kind: rate(v["accepted"], v["total"]) for kind, v in attacks.items()},
    "BPCER": rate(bonafide["rejected"], bonafide["total"]),
    "caveat": "These metrics do not imply certification. Report attack samples and 95% intervals.",
}, indent=2))
