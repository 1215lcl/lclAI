"""模型 Provider 的非敏感配置更新与审计。"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any, ClassVar
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from lclai.audit import ConfigAuditRepository
from lclai.config import AppSettings
from lclai.model_gateway import ModelProviderDescription, describe_model_providers
from lclai.providers import ProviderDescriptor, ProviderRegistry


class ModelProviderConfigUpdate(BaseModel):
    """只允许更新可安全持久化和展示的模型配置。"""

    model_config = ConfigDict(extra="forbid", frozen=True)

    model_id: str = Field(min_length=1)
    base_url: str
    timeout_seconds: int = Field(ge=1, le=300)
    max_retries: int = Field(ge=0, le=10)

    @field_validator("model_id")
    @classmethod
    def require_non_blank_model_id(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("模型标识不得为空")
        return value

    @field_validator("base_url")
    @classmethod
    def require_safe_http_base_url(cls, value: str) -> str:
        value = value.strip().rstrip("/")
        parsed = urlparse(value)
        if parsed.scheme not in {"http", "https"} or parsed.hostname is None:
            raise ValueError("数据面地址必须是有效的 HTTP(S) URL")
        if parsed.username or parsed.password or parsed.query or parsed.fragment:
            raise ValueError("数据面地址不得包含凭据、查询参数或片段")
        return value


class ProviderConfigNotFoundError(LookupError):
    """请求更新的 Provider 不受支持。"""


class ProviderConfigValidationError(ValueError):
    """不包含原始输入值的字段校验错误。"""

    def __init__(self, fields: list[dict[str, str]]) -> None:
        super().__init__("Provider 配置无效")
        self.fields = fields


class ModelProviderConfigService:
    """验证、审计并应用进程内非敏感模型配置。"""

    _SETTING_FIELDS: ClassVar[dict[str, tuple[str, str, str]]] = {
        "openai": ("openai_model_id", "openai_base_url", "OpenAI"),
        "ark": ("ark_model_id", "ark_base_url", "火山方舟"),
    }

    def __init__(
        self,
        settings: AppSettings,
        registry: ProviderRegistry,
        audit_repository: ConfigAuditRepository,
    ) -> None:
        self._settings = settings
        self._registry = registry
        self._audit_repository = audit_repository

    def update(
        self,
        provider_id: str,
        configuration: Mapping[str, Any],
    ) -> ModelProviderDescription:
        fields = self._SETTING_FIELDS.get(provider_id)
        if fields is None:
            raise ProviderConfigNotFoundError(f"不支持的模型 Provider：{provider_id}")

        try:
            update = ModelProviderConfigUpdate.model_validate(configuration)
        except ValidationError as error:
            self._audit_repository.record_config_change(
                provider_id,
                configuration,
                success=False,
            )
            safe_errors = [
                {
                    "field": ".".join(str(item) for item in issue["loc"]),
                    "message": issue["msg"],
                    "type": issue["type"],
                }
                for issue in error.errors()
            ]
            raise ProviderConfigValidationError(safe_errors) from error

        summary = update.model_dump()
        self._audit_repository.record_config_change(
            provider_id,
            summary,
            success=True,
        )

        model_field, base_url_field, display_name = fields
        setattr(self._settings, model_field, update.model_id)
        setattr(self._settings, base_url_field, update.base_url)
        self._settings.model_timeout_seconds = update.timeout_seconds
        self._settings.model_max_retries = update.max_retries

        credential = getattr(self._settings, f"{provider_id}_api_key")
        self._registry.replace(
            ProviderDescriptor(
                provider_id=provider_id,
                kind=self._registry.get(provider_id).kind,
                display_name=display_name,
                configured=credential is not None and bool(update.model_id),
                diagnostic="基础阶段不执行真实模型健康调用",
            )
        )

        return next(
            provider
            for provider in describe_model_providers(self._settings)
            if provider.provider_id == provider_id
        )
