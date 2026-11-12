"""模型 Provider 选择契约；本模块不实现任何外部调用。"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Protocol

from pydantic import BaseModel, ConfigDict, Field

from lclai.config import AppSettings


class ModelProviderNotSelectedError(ValueError):
    """未显式选择模型 Provider。"""


class ModelProviderUnavailableError(LookupError):
    """所选模型 Provider 未注册。"""


class ModelSelection(BaseModel):
    model_config = ConfigDict(frozen=True)

    provider_id: str = Field(pattern=r"^[a-z][a-z0-9_-]*$")
    model_id: str = Field(min_length=1)


class ModelProviderDescription(BaseModel):
    """可安全展示的非敏感模型配置。"""

    model_config = ConfigDict(frozen=True)

    provider_id: str
    display_name: str
    model_id: str | None
    base_url: str
    timeout_seconds: int
    max_retries: int
    credential_present: bool


class ModelInvocationResult(BaseModel):
    """保留显式选择信息的模型调用结果。"""

    model_config = ConfigDict(frozen=True)

    provider_id: str
    model_id: str
    content: str


class ModelAdapter(Protocol):
    provider_id: str

    def invoke(self, prompt: str, model_id: str) -> str: ...


class ModelGateway:
    """只把请求交给用户显式选择的 Adapter。"""

    def __init__(self, adapters: Iterable[ModelAdapter]) -> None:
        self._adapters: dict[str, ModelAdapter] = {}
        for adapter in adapters:
            if adapter.provider_id in self._adapters:
                raise ValueError(f"模型 Adapter 已存在：{adapter.provider_id}")
            self._adapters[adapter.provider_id] = adapter

    def invoke(
        self,
        selection: ModelSelection | None,
        prompt: str,
    ) -> ModelInvocationResult:
        if selection is None:
            raise ModelProviderNotSelectedError("必须显式选择模型 Provider")
        try:
            adapter = self._adapters[selection.provider_id]
        except KeyError as error:
            raise ModelProviderUnavailableError(
                f"模型 Provider 未注册：{selection.provider_id}"
            ) from error
        content = adapter.invoke(prompt, selection.model_id)
        return ModelInvocationResult(
            provider_id=selection.provider_id,
            model_id=selection.model_id,
            content=content,
        )


def describe_model_providers(
    settings: AppSettings,
) -> list[ModelProviderDescription]:
    """从秘密配置生成不含秘密值的描述。"""

    common = {
        "timeout_seconds": settings.model_timeout_seconds,
        "max_retries": settings.model_max_retries,
    }
    return [
        ModelProviderDescription(
            provider_id="openai",
            display_name="OpenAI",
            model_id=settings.openai_model_id,
            base_url=settings.openai_base_url,
            credential_present=settings.openai_api_key is not None,
            **common,
        ),
        ModelProviderDescription(
            provider_id="ark",
            display_name="火山方舟",
            model_id=settings.ark_model_id,
            base_url=settings.ark_base_url,
            credential_present=settings.ark_api_key is not None,
            **common,
        ),
    ]
