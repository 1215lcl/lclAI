"""模型 Provider 显式选择契约测试。"""

from dataclasses import dataclass

import pytest
from pydantic import SecretStr

from lclai.config import AppSettings
from lclai.model_gateway import (
    ModelGateway,
    ModelProviderNotSelectedError,
    ModelSelection,
    describe_model_providers,
)


@dataclass
class StubAdapter:
    provider_id: str
    response: str = "ok"
    failure: Exception | None = None
    calls: int = 0

    def invoke(self, prompt: str, model_id: str) -> str:
        self.calls += 1
        if self.failure is not None:
            raise self.failure
        return f"{self.response}:{model_id}:{prompt}"


def test_model_invocation_requires_explicit_provider_selection() -> None:
    openai = StubAdapter("openai")
    gateway = ModelGateway([openai])

    with pytest.raises(ModelProviderNotSelectedError, match="显式选择"):
        gateway.invoke(None, "分析持仓")

    assert openai.calls == 0


def test_model_result_keeps_selected_provider_and_model_visible() -> None:
    gateway = ModelGateway([StubAdapter("openai", response="分析结果")])

    result = gateway.invoke(
        ModelSelection(provider_id="openai", model_id="gpt-test"),
        "分析持仓",
    )

    assert result.provider_id == "openai"
    assert result.model_id == "gpt-test"
    assert result.content == "分析结果:gpt-test:分析持仓"


def test_failed_provider_does_not_call_configured_backup() -> None:
    openai = StubAdapter("openai", failure=TimeoutError("调用超时"))
    ark = StubAdapter("ark")
    gateway = ModelGateway([openai, ark])

    with pytest.raises(TimeoutError, match="调用超时"):
        gateway.invoke(ModelSelection(provider_id="openai", model_id="gpt-test"), "分析行情")

    assert openai.calls == 1
    assert ark.calls == 0


def test_openai_and_ark_descriptions_never_contain_credentials() -> None:
    settings = AppSettings(
        openai_api_key=SecretStr("openai-secret"),
        openai_model_id="gpt-test",
        ark_api_key=SecretStr("ark-secret"),
        ark_model_id="ep-test",
    )

    descriptions = describe_model_providers(settings)
    serialized = " ".join(item.model_dump_json() for item in descriptions)

    assert {item.provider_id for item in descriptions} == {"openai", "ark"}
    assert all(item.credential_present for item in descriptions)
    assert "openai-secret" not in serialized
    assert "ark-secret" not in serialized
