"""示例配置文件验证。"""

from pathlib import Path

from lclai.config import AppSettings


def test_example_config_has_no_credentials_and_validates() -> None:
    example_path = Path(__file__).parents[1] / ".env.example"
    payload: dict[str, str] = {}

    for raw_line in example_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        name, value = line.split("=", maxsplit=1)
        if value:
            payload[name.removeprefix("LCLAI_").lower()] = value

    settings = AppSettings.model_validate(payload)

    assert settings.openai_api_key is None
    assert settings.ark_api_key is None
    assert str(settings.host) == "127.0.0.1"
