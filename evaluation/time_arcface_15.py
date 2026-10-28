"""Time 15 real consented face frames on CPU; does not save embeddings."""
import argparse
import json
import platform
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from services.face.app.recognition import _sessions, embed_image_bytes


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("frames", nargs=15, type=Path, help="Exactly 15 locally stored consented face images")
    args = parser.parse_args()
    _sessions()  # Load ONNX weights before the timed section; report inference, not cold startup.
    start = time.perf_counter()
    statuses = [embed_image_bytes(path.read_bytes()).get("status") for path in args.frames]
    elapsed = time.perf_counter() - start
    print(json.dumps({"frames": len(statuses), "successful": statuses.count("OK"),
                      "retry": statuses.count("RETRY"), "elapsedSeconds": round(elapsed, 4),
                      "meanMsPerFrame": round(elapsed * 1000 / len(statuses), 2),
                      "cpu": platform.processor(), "python": platform.python_version(),
                      "device": "CPUExecutionProvider", "model": "InsightFace buffalo_l SCRFD+ArcFace",
                      "imagesSavedOrUploaded": False}, indent=2))


if __name__ == "__main__":
    main()
