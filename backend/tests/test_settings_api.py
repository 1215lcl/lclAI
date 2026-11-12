"""非敏感设置 API 测试。"""

from pathlib import Path

from fastapi.testclient import TestClient
from pydantic import SecretStr

from lclai.app import create_app
from lclai.audit import ConfigAuditRepository
from lclai.config import AppSettings
from lclai.storage import LocalStorage


def test_model_settings_response_never_exposes_credentials(tmp_path: Path) -> None:
    settings = AppSettings(
        data_dir=tmp_path / "state",
        openai_api_key=SecretStr("openai-secret-must-not-render"),
        openai_model_id=None,
        ark_api_key=SecretStr("ark-secret-must-not-render"),
        ark_model_id="ep-test",
    )
    app = create_app(settings=settings, storage=LocalStorage(settings.data_dir))

    with TestClient(app) as client:
        response = client.get("/api/v1/settings/providers")

    serialized = response.text
    providers = response.json()["providers"]
    assert response.status_code == 200
    assert providers[0]["credential_present"] is True
    assert providers[0]["model_id"] is None
    assert providers[1]["credential_present"] is True
    assert "openai-secret-must-not-render" not in serialized
    assert "ark-secret-must-not-render" not in serialized


def test_valid_model_config_update_is_applied_and_audited(tmp_path: Path) -> None:
    settings = AppSettings(
        data_dir=tmp_path / "state",
        openai_api_key=SecretStr("openai-secret-must-not-persist"),
        openai_model_id=None,
    )
    storage = LocalStorage(settings.data_dir)
    app = create_app(settings=settings, storage=storage)

    with TestClient(app) as client:
        update_response = client.put(
            "/api/v1/settings/providers/openai",
            json={
                "model_id": "gpt-test",
                "base_url": "https://api.openai.com/v1",
                "timeout_seconds": 30,
                "max_retries": 1,
            },
        )
        settings_response = client.get("/api/v1/settings/providers")
        providers_response = client.get("/api/v1/providers")

    assert update_response.status_code == 200
    assert update_response.json()["provider"]["model_id"] == "gpt-test"
    assert settings_response.json()["providers"][0]["model_id"] == "gpt-test"
    assert providers_response.json()["providers"][0]["status"] == "unavailable"

    records = ConfigAuditRepository(storage.database_path).list_recent()
    assert len(records) == 1
    assert records[0].provider_id == "openai"
    assert records[0].success is True
    assert records[0].summary["model_id"] == "gpt-test"
    assert b"openai-secret-must-not-persist" not in storage.database_path.read_bytes()


def test_invalid_or_sensitive_model_config_update_is_rejected_and_audited(
    tmp_path: Path,
) -> None:
    settings = AppSettings(data_dir=tmp_path / "state", openai_model_id="original")
    storage = LocalStorage(settings.data_dir)
    app = create_app(settings=settings, storage=storage)

    with TestClient(app) as client:
        response = client.put(
            "/api/v1/settings/providers/openai",
            json={
                "model_id": " ",
                "base_url": "not-a-url",
                "timeout_seconds": 0,
                "max_retries": -1,
                "api_key": "secret-must-never-persist",
            },
        )
        current = client.get("/api/v1/settings/providers")

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "invalid_provider_config"
    assert "secret-must-never-persist" not in response.text
    assert current.json()["providers"][0]["model_id"] == "original"

    records = ConfigAuditRepository(storage.database_path).list_recent()
    assert len(records) == 1
    assert records[0].success is False
    assert b"secret-must-never-persist" not in storage.database_path.read_bytes()
