import asyncio
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from app.main import app

async def _request(method: str, path: str, **kwargs):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        return await getattr(client, method)(path, **kwargs)

def request(method: str, path: str, **kwargs):
    return asyncio.run(_request(method, path, **kwargs))


def test_health_reports_not_ready_without_model(monkeypatch):
    monkeypatch.delenv("FACE_MODEL_PATH", raising=False)
    response = request("get", "/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "ready": False}


def test_health_stays_not_ready_if_a_path_is_set(monkeypatch):
    monkeypatch.setenv("FACE_MODEL_PATH", "/path/to/unreviewed-model.onnx")
    assert request("get", "/health").json()["ready"] is False


def test_analysis_requires_internal_token(monkeypatch):
    monkeypatch.setenv("FACE_SERVICE_TOKEN", "secret")
    response = request("post", "/internal/face/analyse", files=[("frames", ("frame.png", b"x" * 128, "image/png"))])
    assert response.status_code == 401


def test_analysis_rejects_invalid_frame(monkeypatch):
    monkeypatch.setenv("FACE_SERVICE_TOKEN", "secret")
    response = request(
        "post", "/internal/face/analyse",
        headers={"X-Face-Service-Token": "secret"},
        files=[("frames", ("frame.png", b"not-an-image" * 16, "image/png"))],
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid image frame"
