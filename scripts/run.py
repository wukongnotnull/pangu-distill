#!/usr/bin/env python3
"""
盘古蒸馏信息采集入口

自动检测 Python 环境：
- 有 Python + uv → uv run（推荐，自动管理依赖）
- 有 Python 无 uv → pip install 后运行
- 无 Python → 提示安装
"""

import subprocess
import sys
import os
import shutil

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_SCRIPT = os.path.join(SCRIPT_DIR, "cli.py")


def check_command(cmd: str) -> bool:
    """检测命令是否存在"""
    return shutil.which(cmd) is not None


def check_python() -> bool:
    """检测 Python 是否可用"""
    try:
        result = subprocess.run(
            ["python3", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def run_with_uv(args: list):
    """使用 uv 运行"""
    result = subprocess.run(
        ["uv", "run", "--python", "3.9", "python", MAIN_SCRIPT] + args,
        cwd=SCRIPT_DIR,
    )
    return result.returncode


def run_with_pip(args: list):
    """使用 pip 安装依赖后运行"""
    print("📦 安装依赖...")
    install_result = subprocess.run(
        [sys.executable, "-m", "pip", "install", "-e", "."],
        cwd=SCRIPT_DIR,
        capture_output=True,
        text=True,
    )
    if install_result.returncode != 0:
        print("⚠️ 可编辑安装失败，改为只装依赖")
        print(install_result.stderr[-500:] if install_result.stderr else "")
        deps = subprocess.run(
            [
                sys.executable, "-m", "pip", "install",
                "requests>=2.28.0",
                "beautifulsoup4>=4.11.0",
                "lxml>=4.9.0",
                "html2text>=2020.1.16",
            ],
            cwd=SCRIPT_DIR,
            capture_output=True,
            text=True,
        )
        if deps.returncode != 0:
            print(f"❌ 安装失败: {deps.stderr}")
            return 1

    env = os.environ.copy()
    env["PYTHONPATH"] = SCRIPT_DIR + os.pathsep + env.get("PYTHONPATH", "")
    result = subprocess.run(
        [sys.executable, MAIN_SCRIPT] + args,
        cwd=SCRIPT_DIR,
        env=env,
    )
    return result.returncode


def run_path_command(args: list) -> int:
    """output-root / skill-root 不依赖搜索爬虫，直接跑。"""
    sys.path.insert(0, SCRIPT_DIR)
    from host_paths import detect_output_root, detect_skill_root, skill_output_dir

    if args[0] == "output-root":
        slug = None
        if len(args) >= 3 and args[1] == "--slug":
            slug = args[2]
        root = detect_output_root()
        print(skill_output_dir(slug, root) if slug else root)
        return 0

    root = detect_skill_root()
    if root is None:
        print(
            "未检测到 PANGU_SKILL_ROOT / CLAUDE_SKILL_DIR / CODEX_SKILL_DIR / CURSOR_SKILL_DIR",
            file=sys.stderr,
        )
        return 2
    print(root)
    return 0


def main():
    args = sys.argv[1:]

    if not args:
        # 无参数，显示帮助
        args = ["--help"]

    if args[0] in {"output-root", "skill-root"}:
        return run_path_command(args)

    # 检查 uv
    if check_command("uv"):
        print("🔧 使用 uv 运行...")
        return run_with_uv(args)

    # 检查 Python
    if check_python():
        print("🔧 使用 pip 运行...")
        return run_with_pip(args)

    # 无 Python
    print("=" * 60)
    print("❌ 未检测到 Python 3.9+ 环境")
    print()
    print("请先安装 Python：")
    print()
    print("macOS/Linux:")
    print("  curl -LsSf https://astral.sh/uv/install.sh | sh")
    print()
    print("Windows:")
    print('  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"')
    print()
    print("安装 uv 后，一条命令运行：")
    print("  uv run python run.py search \"芒格 思维框架\"")
    print("=" * 60)
    return 1


if __name__ == "__main__":
    sys.exit(main())
