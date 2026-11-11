"""本地核心存储契约测试。"""

from pathlib import Path

from lclai.storage import LocalStorage


def test_sqlite_storage_can_be_initialized_repeatedly(tmp_path: Path) -> None:
    storage = LocalStorage(tmp_path / "state")

    first = storage.initialize()
    second = storage.initialize()

    assert first.ready is True
    assert second.ready is True
    assert storage.database_path.is_file()


def test_storage_initialization_failure_is_diagnostic(tmp_path: Path) -> None:
    invalid_directory = tmp_path / "not-a-directory"
    invalid_directory.write_text("占位文件", encoding="utf-8")

    result = LocalStorage(invalid_directory).initialize()

    assert result.ready is False
    assert result.code == "storage_initialization_failed"
    assert "not-a-directory" in result.detail
