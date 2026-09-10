"""极简 Markdown 解析：YAML 头 + 按标题切段。只用标准库。"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple


def parse_frontmatter(text: str) -> Tuple[Dict[str, str], str]:
    """极简 YAML 头：只认 `key: value` 和 `key: |` 块。不引第三方库。"""
    if not text.startswith("---"):
        return {}, text
    parts = text.split("\n")
    end = None
    for idx in range(1, len(parts)):
        if parts[idx].strip() == "---":
            end = idx
            break
    if end is None:
        return {}, text
    meta: Dict[str, str] = {}
    key = None
    block: List[str] = []
    for line in parts[1:end]:
        m = re.match(r"^([A-Za-z_][\w-]*):\s*(.*)$", line)
        if m and not line.startswith((" ", "\t")):
            if key and block:
                meta[key] = "\n".join(block).strip()
            key, value = m.group(1), m.group(2).strip()
            block = []
            if value in ("|", ">", "|-", ">-"):
                continue
            meta[key] = value.strip("'\"")
            key = None
        elif key is not None:
            block.append(line.strip())
    if key and block:
        meta[key] = "\n".join(block).strip()
    body = "\n".join(parts[end + 1 :])
    return meta, body


def split_sections(body: str, level: int = 2) -> List[Tuple[str, str]]:
    """按 `## ` 切段，返回 [(标题, 正文)]。"""
    pattern = re.compile(rf"^{'#' * level}\s+(.+?)\s*$", re.MULTILINE)
    matches = list(pattern.finditer(body))
    sections: List[Tuple[str, str]] = []
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        sections.append((m.group(1).strip(), body[start:end]))
    return sections


def find_section(sections: List[Tuple[str, str]], pattern: str) -> Optional[Tuple[str, str]]:
    rx = re.compile(pattern)
    for title, text in sections:
        if rx.search(title):
            return title, text
    return None
