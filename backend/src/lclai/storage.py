"""SQLite 核心状态存储。"""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class StorageReadiness:
    """不包含秘密信息的存储就绪结果。"""

    ready: bool
    code: str
    detail: str


class LocalStorage:
    """管理工作台核心 SQLite 文件的初始化。"""

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = data_dir
        self.database_path = data_dir / "lclai.sqlite3"

    def initialize(self) -> StorageReadiness:
        try:
            self.data_dir.mkdir(parents=True, exist_ok=True)
            with sqlite3.connect(self.database_path) as connection:
                connection.execute("PRAGMA foreign_keys = ON")
                connection.execute("SELECT 1")
        except (OSError, sqlite3.Error) as error:
            return StorageReadiness(
                ready=False,
                code="storage_initialization_failed",
                detail=(
                    f"无法初始化本地存储 {self.data_dir}: "
                    f"{type(error).__name__}: {error}"
                ),
            )

        return StorageReadiness(
            ready=True,
            code="ready",
            detail=f"SQLite 已就绪：{self.database_path}",
        )
