"""跨宿主 Skill 路径。

一份 SKILL.md 可以在多个 Agent 上跑，差别只是发现目录。
产出目录优先用已经存在的项目 skills 目录，否则默认创建 .agents/skills/。
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Iterable, List, Mapping, Optional, Sequence


SKILL_SLUG = "pangu-distill"

# 项目级：先探测到谁用谁。顺序按「跨宿主默认 → 各家目录」。
PROJECT_SKILL_DIRS: Sequence[str] = (
    ".agents/skills",
    ".cursor/skills",
    ".claude/skills",
    ".codex/skills",
    ".github/skills",
    "skills",
)

# 用户级安装目标（与 host-compatibility.md 共用这张表）
USER_INSTALL_DIRS: Mapping[str, str] = {
    "agents": "~/.agents/skills",
    "claude": "~/.claude/skills",
    "codex": "~/.codex/skills",
    "openclaw": "~/.openclaw/skills",
    "gemini": "~/.gemini/skills",
    "copilot": "~/.config/github-copilot/skills",
    "hermes": "~/.hermes/skills",
    "opencode": "~/.config/opencode/skills",
}

PROJECT_INSTALL_DIRS: Mapping[str, str] = {
    "agents": ".agents/skills",
    "cursor": ".cursor/skills",
    "claude": ".claude/skills",
    "codex": ".codex/skills",
    "copilot": ".github/skills",
    "openclaw": "skills",
}

SKILL_ROOT_ENV_CANDIDATES: Sequence[str] = (
    "PANGU_SKILL_ROOT",
    "CLAUDE_SKILL_DIR",
    "CODEX_SKILL_DIR",
    "CURSOR_SKILL_DIR",
)


def find_project_root(start: Optional[Path] = None) -> Path:
    """从 start 向上找到 git 根；找不到就返回 start。"""
    here = (start or Path.cwd()).resolve()
    for candidate in (here, *here.parents):
        if (candidate / ".git").exists():
            return candidate
    return here


def detect_output_root(
    cwd: Optional[Path] = None,
    env: Optional[Mapping[str, str]] = None,
) -> Path:
    """蒸馏产物应写入的项目 skills 目录（不含 skill 名）。"""
    environ = env if env is not None else os.environ
    override = (environ.get("PANGU_OUTPUT_ROOT") or "").strip()
    if override:
        return Path(override).expanduser()

    root = find_project_root(cwd)
    for rel in PROJECT_SKILL_DIRS:
        path = root / rel
        if path.is_dir():
            return path
    return root / ".agents/skills"


def detect_skill_root(env: Optional[Mapping[str, str]] = None) -> Optional[Path]:
    """宿主已注入的本 Skill 根目录。都没有则返回 None，由 Agent 用加载路径补。"""
    environ = env if env is not None else os.environ
    for key in SKILL_ROOT_ENV_CANDIDATES:
        value = (environ.get(key) or "").strip()
        if value:
            return Path(value).expanduser()
    return None


def product_skill_name(object_slug: str) -> str:
    """产物目录 / YAML name：`pangu-[对象]`。母体 `pangu-distill` 不可占用。"""
    slug = (object_slug or "").strip().lower().replace("_", "-").replace(" ", "-")
    while "--" in slug:
        slug = slug.replace("--", "-")
    slug = slug.strip("-")
    if slug.startswith("pangu-"):
        slug = slug[len("pangu-") :]
    if slug.endswith("-distill"):
        slug = slug[: -len("-distill")]
    if not slug or slug == "distill":
        raise ValueError(
            "产物不能叫 pangu-distill（那是母体）。请用 pangu-[对象]，对象 slug 不能是 distill。"
        )
    return f"pangu-{slug}"


def skill_output_dir(slug: str, output_root: Optional[Path] = None) -> Path:
    return (output_root or detect_output_root()) / product_skill_name(slug)


def expand_user_install_dir(host: str) -> Path:
    rel = USER_INSTALL_DIRS[host]
    return Path(rel).expanduser() / SKILL_SLUG


def project_install_dir(host: str, project_root: Optional[Path] = None) -> Path:
    root = (project_root or find_project_root()).resolve()
    return root / PROJECT_INSTALL_DIRS[host] / SKILL_SLUG


def known_hosts(*, project: bool = False) -> List[str]:
    table = PROJECT_INSTALL_DIRS if project else USER_INSTALL_DIRS
    return list(table.keys())


def iter_user_targets(hosts: Iterable[str]) -> List[Path]:
    return [expand_user_install_dir(h) for h in hosts]
