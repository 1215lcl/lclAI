"""日志与响应共用的秘密信息脱敏工具。"""

from __future__ import annotations

import logging
import re
from collections.abc import Mapping, Sequence
from typing import Any

REDACTED = "[REDACTED]"

_SENSITIVE_KEYS = {
    "apikey",
    "authorization",
    "token",
    "accesstoken",
    "refreshtoken",
    "secret",
    "password",
}
_AUTHORIZATION_PATTERN = re.compile(
    r"(?i)(authorization\s*[:=]\s*(?:bearer\s+)?)([^\s,;]+)"
)
_NAMED_SECRET_PATTERN = re.compile(
    r"(?i)\b(api[_-]?key|access[_-]?token|refresh[_-]?token|token)"
    r"(\s*[:=]\s*)(?:['\"])?([^'\"\s,;}]+)(?:['\"])?"
)
_OPENAI_STYLE_KEY_PATTERN = re.compile(r"\bsk-[A-Za-z0-9_-]{8,}\b")


def _normalized_key(value: object) -> str:
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def redact_text(value: str) -> str:
    """遮蔽文本中的常见 Authorization、Token 和 API Key 格式。"""

    value = _AUTHORIZATION_PATTERN.sub(rf"\1{REDACTED}", value)
    value = _NAMED_SECRET_PATTERN.sub(rf"\1\2{REDACTED}", value)
    return _OPENAI_STYLE_KEY_PATTERN.sub(REDACTED, value)


def redact(value: Any) -> Any:
    """递归复制并脱敏可序列化响应数据。"""

    if isinstance(value, Mapping):
        return {
            key: REDACTED if _normalized_key(key) in _SENSITIVE_KEYS else redact(item)
            for key, item in value.items()
        }
    if isinstance(value, str):
        return redact_text(value)
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return [redact(item) for item in value]
    return value


class SecretRedactionFilter(logging.Filter):
    """在日志记录交给 Handler 前遮蔽秘密。"""

    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = redact_text(record.getMessage())
        record.args = ()
        return True
