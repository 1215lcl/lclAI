"""本机 CORS 与静态前端托管集成测试。"""

from pathlib import Path

from fastapi.testclient import TestClient

from lclai.app import create_app
from lclai.config import AppSettings
from lclai.storage import LocalStorage


def test_cors_allows_configured_loopback_and_rejects_external_origin(
    tmp_path: Path,
) -> None:
    settings = AppSettings(data_dir=tmp_path / "state")
    app = create_app(settings=settings, storage=LocalStorage(settings.data_dir))

    with TestClient(app) as client:
        allowed = client.options(
            "/api/v1/health/live",
            headers={
                "Origin": "http://127.0.0.1:5173",
                "Access-Control-Request-Method": "GET",
            },
        )
        rejected = client.options(
            "/api/v1/health/live",
            headers={
                "Origin": "https://example.com",
                "Access-Control-Request-Method": "GET",
            },
        )

    assert allowed.headers["access-control-allow-origin"] == "http://127.0.0.1:5173"
    assert "access-control-allow-origin" not in rejected.headers


def test_frontend_build_is_served_without_shadowing_api(tmp_path: Path) -> None:
    static_dir = tmp_path / "dist"
    assets_dir = static_dir / "assets"
    assets_dir.mkdir(parents=True)
    (static_dir / "index.html").write_text("<h1>lclAI shell</h1>", encoding="utf-8")
    (assets_dir / "app.js").write_text("console.log('lclAI')", encoding="utf-8")
    settings = AppSettings(data_dir=tmp_path / "state")
    app = create_app(
        settings=settings,
        storage=LocalStorage(settings.data_dir),
        frontend_dist=static_dir,
    )

    with TestClient(app) as client:
        root_response = client.get("/")
        route_response = client.get("/settings")
        asset_response = client.get("/assets/app.js")
        api_response = client.get("/api/v1/health/live")

    assert root_response.status_code == 200
    assert "lclAI shell" in root_response.text
    assert route_response.status_code == 200
    assert "lclAI shell" in route_response.text
    assert asset_response.status_code == 200
    assert api_response.json() == {"status": "alive"}
