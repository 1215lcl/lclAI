"""秘密信息脱敏测试。"""

import json
import logging

import pytest

from lclai.redaction import REDACTED, SecretRedactionFilter, redact


def test_nested_response_fields_are_redacted_without_mutating_source() -> None:
    source = {
        "provider": "openai",
        "api_key": "sk-api-secret-123456",
        "nested": {
            "Authorization": "Bearer bearer-secret-123456",
            "token": "token-secret-123456",
        },
    }

    result = redact(source)
    serialized = json.dumps(result)

    assert result == {
        "provider": "openai",
        "api_key": REDACTED,
        "nested": {"Authorization": REDACTED, "token": REDACTED},
    }
    assert source["api_key"] == "sk-api-secret-123456"
    assert "secret-123456" not in serialized


def test_log_filter_removes_common_secret_formats(
    caplog: pytest.LogCaptureFixture,
) -> None:
    logger = logging.getLogger("lclai.redaction.contract")
    redaction_filter = SecretRedactionFilter()
    logger.addFilter(redaction_filter)
    caplog.set_level(logging.ERROR, logger=logger.name)

    try:
        logger.error(
            "request failed Authorization: Bearer %s api_key=%s token=%s",
            "bearer-secret-123456",
            "sk-api-secret-123456",
            "token-secret-123456",
        )
    finally:
        logger.removeFilter(redaction_filter)

    assert "bearer-secret-123456" not in caplog.text
    assert "sk-api-secret-123456" not in caplog.text
    assert "token-secret-123456" not in caplog.text
    assert REDACTED in caplog.text
