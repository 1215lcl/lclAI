"""健康 API 契约测试。"""

from pathlib import Path

from fastapi.testclient import TestClient

from lclai.app import create_app
from lclai.providers import ProviderDescriptor, ProviderKind, ProviderRegistry
from lclai.storage import LocalStorage


def test_live_endpoint_reports_process_is_alive(tmp_path: Path) -> None:
    app = create_app(storage=LocalStorage(tmp_path / "state"))

    with TestClient(app) as client:
        response = client.get("/api/v1/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


def test_optional_provider_failure_does_not_block_core_readiness(
    tmp_path: Path,
) -> None:
    providers = ProviderRegistry(
        [
            ProviderDescriptor(
                provider_id="openai",
                kind=ProviderKind.MODEL,
                display_name="OpenAI",
                configured=True,
                available=False,
                diagnostic="连接检查失败",
            )
        ]
    )
    app = create_app(
        storage=LocalStorage(tmp_path / "state"),
        provider_registry=providers,
    )

    with TestClient(app) as client:
        ready_response = client.get("/api/v1/health/ready")
        providers_response = client.get("/api/v1/providers")

    assert ready_response.status_code == 200
    assert ready_response.json()["status"] == "ready"
    assert ready_response.json()["core"]["storage"] == "ready"
    assert providers_response.status_code == 200
    assert providers_response.json()["providers"][0]["status"] == "unavailable"


def test_storage_failure_makes_core_not_ready(tmp_path: Path) -> None:
    invalid_data_dir = tmp_path / "not-a-directory"
    invalid_data_dir.write_text("占位文件", encoding="utf-8")
    app = create_app(storage=LocalStorage(invalid_data_dir))

    with TestClient(app) as client:
        response = client.get("/api/v1/health/ready")

    assert response.status_code == 503
    assert response.json()["status"] == "not_ready"
    assert response.json()["core"]["storage"] == "not_ready"
    assert "storage_initialization_failed" in response.json()["detail"]
