"""后端测试的全局隔离夹具。"""

from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def isolate_test_working_directory(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    """避免测试隐式读取开发者的 backend/.env 和运行数据。"""

    monkeypatch.chdir(tmp_path)
