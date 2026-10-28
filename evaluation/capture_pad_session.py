"""Capture one consented, local webcam PAD session for research evaluation."""
import argparse
import secrets
import time
import uuid
from pathlib import Path

import cv2

CHALLENGES = {
    "turn_left_then_blink": "Turn your head left, then blink",
    "turn_right_then_blink": "Turn your head right, then blink",
    "blink_then_turn_left": "Blink, then turn your head left",
}
ATTACK_TYPES = ("print_photo", "phone_screen", "laptop_screen", "replay")
FRAME_COUNT = 10
FRAME_INTERVAL_SECONDS = 0.25

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--label", choices=("bona_fide", "attack"), required=True)
parser.add_argument("--attack-type", choices=ATTACK_TYPES, default="")
parser.add_argument("--camera", type=int, default=0)
parser.add_argument("--output-root", type=Path, default=Path("evaluation/data"))
parser.add_argument("--frames", type=int, default=FRAME_COUNT, help="Number of frames to capture (3–15; use 15 for the Phase 1 CPU timing run)")
args = parser.parse_args()

if args.label == "attack" and not args.attack_type:
    parser.error("--attack-type is required when --label=attack")
if args.label == "bona_fide" and args.attack_type:
    parser.error("Do not set --attack-type for bona-fide sessions")
if not 3 <= args.frames <= 15:
    parser.error("--frames must be between 3 and 15")

challenge, prompt = secrets.choice(list(CHALLENGES.items()))
sample_id = uuid.uuid4().hex
output_dir = args.output_root / sample_id
output_dir.mkdir(parents=True, exist_ok=False)
camera = cv2.VideoCapture(args.camera)
if not camera.isOpened():
    output_dir.rmdir()
    raise SystemExit("Could not open the camera. Check camera permissions and --camera index.")

print("This captures face images locally. Continue only with informed consent and your approved research protocol.")
print(f"Session label: {args.label}; attack type: {args.attack_type or 'none'}")
print(f"Challenge: {prompt}")
print(f"Challenge key for the local analysis command: {challenge}")
print(f"Press SPACE to record {args.frames} frames. Keep neutral for the first 3 frames, then perform the challenge. Press ESC to cancel.")

captured = 0
try:
    while True:
        ok, frame = camera.read()
        if not ok:
            raise SystemExit("Camera frame read failed.")
        preview = frame.copy()
        cv2.putText(preview, prompt, (12, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)
        cv2.putText(preview, "Neutral first 3 frames; SPACE capture | ESC cancel", (12, 60), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)
        cv2.imshow("PINITHUB research capture", preview)
        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            raise SystemExit("Capture cancelled; delete the empty output folder if it remains.")
        if key == 32:
            for index in range(args.frames):
                ok, frame = camera.read()
                if not ok:
                    raise SystemExit("Camera frame read failed; remove the incomplete session folder.")
                filename = output_dir / f"frame-{index + 1:02}.jpg"
                if not cv2.imwrite(str(filename), frame, [cv2.IMWRITE_JPEG_QUALITY, 90]):
                    raise SystemExit("Could not write a frame; remove the incomplete session folder.")
                captured += 1
                cv2.imshow("PINITHUB research capture", frame)
                cv2.waitKey(1)
                time.sleep(FRAME_INTERVAL_SECONDS)
            break
finally:
    camera.release()
    cv2.destroyAllWindows()

if captured != args.frames:
    raise SystemExit("Incomplete capture; do not submit it as a test result.")
print(f"Captured {captured} frames locally at {output_dir}")
print(f"Submit PAD sessions to localhost only with: python evaluation/submit_pad_session.py {output_dir} --label {args.label} --challenge {challenge}" + (f" --attack-type {args.attack_type}" if args.attack_type else ""))
print("For ArcFace 15-frame timing, pass the 15 frame paths to evaluation/time_arcface_15.py instead of submitting the folder.")
print("Delete this folder after recording the outcome and when your approved retention period ends.")
