"""非敏感设置 API 测试。"""

from pathlib import Path

from fastapi.testclient import TestClient
from pydantic import SecretStr

from lclai.app import create_app
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
