import os
from io import BytesIO
from hmac import compare_digest

from fastapi import FastAPI, File, Form, Header, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError
from .liveness import CHALLENGE_EVENTS
from .provider import analyze_frames as analyze_liveness_frames, configured
from .recognition import embed_image_bytes, models_ready as recognition_configured

app = FastAPI(title="PinITHUB Face Service", version="0.1.0")
MAX_FRAME_BYTES = 5 * 1024 * 1024
MAX_FRAMES = 15
MIN_FRAME_BYTES = 100
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}


def require_service_token(token: str | None) -> None:
    expected = os.getenv("FACE_SERVICE_TOKEN", "")
    if not expected or not token or not compare_digest(token, expected):
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/health")
def health() -> dict[str, str | bool]:
    # Provider readiness means local experimental assets are present, not that
    # identity decisions are enabled or that liveness has passed evaluation.
    return {"status": "ok", "ready": configured(), "recognitionReady": recognition_configured(),
            "mode": "research-only", "biometricDecisionsEnabled": False}


@app.post("/internal/face/embedding")
async def embedding(
    frame: UploadFile = File(...),
    x_face_service_token: str | None = Header(default=None),
) -> dict[str, object]:
    """Authenticated local evaluation endpoint; embeddings never go to the browser."""
    require_service_token(x_face_service_token)
    data = await frame.read(MAX_FRAME_BYTES + 1)
    await frame.close()
    if len(data) < MIN_FRAME_BYTES:
        raise HTTPException(status_code=400, detail="Invalid image frame")
    if len(data) > MAX_FRAME_BYTES:
        raise HTTPException(status_code=413, detail="Frame too large")
    try:
        return embed_image_bytes(data)
    except Exception:
        # Do not reveal model paths, scores, image bytes, or exception details.
        raise HTTPException(status_code=503, detail="Research recognition provider is unavailable") from None


@app.post("/internal/face/analyse")
async def analyse(
    frames: list[UploadFile] = File(...),
    challenge: str | None = Form(default=None),
    x_face_service_token: str | None = Header(default=None),
) -> dict[str, object]:
    """Validate and run a research-only liveness experiment; never create an identity."""
    require_service_token(x_face_service_token)
    if challenge not in CHALLENGE_EVENTS:
        raise HTTPException(status_code=400, detail="Invalid challenge")
    if not frames or len(frames) > MAX_FRAMES:
        raise HTTPException(status_code=400, detail="Invalid frame count")

    captured: list[bytes] = []
    try:
        for frame in frames:
            data = await frame.read(MAX_FRAME_BYTES + 1)
            captured.append(data)
            if len(data) < MIN_FRAME_BYTES:
                raise HTTPException(status_code=400, detail="Invalid image frame")
            if len(data) > MAX_FRAME_BYTES:
                raise HTTPException(status_code=413, detail="Frame too large")
            try:
                with Image.open(BytesIO(data)) as image:
                    if image.format not in ALLOWED_FORMATS:
                        raise HTTPException(status_code=415, detail="Unsupported image format")
                    if image.width < 64 or image.height < 64 or image.width > 4096 or image.height > 4096:
                        raise HTTPException(status_code=400, detail="Invalid image dimensions")
                    image.verify()
            except (UnidentifiedImageError, OSError):
                raise HTTPException(status_code=400, detail="Invalid image frame") from None
        try:
            return analyze_liveness_frames(captured, challenge)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from None
        except Exception:
            # Do not expose model details, scores, images, or exceptions to callers.
            raise HTTPException(status_code=503, detail="Research liveness provider is unavailable") from None
    finally:
        for frame in frames:
            await frame.close()

