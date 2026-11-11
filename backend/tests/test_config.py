"""应用配置契约测试。"""

from ipaddress import ip_address

import pytest
from pydantic import ValidationError

from lclai.config import AppSettings


@pytest.fixture(autouse=True)
def clear_external_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "LCLAI_HOST",
        "LCLAI_OPENAI_API_KEY",
        "LCLAI_ARK_API_KEY",
    ):
        monkeypatch.delenv(name, raising=False)


def test_default_settings_bind_only_to_loopback_without_credentials() -> None:
    settings = AppSettings()

    assert settings.host == ip_address("127.0.0.1")
    assert settings.openai_api_key is None
    assert settings.ark_api_key is None


def test_non_loopback_bind_address_is_rejected() -> None:
    with pytest.raises(ValidationError, match="回环地址"):
        AppSettings(host=ip_address("0.0.0.0"))


def test_non_local_cors_origin_is_rejected() -> None:
    with pytest.raises(ValidationError, match="CORS"):
        AppSettings(cors_origins=["https://example.com"])
