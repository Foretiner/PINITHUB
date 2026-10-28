"""Research-only MediaPipe + CelebA-Spoof-trained PAD provider.

The candidate model is deliberately not an account-decision provider. Its
published dataset terms restrict use to non-commercial research/education.
"""

from functools import lru_cache
from hashlib import sha256, sha384
from importlib.util import find_spec
from io import BytesIO
from pathlib import Path

from .liveness import FrameSignal, combine_liveness

MODEL_DIR = Path(__file__).resolve().parents[1] / "models"
PAD_MODEL = MODEL_DIR / "anti-spoof-mn3.onnx"
LANDMARK_MODEL = MODEL_DIR / "face_landmarker.task"
PAD_SHA384 = "6de4534964b723397b3e8c995cadcf43bc007cc2f9930b95ae25f76adccece5d1d4d058d0b15117b9e4a9f758424f92a"
LANDMARK_SHA256 = "64184e229b263107bc2b804c6625db1341ff2bb731874b0bcc2fe6544e0bc9ff"
PAD_MODEL_ID = "open_model_zoo/anti-spoof-mn3/2022.1"
LANDMARK_MODEL_ID = "mediapipe/face_landmarker/float16/1"


def _has_runtime() -> bool:
    return all(find_spec(name) is not None for name in ("mediapipe", "onnxruntime", "numpy", "PIL", "cv2"))


def _matches_hash(path: Path, algorithm: str, expected: str) -> bool:
    if not path.is_file():
        return False
    digest = sha256() if algorithm == "sha256" else sha384()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest() == expected


@lru_cache(maxsize=1)
def configured() -> bool:
    return (
        _has_runtime()
        and _matches_hash(PAD_MODEL, "sha384", PAD_SHA384)
        and _matches_hash(LANDMARK_MODEL, "sha256", LANDMARK_SHA256)
    )


@lru_cache(maxsize=1)
def _load_models():
    import onnxruntime as ort

    session = ort.InferenceSession(str(PAD_MODEL), providers=["CPUExecutionProvider"])
    return session


def _crop_face(rgb, landmarks):
    import numpy as np

    height, width = rgb.shape[:2]
    xs = [point.x * width for point in landmarks]
    ys = [point.y * height for point in landmarks]
    left, right = min(xs), max(xs)
    top, bottom = min(ys), max(ys)
    margin_x = (right - left) * 0.25
    margin_y = (bottom - top) * 0.25
    x1 = max(0, int(left - margin_x))
    x2 = min(width, int(right + margin_x))
    y1 = max(0, int(top - margin_y))
    y2 = min(height, int(bottom + margin_y))
    if x2 - x1 < 32 or y2 - y1 < 32:
        return None
    return np.ascontiguousarray(rgb[y1:y2, x1:x2])


def _face_signals(rgb, landmarks, blendshapes, pad_session):
    import cv2
    import numpy as np

    face = _crop_face(rgb, landmarks)
    if face is None:
        return None
    # OMZ's converted ONNX expects BGR and these per-channel normalization values.
    bgr = cv2.cvtColor(face, cv2.COLOR_RGB2BGR)
    resized = cv2.resize(bgr, (128, 128), interpolation=cv2.INTER_LINEAR).astype(np.float32)
    means = np.asarray([151.2405, 119.5950, 107.8395], dtype=np.float32)
    scales = np.asarray([63.0105, 56.4570, 55.0035], dtype=np.float32)
    tensor = ((resized - means) / scales).transpose(2, 0, 1)[None, ...]
    output = np.asarray(pad_session.run(None, {"actual_input_1": tensor})[0][0], dtype=np.float64)
    if output.shape != (2,) or not np.isfinite(output).all():
        return None
    # Model card defines class 0 as bona fide and class 1 as spoof.
    total = float(output.sum())
    if total <= 0:
        return None
    probabilities = output / total

    # Landmark indices follow the 478-point MediaPipe FaceMesh topology.
    if len(landmarks) <= 263:
        return None
    eye_mid = (landmarks[33].x + landmarks[263].x) / 2
    eye_span = abs(landmarks[263].x - landmarks[33].x)
    if eye_span <= 1e-4:
        return None
    yaw_proxy = (landmarks[1].x - eye_mid) / eye_span

    shapes = {item.category_name: item.score for item in blendshapes}
    blink_score = (shapes.get("eyeBlinkLeft", 0.0) + shapes.get("eyeBlinkRight", 0.0)) / 2
    return FrameSignal(yaw_proxy=yaw_proxy, blink_score=blink_score, live_score=float(probabilities[0]))


def analyze_frames(frame_bytes: list[bytes], challenge: str) -> dict[str, object]:
    """Run experimental active challenge and passive PAD on server-side frames."""
    if not configured():
        raise RuntimeError("Research liveness models are unavailable or failed checksum verification")

    import numpy as np
    from PIL import Image, UnidentifiedImageError

    import mediapipe as mp

    pad_session = _load_models()
    options = mp.tasks.vision.FaceLandmarkerOptions(
        base_options=mp.tasks.BaseOptions(model_asset_path=str(LANDMARK_MODEL)),
        running_mode=mp.tasks.vision.RunningMode.VIDEO,
        num_faces=1,
        output_face_blendshapes=True,
        output_facial_transformation_matrixes=True,
    )
    landmarker = mp.tasks.vision.FaceLandmarker.create_from_options(options)
    signals: list[FrameSignal] = []
    try:
        for index, data in enumerate(frame_bytes):
            try:
                with Image.open(BytesIO(data)) as image:
                    rgb = np.asarray(image.convert("RGB"))
            except (UnidentifiedImageError, OSError):
                raise ValueError("Invalid image frame") from None
            if rgb.ndim != 3 or rgb.shape[0] < 64 or rgb.shape[1] < 64:
                raise ValueError("Invalid image frame")
            result = landmarker.detect_for_video(
                mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb),
                timestamp_ms=(index + 1) * 250,
            )
            if len(result.face_landmarks) != 1 or len(result.face_blendshapes) != 1:
                return {
                    "decision": "RETRY",
                    "reason": "FACE_NOT_STABLE",
                    "mode": "EXPERIMENTAL_RESEARCH_ONLY",
                    "padModel": PAD_MODEL_ID,
                    "landmarkModel": LANDMARK_MODEL_ID,
                    "framesProcessed": index + 1,
                }
            signal = _face_signals(rgb, result.face_landmarks[0], result.face_blendshapes[0], pad_session)
            if signal is None:
                return {
                    "decision": "RETRY",
                    "reason": "LOW_QUALITY",
                    "mode": "EXPERIMENTAL_RESEARCH_ONLY",
                    "padModel": PAD_MODEL_ID,
                    "landmarkModel": LANDMARK_MODEL_ID,
                    "framesProcessed": index + 1,
                }
            signals.append(signal)
    finally:
        landmarker.close()

    combined = combine_liveness(challenge, signals)
    return {
        "decision": "LIVE" if combined["livenessPassed"] else "RETRY",
        "mode": "EXPERIMENTAL_RESEARCH_ONLY",
        "padModel": PAD_MODEL_ID,
        "landmarkModel": LANDMARK_MODEL_ID,
        "framesProcessed": len(signals),
        "liveness": combined,
    }
