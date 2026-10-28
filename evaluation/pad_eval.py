"""Calculate research APCER/BPCER from one result per capture session.

CSV columns: sample_id,label,prediction,attack_type,system_decision,reason.
Do not put names, images, or other personal identifiers here. Repeated frames
from one capture are not independent samples and must not be separate rows.
"""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path
from metrics import rate

ATTACK_TYPES = ("print_photo", "phone_screen", "laptop_screen", "replay")

parser = argparse.ArgumentParser()
parser.add_argument("csv_path", type=Path)
args = parser.parse_args()
attacks = defaultdict(lambda: {"accepted": 0, "total": 0})
bonafide = {"rejected": 0, "total": 0}
retry_counts = defaultdict(lambda: {"retry": 0, "total": 0})
sample_ids = set()
with args.csv_path.open(newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    required = {"sample_id", "label", "prediction", "attack_type"}
    if not required.issubset(reader.fieldnames or []):
        raise SystemExit("CSV must contain sample_id,label,prediction,attack_type")
    for row in reader:
        sample_id = row["sample_id"].strip()
        if not sample_id or sample_id in sample_ids:
            raise SystemExit("sample_id must be present and unique; use one row per capture session")
        sample_ids.add(sample_id)
        label = row["label"].strip().lower()
        prediction = row["prediction"].strip().lower()
        system_decision = row.get("system_decision", "").strip().upper()
        if system_decision and (system_decision not in {"LIVE", "RETRY"}
                                or prediction != ("live" if system_decision == "LIVE" else "spoof")):
            raise SystemExit("prediction must match system_decision: LIVE=live, RETRY=spoof/rejected")
        if label == "attack" and prediction in {"live", "spoof"}:
            kind = row["attack_type"].strip()
            if kind not in ATTACK_TYPES:
                raise SystemExit(f"attack_type must be one of: {', '.join(ATTACK_TYPES)}")
            attacks[kind]["total"] += 1
            attacks[kind]["accepted"] += prediction == "live"
            retry_counts[label]["total"] += 1
            retry_counts[label]["retry"] += system_decision == "RETRY"
        elif label == "bona_fide" and prediction in {"live", "spoof"}:
            if row["attack_type"].strip():
                raise SystemExit("attack_type must be empty for bona_fide rows")
            bonafide["total"] += 1
            bonafide["rejected"] += prediction == "spoof"
            retry_counts[label]["total"] += 1
            retry_counts[label]["retry"] += system_decision == "RETRY"
        else:
            raise SystemExit("invalid label/prediction combination")
print(json.dumps({
    "APCER_by_attack_type": {
        kind: rate(attacks[kind]["accepted"], attacks[kind]["total"])
        for kind in ATTACK_TYPES
    },
    "BPCER": rate(bonafide["rejected"], bonafide["total"]),
    "RETRY_rate_by_label": {
        label: rate(values["retry"], values["total"])
        for label, values in retry_counts.items()
    },
    "caveat": "These metrics do not imply certification. Report attack samples and 95% intervals.",
}, indent=2))
