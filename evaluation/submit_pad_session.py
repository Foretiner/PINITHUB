"""Submit one locally captured research session and append only its outcome CSV row."""
import argparse
import csv
import os
import sys
import uuid
from pathlib import Path
from urllib.parse import urlparse

import httpx

ATTACK_TYPES = ("print_photo", "phone_screen", "laptop_screen", "replay")
CHALLENGES = ("turn_left_then_blink", "turn_right_then_blink", "blink_then_turn_left")
IMAGE_TYPES = {".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".png": "image/png", ".webp": "image/webp"}
FIELDS = ["sample_id", "label", "prediction", "attack_type", "challenge", "system_decision", "reason"]

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("frame_dir", type=Path, help="Local directory containing 6-15 ordered image frames")
parser.add_argument("--label", choices=("bona_fide", "attack"), required=True)
parser.add_argument("--attack-type", choices=ATTACK_TYPES, default="")
parser.add_argument("--challenge", choices=CHALLENGES, required=True)
parser.add_argument("--url", default="http://127.0.0.1:8001")
parser.add_argument("--output", type=Path, default=Path("evaluation/runs/pad_results.csv"))
args = parser.parse_args()

host = urlparse(args.url).hostname
if host not in {"localhost", "127.0.0.1", "::1"}:
    raise SystemExit("For privacy, this tool only sends frames to a localhost face service")
if args.label == "attack" and not args.attack_type:
    raise SystemExit("--attack-type is required when --label=attack")
if args.label == "bona_fide" and args.attack_type:
    raise SystemExit("Do not set --attack-type for bona-fide sessions")
token = os.getenv("FACE_SERVICE_TOKEN", "")
if not token or token == "replace-with-a-long-random-secret":
    raise SystemExit("Set FACE_SERVICE_TOKEN in this PowerShell session to match the local face service")
if not args.frame_dir.is_dir():
    raise SystemExit("Frame directory does not exist")
frames = sorted((p for p in args.frame_dir.iterdir() if p.is_file() and p.suffix.lower() in IMAGE_TYPES), key=lambda p: p.name)
if not 6 <= len(frames) <= 15:
    raise SystemExit(f"Expected 6-15 ordered image frames; found {len(frames)}")

opened = []
try:
    parts = []
    for path in frames:
        handle = path.open("rb")
        opened.append(handle)
        parts.append(("frames", (path.name, handle, IMAGE_TYPES[path.suffix.lower()])))
    try:
        response = httpx.post(
            f"{args.url.rstrip('/')}/internal/face/analyse",
            headers={"X-Face-Service-Token": token},
            data={"challenge": args.challenge},
            files=parts,
            timeout=90.0,
        )
    except httpx.HTTPError:
        raise SystemExit("Could not reach the localhost face service; no result row was saved") from None
finally:
    for handle in opened:
        handle.close()

if response.status_code != 200:
    raise SystemExit(f"Local face service returned HTTP {response.status_code}; no result row was saved")
result = response.json()
decision = result.get("decision")
if decision not in {"LIVE", "RETRY"}:
    raise SystemExit("Unexpected face-service result; no result row was saved")

# For APCER/BPCER, a LIVE result is acceptance; RETRY is a non-acceptance.
# Keep the raw decision/reason too so technical retries remain visible.
row = {
    "sample_id": uuid.uuid4().hex,
    "label": args.label,
    "prediction": "live" if decision == "LIVE" else "spoof",
    "attack_type": args.attack_type,
    "challenge": args.challenge,
    "system_decision": decision,
    "reason": result.get("reason", ""),
}
args.output.parent.mkdir(parents=True, exist_ok=True)
new_file = not args.output.exists()
with args.output.open("a", newline="", encoding="utf-8") as file:
    writer = csv.DictWriter(file, fieldnames=FIELDS)
    if new_file:
        writer.writeheader()
    writer.writerow(row)
print(f"Saved {row['sample_id']}: {decision} ({result.get('reason', 'no retry reason')}) to {args.output}")
print("Delete the local frame images when your approved retention period ends; this tool does not copy them.")
