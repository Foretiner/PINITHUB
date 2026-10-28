import csv
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).with_name("pad_eval.py")


def _run(tmp_path, rows):
    path = tmp_path / "results.csv"
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["sample_id", "label", "prediction", "attack_type"])
        writer.writeheader()
        writer.writerows(rows)
    return subprocess.run([sys.executable, str(SCRIPT), str(path)], capture_output=True, text=True)


def test_pad_eval_reports_apcer_bpcer_with_intervals(tmp_path):
    result = _run(tmp_path, [
        {"sample_id": "a1", "label": "bona_fide", "prediction": "live", "attack_type": ""},
        {"sample_id": "a2", "label": "bona_fide", "prediction": "spoof", "attack_type": ""},
        {"sample_id": "b1", "label": "attack", "prediction": "live", "attack_type": "print_photo"},
        {"sample_id": "b2", "label": "attack", "prediction": "spoof", "attack_type": "print_photo"},
    ])
    assert result.returncode == 0, result.stderr
    assert '"BPCER"' in result.stdout
    assert '"APCER_by_attack_type"' in result.stdout
    assert '"total": 2' in result.stdout


def test_pad_eval_rejects_duplicate_session_rows(tmp_path):
    row = {"sample_id": "same", "label": "attack", "prediction": "spoof", "attack_type": "replay"}
    result = _run(tmp_path, [row, row])
    assert result.returncode != 0
    assert "unique" in result.stderr
