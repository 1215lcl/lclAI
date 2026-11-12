"""外部能力 Provider 的最小状态契约。"""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, computed_field, model_validator


class ProviderKind(StrEnum):
    MODEL = "model"
    MARKET_DATA = "market_data"
    NEWS = "news"
    VECTOR_STORE = "vector_store"
    TRADING = "trading"


class ProviderStatus(StrEnum):
    UNCONFIGURED = "unconfigured"
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    MOCK = "mock"


class ProviderDescriptor(BaseModel):
    """可安全返回给界面的 Provider 描述。"""

    model_config = ConfigDict(frozen=True)

    provider_id: str = Field(pattern=r"^[a-z][a-z0-9_-]*$")
    kind: ProviderKind
    display_name: str = Field(min_length=1)
    configured: bool = False
    available: bool = False
    mock: bool = False
    diagnostic: str | None = None
    last_checked_at: datetime | None = None

    @model_validator(mode="after")
    def validate_state_flags(self) -> ProviderDescriptor:
        if self.available and not self.configured:
            raise ValueError("available Provider 必须 configured")
        if self.mock and self.available:
            raise ValueError("Mock Provider 不得同时标记 available")
        return self

    @computed_field  # type: ignore[prop-decorator]
    @property
    def status(self) -> ProviderStatus:
        if self.mock:
            return ProviderStatus.MOCK
        if not self.configured:
            return ProviderStatus.UNCONFIGURED
        if self.available:
            return ProviderStatus.AVAILABLE
        return ProviderStatus.UNAVAILABLE


class ProviderRegistry:
    """按标识注册 Provider，不聚合或覆盖单项状态。"""

    def __init__(self, providers: Iterable[ProviderDescriptor] = ()) -> None:
        self._providers: dict[str, ProviderDescriptor] = {}
        for provider in providers:
            self.register(provider)

    def register(self, provider: ProviderDescriptor) -> None:
        if provider.provider_id in self._providers:
            raise ValueError(f"Provider 已存在：{provider.provider_id}")
        self._providers[provider.provider_id] = provider

    def get(self, provider_id: str) -> ProviderDescriptor:
        return self._providers[provider_id]

    def replace(self, provider: ProviderDescriptor) -> None:
        """替换已注册 Provider 的状态，不允许隐式新增。"""

        if provider.provider_id not in self._providers:
            raise KeyError(provider.provider_id)
        self._providers[provider.provider_id] = provider

    def list(self) -> list[ProviderDescriptor]:
        return list(self._providers.values())
