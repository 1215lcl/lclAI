"""Provider 配置变更的本地非敏感审计。"""

from __future__ import annotations

import json
import re
import sqlite3
from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_SAFE_CONFIGURATION_FIELDS = {
    "base_url",
    "credential_present",
    "enabled",
    "max_retries",
    "model_id",
    "timeout_seconds",
}
_CREDENTIAL_FIELDS = {
    "apikey",
    "authorization",
    "password",
    "secret",
    "token",
    "accesstoken",
    "refreshtoken",
}


@dataclass(frozen=True, slots=True)
class ConfigAuditRecord:
    id: int
    provider_id: str
    summary: dict[str, Any]
    changed_at: datetime
    success: bool


def _normalize_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def _safe_summary(configuration: Mapping[str, object]) -> dict[str, object]:
    summary: dict[str, object] = {}
    credential_present = False
    for key, value in configuration.items():
        if key in _SAFE_CONFIGURATION_FIELDS:
            summary[key] = value if isinstance(value, (str, int, float, bool)) else str(value)
        if _normalize_key(key) in _CREDENTIAL_FIELDS and bool(value):
            credential_present = True
    if credential_present:
        summary["credential_present"] = True
    return summary


class ConfigAuditRepository:
    """把非敏感配置摘要持久化到核心 SQLite。"""

    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS config_audit (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider_id TEXT NOT NULL,
                    summary_json TEXT NOT NULL,
                    changed_at TEXT NOT NULL,
                    success INTEGER NOT NULL CHECK (success IN (0, 1))
                )
                """
            )

    def record_config_change(
        self,
        provider_id: str,
        configuration: Mapping[str, object],
        *,
        success: bool,
    ) -> int:
        summary_json = json.dumps(
            _safe_summary(configuration),
            ensure_ascii=False,
            sort_keys=True,
        )
        changed_at = datetime.now(UTC).isoformat()
        with self._connect() as connection:
            cursor = connection.execute(
                """
                INSERT INTO config_audit (
                    provider_id, summary_json, changed_at, success
                ) VALUES (?, ?, ?, ?)
                """,
                (provider_id, summary_json, changed_at, int(success)),
            )
            record_id = cursor.lastrowid
        if record_id is None:
            raise RuntimeError("配置审计记录写入失败")
        return record_id

    def list_recent(self, limit: int = 100) -> list[ConfigAuditRecord]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, provider_id, summary_json, changed_at, success
                FROM config_audit
                ORDER BY id DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [
            ConfigAuditRecord(
                id=row["id"],
                provider_id=row["provider_id"],
                summary=json.loads(row["summary_json"]),
                changed_at=datetime.fromisoformat(row["changed_at"]),
                success=bool(row["success"]),
            )
            for row in rows
        ]
