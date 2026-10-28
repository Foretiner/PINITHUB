import asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from unittest.mock import patch
from app.main import app

async def _request(method: str, path: str, **kwargs):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        return await getattr(client, method)(path, **kwargs)

def request(method: str, path: str, **kwargs):
    return asyncio.run(_request(method, path, **kwargs))


def test_health_reports_not_ready_without_model(monkeypatch):
    monkeypatch.delenv("FACE_MODEL_PATH", raising=False)
    with patch("app.main.configured", return_value=False), patch("app.main.recognition_configured", return_value=False):
        response = request("get", "/health")
    assert response.status_code == 200
    assert response.json() == {
        "status": "ok", "ready": False, "recognitionReady": False, "mode": "research-only", "biometricDecisionsEnabled": False,
    }


def test_health_stays_not_ready_if_a_path_is_set(monkeypatch):
    monkeypatch.setenv("FACE_MODEL_PATH", "/path/to/unreviewed-model.onnx")
    with patch("app.main.configured", return_value=False):
        assert request("get", "/health").json()["ready"] is False

def test_embedding_requires_internal_token(monkeypatch):
    monkeypatch.setenv("FACE_SERVICE_TOKEN", "secret")
    response = request("post", "/internal/face/embedding", files={"frame": ("frame.jpg", b"x" * 128, "image/jpeg")})
    assert response.status_code == 401

def test_embedding_rejects_invalid_image(monkeypatch):
    monkeypatch.setenv("FACE_SERVICE_TOKEN", "secret")
    response = request("post", "/internal/face/embedding", headers={"X-Face-Service-Token": "secret"},
                       files={"frame": ("frame.jpg", b"not-an-image" * 16, "image/jpeg")})
    assert response.status_code == 200
    assert response.json() == {"status": "RETRY", "reason": "INVALID_IMAGE"}


def test_analysis_requires_internal_token(monkeypatch):
    monkeypatch.setenv("FACE_SERVICE_TOKEN", "secret")
    response = request("post", "/internal/face/analyse", files=[("frames", ("frame.png", b"x" * 128, "image/png"))])
    assert response.status_code == 401


def test_analysis_rejects_invalid_frame(monkeypatch):
    monkeypatch.setenv("FACE_SERVICE_TOKEN", "secret")
    response = request(
        "post", "/internal/face/analyse",
        headers={"X-Face-Service-Token": "secret"},
        data={"challenge": "turn_left_then_blink"},
        files=[("frames", ("frame.png", b"not-an-image" * 16, "image/png"))],
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid image frame"


def test_analysis_rejects_unknown_challenge(monkeypatch):
    monkeypatch.setenv("FACE_SERVICE_TOKEN", "secret")
    response = request(
        "post", "/internal/face/analyse",
        headers={"X-Face-Service-Token": "secret"},
        data={"challenge": "skip_liveness"},
        files=[("frames", ("frame.png", b"not-an-image" * 16, "image/png"))],
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid challenge"


def test_analysis_returns_research_liveness_without_enabling_enrollment(monkeypatch):
    from io import BytesIO
    from PIL import Image

    monkeypatch.setenv("FACE_SERVICE_TOKEN", "secret")
    output = BytesIO()
    Image.new("RGB", (64, 64), color="white").save(output, format="JPEG")
    monkeypatch.setattr("app.main.analyze_liveness_frames", lambda frames, challenge: {
        "decision": "RETRY", "mode": "EXPERIMENTAL_RESEARCH_ONLY", "framesProcessed": len(frames),
    })
    response = request(
        "post", "/internal/face/analyse",
        headers={"X-Face-Service-Token": "secret"},
        data={"challenge": "turn_left_then_blink"},
        files=[("frames", (f"frame-{i}.jpg", output.getvalue(), "image/jpeg")) for i in range(3)],
    )
    assert response.status_code == 200
    assert response.json()["mode"] == "EXPERIMENTAL_RESEARCH_ONLY"
    assert response.json()["framesProcessed"] == 3
