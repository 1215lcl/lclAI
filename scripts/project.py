"""lclAI 跨平台项目命令入口。"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
import subprocess
import sys
from typing import Final


ROOT: Final = Path(__file__).resolve().parents[1]
BACKEND: Final = ROOT / "backend"
FRONTEND: Final = ROOT / "frontend"


def executable(name: str) -> str:
    """返回当前平台对应的可执行文件名。"""

    if os.name == "nt" and name == "npm":
        return "npm.cmd"
    return name


def environment() -> dict[str, str]:
    """使用项目内缓存，避免依赖用户目录权限。"""

    env = os.environ.copy()
    cache_root = ROOT / ".cache"
    env.setdefault("UV_CACHE_DIR", str(cache_root / "uv"))
    env.setdefault("npm_config_cache", str(cache_root / "npm"))
    return env


def run(command: list[str], cwd: Path) -> None:
    """执行子命令并在失败时立即停止。"""

    print(f"[{cwd.relative_to(ROOT) or '.'}] {' '.join(command)}", flush=True)
    subprocess.run(command, cwd=cwd, env=environment(), check=True)


def setup() -> None:
    run(["uv", "sync", "--all-groups", "--frozen"], BACKEND)
    run([executable("npm"), "ci"], FRONTEND)


def test() -> None:
    run(["uv", "run", "pytest"], BACKEND)
    run([executable("npm"), "run", "test"], FRONTEND)


def check() -> None:
    run(["uv", "run", "ruff", "check", "src", "tests"], BACKEND)
    run(["uv", "run", "mypy", "src", "tests"], BACKEND)
    run([executable("npm"), "run", "lint"], FRONTEND)
    run([executable("npm"), "run", "typecheck"], FRONTEND)
    run(
        ["openspec", "validate", "--all", "--strict", "--no-interactive"],
        ROOT,
    )


def verify() -> None:
    """运行提交与 CI 共用的完整质量门禁。"""

    run(["uv", "run", "ruff", "check", "src", "tests"], BACKEND)
    run(["uv", "run", "mypy", "src", "tests"], BACKEND)
    run(["uv", "run", "pytest"], BACKEND)
    run([executable("npm"), "run", "check"], FRONTEND)
    run(
        ["openspec", "validate", "--all", "--strict", "--no-interactive"],
        ROOT,
    )


def build() -> None:
    run(["uv", "build"], BACKEND)
    run([executable("npm"), "run", "build"], FRONTEND)


def dev_backend() -> None:
    run(
        [
            "uv",
            "run",
            "uvicorn",
            "lclai.app:app",
            "--reload",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        ],
        BACKEND,
    )


def dev_frontend() -> None:
    run(
        [executable("npm"), "run", "dev", "--", "--host", "127.0.0.1"],
        FRONTEND,
    )


COMMANDS = {
    "setup": setup,
    "test": test,
    "check": check,
    "verify": verify,
    "build": build,
    "dev-backend": dev_backend,
    "dev-frontend": dev_frontend,
}


def main() -> None:
    parser = argparse.ArgumentParser(description="lclAI 项目命令")
    parser.add_argument("command", choices=COMMANDS)
    args = parser.parse_args()
    COMMANDS[args.command]()


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        raise SystemExit(error.returncode) from error
    except KeyboardInterrupt:
        sys.exit(130)
