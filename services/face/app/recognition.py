"""Research-only CPU face detection and ArcFace embedding with InsightFace ONNX.

Weights come from the InsightFace buffalo_l pack (non-commercial research only).
This module returns one normalized embedding; it does not store or compare it.
"""

from __future__ import annotations

from functools import lru_cache
from hashlib import sha256
from pathlib import Path

import numpy as np

MODEL_DIR = Path(__file__).resolve().parents[1] / "models"
DETECTOR = MODEL_DIR / "det_10g.onnx"
RECOGNIZER = MODEL_DIR / "w600k_r50.onnx"
DETECTOR_SHA256 = "5838f7fe053675b1c7a08b633df49e7af5495cee0493c7dcf6697200b85b5b91"
RECOGNIZER_SHA256 = "4c06341c33c2ca1f86781dab0e829f88ad5b64be9fba56e56bc9ebdefc619e43"
INPUT_SIZE = (640, 640)
STRIDES = (8, 16, 32)
ANCHORS = 2
ARC_TEMPLATE = np.asarray(
    [[38.2946, 51.6963], [73.5318, 51.5014], [56.0252, 71.7366],
     [41.5493, 92.3655], [70.7299, 92.2041]], dtype=np.float32
)


def _sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as file:
        for block in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


@lru_cache(maxsize=1)
def models_ready() -> bool:
    return (
        DETECTOR.is_file() and RECOGNIZER.is_file()
        and _sha256(DETECTOR) == DETECTOR_SHA256
        and _sha256(RECOGNIZER) == RECOGNIZER_SHA256
    )


@lru_cache(maxsize=1)
def _sessions():
    if not models_ready():
        raise RuntimeError("Research ArcFace/SCRFD models missing or checksum mismatch")
    import onnxruntime as ort

    options = ort.SessionOptions()
    options.intra_op_num_threads = 1
    options.inter_op_num_threads = 1
    detector = ort.InferenceSession(str(DETECTOR), sess_options=options, providers=["CPUExecutionProvider"])
    recognizer = ort.InferenceSession(str(RECOGNIZER), sess_options=options, providers=["CPUExecutionProvider"])
    return detector, recognizer


def _decode_faces(image_bgr: np.ndarray, threshold: float = 0.5):
    import cv2

    height, width = image_bgr.shape[:2]
    scale = min(INPUT_SIZE[0] / width, INPUT_SIZE[1] / height)
    resized = cv2.resize(image_bgr, (round(width * scale), round(height * scale)))
    canvas = np.zeros((INPUT_SIZE[1], INPUT_SIZE[0], 3), dtype=np.uint8)
    canvas[:resized.shape[0], :resized.shape[1]] = resized
    tensor = ((canvas.astype(np.float32) - 127.5) / 128.0).transpose(2, 0, 1)[None]
    detector, _ = _sessions()
    outputs = detector.run(None, {detector.get_inputs()[0].name: tensor})
    boxes_all: list[np.ndarray] = []
    scores_all: list[float] = []
    points_all: list[np.ndarray] = []
    for index, stride in enumerate(STRIDES):
        scores = outputs[index].reshape(-1)
        boxes = outputs[index + len(STRIDES)].reshape(-1, 4) * stride
        points = outputs[index + 2 * len(STRIDES)].reshape(-1, 5, 2) * stride
        feat_h, feat_w = INPUT_SIZE[1] // stride, INPUT_SIZE[0] // stride
        centers = np.stack(np.mgrid[:feat_h, :feat_w][::-1], axis=-1).astype(np.float32)
        centers = (centers.reshape(-1, 2) * stride).repeat(ANCHORS, axis=0)
        keep = scores >= threshold
        if not np.any(keep):
            continue
        center = centers[keep]
        dist = boxes[keep]
        xyxy = np.column_stack((center[:, 0] - dist[:, 0], center[:, 1] - dist[:, 1],
                                center[:, 0] + dist[:, 2], center[:, 1] + dist[:, 3])) / scale
        keypoints = (points[keep] + center[:, None, :]) / scale
        boxes_all.extend(xyxy)
        scores_all.extend(scores[keep].tolist())
        points_all.extend(keypoints)
    if not scores_all:
        return []
    rects = [[float(b[0]), float(b[1]), float(b[2] - b[0]), float(b[3] - b[1])] for b in boxes_all]
    chosen = cv2.dnn.NMSBoxes(rects, scores_all, threshold, 0.4)
    indices = np.asarray(chosen).reshape(-1).tolist() if len(chosen) else []
    return [(boxes_all[i], scores_all[i], points_all[i]) for i in indices]


def embed_image_bytes(image_bytes: bytes) -> dict[str, object]:
    """Detect exactly one face, align by five SCRFD landmarks, return a 512-D ArcFace vector."""
    import cv2
    from PIL import Image, UnidentifiedImageError
    from io import BytesIO

    try:
        with Image.open(BytesIO(image_bytes)) as image:
            rgb = np.asarray(image.convert("RGB"))
    except (UnidentifiedImageError, OSError):
        return {"status": "RETRY", "reason": "INVALID_IMAGE"}
    if rgb.ndim != 3 or rgb.shape[0] < 64 or rgb.shape[1] < 64:
        return {"status": "RETRY", "reason": "IMAGE_TOO_SMALL"}
    bgr = cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    faces = _decode_faces(bgr)
    if not faces:
        return {"status": "RETRY", "reason": "NO_FACE"}
    if len(faces) != 1:
        return {"status": "RETRY", "reason": "MULTIPLE_FACES"}
    _, confidence, landmarks = faces[0]
    transform, _ = cv2.estimateAffinePartial2D(landmarks.astype(np.float32), ARC_TEMPLATE, method=cv2.LMEDS)
    if transform is None or not np.isfinite(transform).all():
        return {"status": "RETRY", "reason": "ALIGNMENT_FAILED"}
    aligned = cv2.warpAffine(bgr, transform, (112, 112), borderValue=0)
    tensor = ((aligned.astype(np.float32) - 127.5) / 127.5).transpose(2, 0, 1)[None]
    _, recognizer = _sessions()
    raw = recognizer.run(None, {recognizer.get_inputs()[0].name: tensor})[0].reshape(-1).astype(np.float32)
    norm = float(np.linalg.norm(raw))
    if raw.shape != (512,) or not np.isfinite(raw).all() or norm <= 1e-12:
        return {"status": "RETRY", "reason": "INVALID_EMBEDDING"}
    return {"status": "OK", "embedding": (raw / norm).tolist(), "detectorConfidence": float(confidence),
            "model": "insightface/buffalo_l-SCRFD-10GF+ArcFace-w600k_r50"}
