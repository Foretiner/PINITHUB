"""Run genuine/impostor image-pair checks on real licensed/consented images.

CSV columns: sample_id,image_a,image_b,label (label is genuine or impostor).
Paths are relative to the CSV. Never put images or personally identifying names
in Git or the result file. This tool does not train or tune model weights.
"""
import argparse
import csv
import json
from pathlib import Path
import sys

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from metrics import rate
from services.face.app.recognition import embed_image_bytes


def embed(path: Path) -> np.ndarray:
    result = embed_image_bytes(path.read_bytes())
    if result.get("status") != "OK":
        raise ValueError(f"{path.name}: {result.get('reason', 'embedding failed')}")
    return np.asarray(result["embedding"], dtype=np.float32)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("pairs_csv", type=Path)
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--threshold", type=float, help="Frozen development-set threshold in [0,1]; omit for scores only")
    args = parser.parse_args()
    if args.threshold is not None and not 0 <= args.threshold <= 1:
        parser.error("--threshold must be between 0 and 1")
    rows = list(csv.DictReader(args.pairs_csv.open(newline="", encoding="utf-8")))
    if not rows or not {"sample_id", "image_a", "image_b", "label"}.issubset(rows[0]):
        parser.error("CSV must have sample_id,image_a,image_b,label columns")
    root = args.pairs_csv.resolve().parent
    out = []
    sample_ids: set[str] = set()
    for row in rows:
        if not row["sample_id"] or row["sample_id"] in sample_ids:
            parser.error("sample_id values must be non-empty and unique")
        sample_ids.add(row["sample_id"])
        if row["label"] not in {"genuine", "impostor"}:
            parser.error("labels must be genuine or impostor")
        score = float(np.dot(embed((root / row["image_a"]).resolve()), embed((root / row["image_b"]).resolve())))
        prediction = "" if args.threshold is None else ("genuine" if score >= args.threshold else "impostor")
        out.append({"sample_id": row["sample_id"], "label": row["label"], "similarity": f"{score:.8f}", "prediction": prediction})
    args.results.parent.mkdir(parents=True, exist_ok=True)
    with args.results.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["sample_id", "label", "similarity", "prediction"])
        writer.writeheader(); writer.writerows(out)
    summary: dict[str, object] = {"pairCount": len(out), "genuineCount": sum(r["label"] == "genuine" for r in out),
                                  "impostorCount": sum(r["label"] == "impostor" for r in out), "threshold": args.threshold}
    if args.threshold is not None:
        impostors = [r for r in out if r["label"] == "impostor"]
        genuine = [r for r in out if r["label"] == "genuine"]
        summary["FMR"] = rate(sum(r["prediction"] == "genuine" for r in impostors), len(impostors))
        summary["FNMR"] = rate(sum(r["prediction"] == "impostor" for r in genuine), len(genuine))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
