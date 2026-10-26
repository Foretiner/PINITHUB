import os
from io import BytesIO
from hmac import compare_digest

from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from PIL import Image, UnidentifiedImageError

app = FastAPI(title="PinITHUB Face Service", version="0.1.0")
MAX_FRAME_BYTES = 5 * 1024 * 1024
MAX_FRAMES = 15
MIN_FRAME_BYTES = 100
ALLOWED_FORMATS = {"JPEG", "PNG", "WEBP"}


def configured() -> bool:
    return False


def require_service_token(token: str | None) -> None:
    expected = os.getenv("FACE_SERVICE_TOKEN", "")
    if not expected or not token or not compare_digest(token, expected):
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/health")
def health() -> dict[str, str | bool]:
    # Readiness is false until a reviewed model provider is installed.
    return {"status": "ok", "ready": configured()}


@app.post("/internal/face/analyse")
async def analyse(
    frames: list[UploadFile] = File(...),
    x_face_service_token: str | None = Header(default=None),
) -> None:
    """Validate uploaded frames in memory, then fail closed without a provider."""
    require_service_token(x_face_service_token)
    if not frames or len(frames) > MAX_FRAMES:
        raise HTTPException(status_code=400, detail="Invalid frame count")

    try:
        for frame in frames:
            data = await frame.read(MAX_FRAME_BYTES + 1)
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
    finally:
        for frame in frames:
            await frame.close()

    # No model is selected: never fabricate an embedding, liveness result, or decision.
    raise HTTPException(status_code=503, detail="Face analysis provider is not configured")

