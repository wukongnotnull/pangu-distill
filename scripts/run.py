#!/usr/bin/env python3
"""
盘古蒸馏脚本入口

plan / check / fidelity / output-root / skill-root 只用标准库，直接跑。
ingest / search / fetch / collect-local / transcribe 需要 requests + bs4：
- 有 uv → uv run（自动管理依赖）
- 有 Python 无 uv → pip install 后运行
- 无 Python → 提示安装
"""

import os
import shutil
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_SCRIPT = os.path.join(SCRIPT_DIR, "cli.py")

# 这些命令不依赖第三方包，跳过 uv / pip。
STDLIB_COMMANDS = {"plan", "check", "fidelity", "output-root", "skill-root", "-h", "--help"}


def check_command(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def run_direct(args: list) -> int:
    env = os.environ.copy()
    env["PYTHONPATH"] = SCRIPT_DIR + os.pathsep + env.get("PYTHONPATH", "")
    # 不切换 cwd：check <dir> / ingest results.json / -o 等相对路径要按调用者所在目录解析。
    result = subprocess.run([sys.executable, MAIN_SCRIPT] + args, env=env)
    return result.returncode


def deps_importable() -> bool:
    try:
        import requests  # noqa: F401
        import bs4  # noqa: F401
        import lxml  # noqa: F401
    except ImportError:
        return False
    return True


def run_with_uv(args: list) -> int:
    result = subprocess.run(
        ["uv", "run", "--project", SCRIPT_DIR, "python", MAIN_SCRIPT] + args,
    )
    return result.returncode


def run_with_pip(args: list) -> int:
    print("📦 安装依赖（requests / beautifulsoup4 / lxml）...", file=sys.stderr)
    deps = subprocess.run(
        [
            sys.executable, "-m", "pip", "install", "--quiet",
            "requests>=2.28.0",
            "beautifulsoup4>=4.11.0",
            "lxml>=4.9.0",
        ],
        cwd=SCRIPT_DIR,
        capture_output=True,
        text=True,
    )
    if deps.returncode != 0:
        print(f"❌ 安装失败: {deps.stderr[-800:]}", file=sys.stderr)
        print("   可改用: uv run python cli.py ...", file=sys.stderr)
        return 1
    return run_direct(args)


def main() -> int:
    args = sys.argv[1:] or ["--help"]

    if args[0] in STDLIB_COMMANDS:
        return run_direct(args)

    if deps_importable():
        return run_direct(args)

    if check_command("uv"):
        print("🔧 使用 uv 运行...", file=sys.stderr)
        return run_with_uv(args)

    if sys.version_info >= (3, 9):
        print("🔧 未检测到 uv，使用 pip 安装依赖...", file=sys.stderr)
        return run_with_pip(args)

    print("=" * 60)
    print("❌ 需要 Python 3.9+")
    print()
    print("macOS/Linux:  curl -LsSf https://astral.sh/uv/install.sh | sh")
    print('Windows:      powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"')
    print()
    print("安装 uv 后：uv run python run.py plan \"芒格\"")
    print("=" * 60)
    return 1


if __name__ == "__main__":
    sys.exit(main())
