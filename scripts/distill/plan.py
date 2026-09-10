"""查询计划：脚本出题，宿主搜索。

`plan` 不联网。它把「对象 + 类型」翻成六路查询、每路要找什么、结果落到哪个文件，
以及宿主 Agent 搜完之后应当写成什么样的 results.json 再交给 `ingest`。
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from .dimensions import (
    SOURCE_BLACKLIST,
    dimension_file,
    dimension_hint,
    dimension_label,
    dimensions_for,
    normalize_kind,
    query_locale,
)

PLAN_FILENAME = "plan.json"
RESULTS_FILENAME = "results.json"

RESULTS_TEMPLATE = {
    "target": "<对象>",
    "results": [
        {
            "dimension": "writings",
            "url": "https://…",
            "title": "页面标题",
            "snippet": "搜索摘要或你读到的关键一句",
            "source_type": "primary | secondary | inferred",
            "note": "可选：为什么选它 / 属于七级里的哪一级",
        }
    ],
}


@dataclass
class PlanQuery:
    dimension: str
    query: str
    file: str
    label: str
    hint: str

    def to_dict(self) -> dict:
        return {
            "dimension": self.dimension,
            "query": self.query,
            "file": self.file,
            "label": self.label,
            "hint": self.hint,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "PlanQuery":
        return cls(
            dimension=data["dimension"],
            query=data["query"],
            file=data.get("file") or dimension_file(data["dimension"]),
            label=data.get("label") or dimension_label(data["dimension"]),
            hint=data.get("hint") or dimension_hint(data["dimension"]),
        )


@dataclass
class Plan:
    target: str
    kind: str
    locale: str
    queries: List[PlanQuery]
    num_results: int = 8
    output_dir: Optional[str] = None
    blacklist: List[str] = field(default_factory=lambda: list(SOURCE_BLACKLIST))
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    @property
    def dimensions(self) -> List[str]:
        return [q.dimension for q in self.queries]

    def query_for(self, dimension: str) -> Optional[PlanQuery]:
        for q in self.queries:
            if q.dimension == dimension:
                return q
        return None

    def to_dict(self) -> dict:
        return {
            "target": self.target,
            "kind": self.kind,
            "locale": self.locale,
            "num_results": self.num_results,
            "output_dir": self.output_dir,
            "created_at": self.created_at,
            "blacklist": list(self.blacklist),
            "queries": [q.to_dict() for q in self.queries],
            "instructions": self.instructions(),
            "results_template": RESULTS_TEMPLATE,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Plan":
        return cls(
            target=data["target"],
            kind=data.get("kind", "person"),
            locale=data.get("locale") or query_locale(data["target"]),
            queries=[PlanQuery.from_dict(q) for q in data.get("queries", [])],
            num_results=int(data.get("num_results", 8)),
            output_dir=data.get("output_dir"),
            blacklist=list(data.get("blacklist", SOURCE_BLACKLIST)),
            created_at=data.get("created_at") or datetime.now().isoformat(timespec="seconds"),
        )

    def instructions(self) -> List[str]:
        return [
            f"用当前宿主的搜索工具逐条执行 {len(self.queries)} 路查询，每路取约 {self.num_results} 条。",
            "官方渠道优先；本人第一手优于转述；收最近 12 个月；每条标 URL 和 primary / secondary / inferred。",
            "黑名单域名不要收：" + "、".join(self.blacklist) + "。公众号原文可作一手，洗稿号不收。",
            "标题和摘要都不点名对象的页面丢掉。",
            f"把结果写成 {RESULTS_FILENAME}（格式见 results_template），然后跑 ingest。",
            "某一路搜不到就留空，ingest 会把空维度写进 00-sources.md；不要用别的维度凑数。",
        ]

    def to_markdown(self) -> str:
        lines = [
            f"# 查询计划：{self.target}",
            "",
            f"类型：{self.kind} · 查询语言：{self.locale} · 每路约 {self.num_results} 条 · 生成于 {self.created_at}",
            "",
            "| 维度 | 查询 | 落盘 | 要找什么 |",
            "|------|------|------|----------|",
        ]
        for q in self.queries:
            lines.append(f"| {q.dimension}（{q.label}） | `{q.query}` | `{q.file}` | {q.hint} |")
        lines.append("")
        lines.append("## 宿主 Agent 要做的事")
        lines.append("")
        for i, step in enumerate(self.instructions(), 1):
            lines.append(f"{i}. {step}")
        lines.append("")
        lines.append("## results.json 格式")
        lines.append("")
        lines.append("```json")
        lines.append(json.dumps(RESULTS_TEMPLATE, ensure_ascii=False, indent=2))
        lines.append("```")
        return "\n".join(lines) + "\n"

    def save(self, output_dir: Path) -> Path:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir = str(output_dir)
        path = output_dir / PLAN_FILENAME
        path.write_text(
            json.dumps(self.to_dict(), ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return path


def build_plan(
    target: str,
    kind: Optional[str] = None,
    num_results: int = 8,
    output_dir: Optional[Path] = None,
    dimensions: Optional[Dict[str, str]] = None,
) -> Plan:
    """按类型出六路查询。dimensions 可以覆盖（{维度名: 查询模板}）。

    D5 自我不出网络计划：dimensions_for 会抛 SelfKindError，由 CLI 转成退出码 2。
    """
    target = (target or "").strip()
    if not target:
        raise ValueError("对象不能为空")
    resolved_kind = normalize_kind(kind)
    templates = dimensions if dimensions is not None else dimensions_for(resolved_kind, target=target)
    queries = [
        PlanQuery(
            dimension=name,
            query=template.format(target=target),
            file=dimension_file(name),
            label=dimension_label(name),
            hint=dimension_hint(name),
        )
        for name, template in templates.items()
    ]
    return Plan(
        target=target,
        kind=resolved_kind,
        locale=query_locale(target),
        queries=queries,
        num_results=max(1, int(num_results)),
        output_dir=str(output_dir) if output_dir else None,
    )


def load_plan(path: Path) -> Plan:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return Plan.from_dict(data)


def parse_dimension_args(items: Optional[List[str]], target: str) -> Optional[Dict[str, str]]:
    """CLI 的 -d 参数：`name:query template` 或只给 name。"""
    if not items:
        return None
    dimensions: Dict[str, str] = {}
    for item in items:
        if ":" in item:
            name, query = item.split(":", 1)
            dimensions[name.strip()] = query.strip()
        else:
            dimensions[item.strip()] = "{target} " + item.strip()
    return dimensions
