"""Provider Registry 契约测试。"""

import pytest
from pydantic import ValidationError

from lclai.providers import (
    ProviderDescriptor,
    ProviderKind,
    ProviderRegistry,
    ProviderStatus,
)


@pytest.mark.parametrize(
    ("configured", "available", "mock", "expected"),
    [
        (False, False, False, ProviderStatus.UNCONFIGURED),
        (True, True, False, ProviderStatus.AVAILABLE),
        (True, False, False, ProviderStatus.UNAVAILABLE),
        (False, False, True, ProviderStatus.MOCK),
    ],
)
def test_provider_status_is_derived_explicitly(
    configured: bool,
    available: bool,
    mock: bool,
    expected: ProviderStatus,
) -> None:
    provider = ProviderDescriptor(
        provider_id="contract-test",
        kind=ProviderKind.MODEL,
        display_name="契约测试",
        configured=configured,
        available=available,
        mock=mock,
    )

    assert provider.status is expected


def test_available_provider_must_be_configured() -> None:
    with pytest.raises(ValidationError, match="configured"):
        ProviderDescriptor(
            provider_id="invalid",
            kind=ProviderKind.NEWS,
            display_name="非法 Provider",
            configured=False,
            available=True,
        )


def test_provider_categories_degrade_independently() -> None:
    registry = ProviderRegistry(
        [
            ProviderDescriptor(
                provider_id="openai",
                kind=ProviderKind.MODEL,
                display_name="OpenAI",
                configured=True,
                available=False,
                diagnostic="连接检查失败",
            ),
            ProviderDescriptor(
                provider_id="local-market",
                kind=ProviderKind.MARKET_DATA,
                display_name="本地行情文件",
                configured=True,
                available=True,
            ),
            ProviderDescriptor(
                provider_id="mock-trading",
                kind=ProviderKind.TRADING,
                display_name="Mock 交易",
                mock=True,
            ),
        ]
    )

    assert registry.get("openai").status is ProviderStatus.UNAVAILABLE
    assert registry.get("local-market").status is ProviderStatus.AVAILABLE
    assert registry.get("mock-trading").status is ProviderStatus.MOCK
