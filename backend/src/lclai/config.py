"""类型化应用配置。"""

from functools import lru_cache
from ipaddress import ip_address
from pathlib import Path
from urllib.parse import urlparse

from pydantic import Field, IPvAnyAddress, SecretStr, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """从环境变量加载的本地工作台配置。"""

    model_config = SettingsConfigDict(
        env_prefix="LCLAI_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        validate_default=True,
    )

    host: IPvAnyAddress = ip_address("127.0.0.1")
    port: int = 8000
    data_dir: Path = Path("data")
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://127.0.0.1:5173",
            "http://localhost:5173",
        ]
    )
    openai_api_key: SecretStr | None = None
    openai_model_id: str | None = None
    openai_base_url: str = "https://api.openai.com/v1"
    ark_api_key: SecretStr | None = None
    ark_model_id: str | None = None
    ark_base_url: str = "https://ark.cn-beijing.volces.com/api/v3"
    model_timeout_seconds: int = 60
    model_max_retries: int = 2

    @field_validator("host")
    @classmethod
    def require_loopback(cls, value: IPvAnyAddress) -> IPvAnyAddress:
        if not value.is_loopback:
            raise ValueError("服务只允许绑定本机回环地址")
        return value

    @field_validator("cors_origins")
    @classmethod
    def require_local_cors_origins(cls, values: list[str]) -> list[str]:
        for value in values:
            parsed = urlparse(value)
            hostname = parsed.hostname
            if parsed.scheme not in {"http", "https"} or hostname is None:
                raise ValueError(f"CORS 来源格式无效：{value}")
            is_loopback = hostname == "localhost"
            if not is_loopback:
                try:
                    is_loopback = ip_address(hostname).is_loopback
                except ValueError:
                    is_loopback = False
            if not is_loopback:
                raise ValueError(f"CORS 来源必须是本机回环地址：{value}")
        return values


@lru_cache
def get_settings() -> AppSettings:
    """返回进程内唯一的配置实例。"""

    return AppSettings()
