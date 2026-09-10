"""把宿主搜到的结果落成 references/distillation/ 底稿。

输入：plan.json + results.json（宿主 Agent 按 plan 搜索后写的）。
处理：校验维度 → 剔除黑名单 → 跨维度去重 → 抓正文 → 按维度写 01–07 底稿 → 写 00-sources.md。
输出：
- `0N-*.md`            每维一份素材底稿（来源表 + 摘录 + 待填的七级提取记录）
- `00-sources.md`      全部来源清单、一手占比、剔除 / 失败 / 空维度、采集日志
- `ingest_result.json` 完整数据（含正文，交付前可删）
- `ingest_summary.json` 统计（check 会读）

脚本不判断内容好坏。它只保证：每条有 URL、有一手 / 二手标注、没有黑名单、没有重复、失败有记录。
"""

from __future__ import annotations

import json
import re
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence
from urllib.parse import unquote, urlparse

from .dimensions import dimension_file, dimension_hint, dimension_label
from .plan import Plan

INGEST_MARKER = "<!-- pangu:ingest"
RESULT_FILENAME = "ingest_result.json"
SUMMARY_FILENAME = "ingest_summary.json"
SOURCES_FILENAME = "00-sources.md"

SOURCE_TYPES = ("primary", "secondary", "inferred", "unknown")
_SOURCE_TYPE_ALIASES = {
    "primary": "primary",
    "一手": "primary",
    "first-hand": "primary",
    "firsthand": "primary",
    "secondary": "secondary",
    "二手": "secondary",
    "inferred": "inferred",
    "推断": "inferred",
    "inference": "inferred",
}
_SOURCE_TYPE_LABELS = {
    "primary": "一手",
    "secondary": "二手",
    "inferred": "推断",
    "unknown": "未标",
}

EXTRACTION_STUB = """## 提取记录（待填，按七级清单）

先扫 1–4 级：信念形成故事 / 真实决策复盘 / 本人承认的失败 / 内在矛盾。
没有形成故事的金句不进 Skill。每条写出处，矛盾不调和。

### [编号] [标题]
- **优先级**：1-7
- **原文**：「……」
- **出处**：[上面素材的编号 + 段落 / 时间戳]
- **类型**：信念形成 / 决策复盘 / 失败承认 / 内在矛盾 / 认知边界 / 思维习惯 / 通用观点
- **内容**：
- **交叉**：★ / 来源单一 / 与 [编号] 矛盾
"""


# 正文有效性：WAF 挑战页、加密 JS、base64 块会以 200 + text/html 回来，抓取器认为「成功」。
# 这里只做机器能判的：可读字符占比、超长无空格字母数字块占比、最短长度。
MIN_CONTENT_CHARS = 150
MIN_READABLE_RATIO = 0.5
MAX_BLOB_RATIO = 0.3
BLOB_TOKEN_MIN = 40
_READABLE_RE = re.compile(r"[\u4e00-\u9fff\u3040-\u30ff\uac00-\ud7afA-Za-z]")
_BLOB_TOKEN_RE = re.compile(r"[A-Za-z0-9+/=_\-]{%d,}" % BLOB_TOKEN_MIN)


def content_validity(text: str) -> Optional[str]:
    """正文能不能当素材。返回 None = 有效；否则返回一句失败原因（写进 fetch_error）。"""
    stripped = re.sub(r"\s+", "", text or "")
    if not stripped:
        return "正文为空"
    if len(stripped) < MIN_CONTENT_CHARS:
        return f"正文过短（{len(stripped)} 字 < {MIN_CONTENT_CHARS}）"
    blob_chars = sum(len(m.group(0)) for m in _BLOB_TOKEN_RE.finditer(text))
    blob_ratio = blob_chars / len(stripped)
    if blob_ratio > MAX_BLOB_RATIO:
        return f"正文疑似乱码 / 加密内容（{blob_ratio:.0%} 为超长字母数字块，WAF 或反爬页）"
    readable = len(_READABLE_RE.findall(stripped))
    readable_ratio = readable / len(stripped)
    if readable_ratio < MIN_READABLE_RATIO:
        return f"正文可读字符占比 {readable_ratio:.0%} < {MIN_READABLE_RATIO:.0%}，疑似非文本"
    return None


def normalize_source_type(value: Optional[str]) -> str:
    key = (value or "").strip().lower()
    return _SOURCE_TYPE_ALIASES.get(key, "unknown")


def source_type_label(value: str) -> str:
    return _SOURCE_TYPE_LABELS.get(value, value)


def domain_of(url: str) -> str:
    try:
        host = urlparse(url).netloc.lower()
    except ValueError:
        return ""
    if host.startswith("www."):
        host = host[4:]
    return host


def is_blacklisted(url: str, blacklist: Iterable[str]) -> bool:
    host = domain_of(url)
    if not host:
        return False
    for bad in blacklist:
        bad = bad.lower().strip()
        if not bad:
            continue
        if host == bad or host.endswith("." + bad):
            return True
    return False


def normalize_url(url: str) -> str:
    """去重用：去掉尾部斜杠、fragment、常见追踪参数。"""
    url = unquote((url or "").strip())
    url = re.sub(r"#.*$", "", url)
    url = re.sub(r"([?&])(utm_[^&]+|ref=[^&]+|spm=[^&]+)", r"\1", url)
    url = re.sub(r"[?&]+$", "", url)
    url = url.replace("?&", "?")
    if url.endswith("/") and url.count("/") > 3:
        url = url[:-1]
    return url


@dataclass
class SourceItem:
    dimension: str
    url: str
    title: str = ""
    snippet: str = ""
    source_type: str = "unknown"
    note: str = ""
    content: str = ""
    fetched: bool = False
    fetch_error: str = ""
    dropped: str = ""  # 非空 = 被剔除的原因
    duplicate_of: str = ""  # 同一 URL 已在哪个维度出现

    @property
    def domain(self) -> str:
        return domain_of(self.url)

    @property
    def kept(self) -> bool:
        return not self.dropped and not self.duplicate_of

    def to_dict(self, max_chars: Optional[int] = None) -> dict:
        content = self.content
        if max_chars is not None and len(content) > max_chars:
            content = content[:max_chars]
        return {
            "dimension": self.dimension,
            "url": self.url,
            "title": self.title,
            "snippet": self.snippet,
            "source_type": self.source_type,
            "note": self.note,
            "domain": self.domain,
            "fetched": self.fetched,
            "fetch_error": self.fetch_error,
            "dropped": self.dropped,
            "duplicate_of": self.duplicate_of,
            "content": content,
            "word_count": len(self.content),
        }


@dataclass
class IngestSummary:
    target: str
    kind: str
    total_input: int = 0
    kept: int = 0
    dropped_blacklist: int = 0
    dropped_invalid: int = 0
    duplicates: int = 0
    fetched_ok: int = 0
    fetch_failed: int = 0
    by_source_type: Dict[str, int] = field(default_factory=dict)
    by_dimension: Dict[str, int] = field(default_factory=dict)
    empty_dimensions: List[str] = field(default_factory=list)
    unknown_dimensions: List[str] = field(default_factory=list)
    files_written: List[str] = field(default_factory=list)
    files_skipped: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    completed_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    @property
    def primary_ratio(self) -> float:
        if not self.kept:
            return 0.0
        return self.by_source_type.get("primary", 0) / self.kept

    @property
    def success(self) -> bool:
        return self.kept > 0

    def to_dict(self) -> dict:
        return {
            "target": self.target,
            "kind": self.kind,
            "success": self.success,
            "total_input": self.total_input,
            "kept": self.kept,
            "dropped_blacklist": self.dropped_blacklist,
            "dropped_invalid": self.dropped_invalid,
            "duplicates": self.duplicates,
            "fetched_ok": self.fetched_ok,
            "fetch_failed": self.fetch_failed,
            "primary_ratio": round(self.primary_ratio, 3),
            "by_source_type": self.by_source_type,
            "by_dimension": self.by_dimension,
            "empty_dimensions": self.empty_dimensions,
            "unknown_dimensions": self.unknown_dimensions,
            "files_written": self.files_written,
            "files_skipped": self.files_skipped,
            "warnings": self.warnings,
            "completed_at": self.completed_at,
        }


# ---------------------------------------------------------------------------
# 读 results.json
# ---------------------------------------------------------------------------


def load_results(path: Path) -> List[dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return coerce_results(data)


def coerce_results(data: Any) -> List[dict]:
    """接受几种宿主容易写出来的形状，统一成 [{dimension, url, ...}]。

    - [ {...}, {...} ]
    - {"results": [ ... ]}
    - {"dimensions": {"writings": [ ... ]}}
    - {"writings": [ ... ], "critics": [ ... ]}
    嵌在维度下的条目可以只是一个 URL 字符串。
    """
    if isinstance(data, list):
        return [_coerce_item(item, None) for item in data]
    if not isinstance(data, dict):
        raise ValueError("results.json 必须是数组或对象")

    if isinstance(data.get("results"), list):
        return [_coerce_item(item, None) for item in data["results"]]

    grouped = data.get("dimensions") if isinstance(data.get("dimensions"), dict) else None
    if grouped is None:
        candidates = {k: v for k, v in data.items() if isinstance(v, list)}
        if candidates:
            grouped = candidates
    if grouped is None:
        raise ValueError("results.json 里没有 results 数组，也没有按维度分组的数组")

    items: List[dict] = []
    for dimension, entries in grouped.items():
        for entry in entries:
            items.append(_coerce_item(entry, dimension))
    return items


def _coerce_item(entry: Any, dimension: Optional[str]) -> dict:
    if isinstance(entry, str):
        return {"dimension": dimension or "", "url": entry}
    if not isinstance(entry, dict):
        raise ValueError(f"无法识别的结果条目: {entry!r}")
    item = dict(entry)
    if dimension and not item.get("dimension"):
        item["dimension"] = dimension
    return item


def build_items(raw_items: Sequence[dict]) -> List[SourceItem]:
    items: List[SourceItem] = []
    for raw in raw_items:
        url = str(raw.get("url") or raw.get("link") or "").strip()
        item = SourceItem(
            dimension=str(raw.get("dimension") or "").strip(),
            url=url,
            title=str(raw.get("title") or "").strip(),
            snippet=str(raw.get("snippet") or raw.get("summary") or "").strip(),
            source_type=normalize_source_type(raw.get("source_type") or raw.get("type")),
            note=str(raw.get("note") or "").strip(),
            content=str(raw.get("content") or "").strip(),
        )
        if item.content:
            # 宿主自带的正文也要过有效性；无效的清掉，交给抓取器再试一次
            problem = content_validity(item.content)
            if problem:
                item.content = ""
                item.fetch_error = f"宿主提供的正文无效：{problem}"
            else:
                item.fetched = True
        items.append(item)
    return items


# ---------------------------------------------------------------------------
# 主流程
# ---------------------------------------------------------------------------


def ingest(
    plan: Plan,
    raw_items: Sequence[dict],
    output_dir: Path,
    fetch: bool = True,
    fetcher: Any = None,
    max_workers: int = 5,
    excerpt_chars: int = 1500,
    max_chars: int = 20000,
) -> IngestSummary:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    summary = IngestSummary(target=plan.target, kind=plan.kind)
    items = build_items(raw_items)
    summary.total_input = len(items)

    plan_dims = set(plan.dimensions)
    seen: Dict[str, str] = {}
    for item in items:
        if not item.url or not item.url.lower().startswith(("http://", "https://")):
            item.dropped = "无效 URL"
            summary.dropped_invalid += 1
            continue
        if not item.dimension:
            item.dropped = "缺 dimension"
            summary.dropped_invalid += 1
            continue
        if is_blacklisted(item.url, plan.blacklist):
            item.dropped = f"黑名单域名 {item.domain}"
            summary.dropped_blacklist += 1
            continue
        key = normalize_url(item.url)
        if key in seen:
            item.duplicate_of = seen[key]
            summary.duplicates += 1
            continue
        seen[key] = item.dimension
        if item.dimension not in plan_dims and item.dimension not in summary.unknown_dimensions:
            summary.unknown_dimensions.append(item.dimension)

    kept_items = [i for i in items if i.kept]
    summary.kept = len(kept_items)

    if fetch and kept_items:
        _fetch_all(kept_items, fetcher, max_workers)
    for item in kept_items:
        if item.fetched:
            summary.fetched_ok += 1
        elif fetch:
            summary.fetch_failed += 1

    for item in kept_items:
        summary.by_source_type[item.source_type] = summary.by_source_type.get(item.source_type, 0) + 1
        summary.by_dimension[item.dimension] = summary.by_dimension.get(item.dimension, 0) + 1
    summary.empty_dimensions = [d for d in plan.dimensions if summary.by_dimension.get(d, 0) == 0]

    if summary.unknown_dimensions:
        summary.warnings.append(
            "有维度不在 plan 里：" + "、".join(summary.unknown_dimensions) + "（已按 10-<维度>.md 落盘）"
        )
    if summary.kept and summary.by_source_type.get("unknown", 0) == summary.kept:
        summary.warnings.append("所有条目都没标 source_type，一手占比无法计算；请回填 primary / secondary / inferred")
    if summary.kept and summary.primary_ratio < 0.5:
        summary.warnings.append(
            f"一手占比 {summary.primary_ratio:.0%} < 50%，构建时要在诚实边界写明"
        )
    if summary.empty_dimensions:
        summary.warnings.append("空维度：" + "、".join(summary.empty_dimensions))

    summary.completed_at = datetime.now().isoformat(timespec="seconds")
    _write_dimension_files(plan, kept_items, output_dir, excerpt_chars, summary)
    _write_sources(plan, items, output_dir, summary)

    (output_dir / RESULT_FILENAME).write_text(
        json.dumps(
            {
                "target": plan.target,
                "kind": plan.kind,
                "plan_created_at": plan.created_at,
                "items": [i.to_dict(max_chars=max_chars) for i in items],
            },
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (output_dir / SUMMARY_FILENAME).write_text(
        json.dumps(summary.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return summary


def _fetch_all(items: List[SourceItem], fetcher: Any, max_workers: int) -> None:
    todo = [i for i in items if not i.fetched]
    if not todo:
        return
    if fetcher is None:
        from crawl.fetcher import ContentFetcher

        fetcher = ContentFetcher()

    def _one(item: SourceItem) -> None:
        try:
            result = fetcher.fetch(item.url)
        except Exception as exc:  # 抓取失败只记录，不中断
            item.fetch_error = str(exc)[:200]
            return
        content = result.content or ""
        problem = content_validity(content)
        if problem:
            item.content = ""
            item.fetched = False
            item.fetch_error = problem
        else:
            item.content = content
            item.fetched = True
            item.fetch_error = ""
        if not item.title and result.title:
            item.title = result.title

    with ThreadPoolExecutor(max_workers=max(1, max_workers)) as pool:
        futures = [pool.submit(_one, item) for item in todo]
        for future in as_completed(futures):
            future.result()


# ---------------------------------------------------------------------------
# 写文件
# ---------------------------------------------------------------------------


def _marker(plan: Plan) -> str:
    stamp = datetime.now().isoformat(timespec="seconds")
    return f"{INGEST_MARKER} target={plan.target} kind={plan.kind} at={stamp} -->"


def _safe_target(output_dir: Path, filename: str, summary: IngestSummary) -> Optional[Path]:
    """已有人工文件（没有 ingest 标记）时不覆盖，改写到 *.ingest.md。"""
    path = output_dir / filename
    if path.exists():
        head = path.read_text(encoding="utf-8", errors="replace")[:400]
        if INGEST_MARKER not in head:
            alt = path.with_name(path.stem + ".ingest.md")
            summary.files_skipped.append(filename)
            summary.warnings.append(f"{filename} 已有人工内容，未覆盖；底稿写到 {alt.name}")
            return alt
    return path


def _excerpt(text: str, limit: int, min_line: int = 30) -> str:
    """优先保留像句子的行（≥30 字），把信息框 / 菜单那种碎行挤出去。"""
    text = re.sub(r"[ \t\u3000]+", " ", text or "")
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    long_lines = [line for line in lines if len(line) >= min_line]
    if sum(len(line) for line in long_lines) >= min(limit, 300):
        lines = long_lines
    joined = "\n".join(lines)
    if len(joined) > limit:
        joined = joined[:limit].rstrip() + " …"
    return joined


def _quote(text: str) -> str:
    if not text:
        return ""
    return "\n".join(f"> {line}" if line.strip() else ">" for line in text.split("\n"))


def _cell(text: str, limit: int = 60) -> str:
    text = (text or "").replace("|", "\\|").replace("\n", " ").strip()
    if len(text) > limit:
        text = text[: limit - 1] + "…"
    return text


def _write_dimension_files(
    plan: Plan,
    items: List[SourceItem],
    output_dir: Path,
    excerpt_chars: int,
    summary: IngestSummary,
) -> None:
    dims_in_order = list(plan.dimensions) + [
        d for d in summary.unknown_dimensions if d not in plan.dimensions
    ]
    by_file: Dict[str, List[str]] = {}
    for dim in dims_in_order:
        by_file.setdefault(dimension_file(dim), []).append(dim)

    for filename, dims in by_file.items():
        sections: List[str] = [_marker(plan), "", f"# {filename[:2]} {' / '.join(dimension_label(d) for d in dims)} · 素材底稿", ""]
        sections.append(f"对象：{plan.target} · 类型：{plan.kind} · 由 `run.py ingest` 生成。摘录只到 {excerpt_chars} 字，全文在 `{RESULT_FILENAME}`。")
        sections.append("")
        total_here = 0
        for dim in dims:
            dim_items = [i for i in items if i.dimension == dim]
            total_here += len(dim_items)
            planned = plan.query_for(dim)
            query = planned.query if planned else "（plan 外维度）"
            primary = sum(1 for i in dim_items if i.source_type == "primary")
            sections.append(f"## 维度：{dim}（{dimension_label(dim)}）")
            sections.append("")
            sections.append(f"查询：`{query}` · 条数：{len(dim_items)} · 一手：{primary}")
            sections.append("")
            sections.append(f"要找什么：{dimension_hint(dim)}")
            sections.append("")
            if not dim_items:
                sections.append("**信息不足**：这一维 0 条。用宿主搜索补，或在诚实边界写明。")
                sections.append("")
                continue
            sections.append("| # | 来源 | 类型 | 域名 | 抓取 |")
            sections.append("|---|------|------|------|------|")
            for n, item in enumerate(dim_items, 1):
                status = "✓" if item.fetched else ("✗ " + _cell(item.fetch_error, 40) if item.fetch_error else "未抓")
                sections.append(
                    f"| {n} | [{_cell(item.title or item.url)}]({item.url}) | {source_type_label(item.source_type)} | {item.domain} | {status} |"
                )
            sections.append("")
            sections.append("### 摘录")
            sections.append("")
            for n, item in enumerate(dim_items, 1):
                sections.append(f"#### [{dim}-{n}] {item.title or item.url}")
                sections.append(f"- URL：{item.url}")
                sections.append(f"- 类型：{source_type_label(item.source_type)}")
                if item.snippet:
                    sections.append(f"- 摘要：{item.snippet}")
                if item.note:
                    sections.append(f"- 备注：{item.note}")
                if item.content:
                    sections.append("")
                    sections.append(_quote(_excerpt(item.content, excerpt_chars)))
                elif item.fetch_error:
                    sections.append(f"- 抓取失败：{item.fetch_error}（请用宿主的读网页工具补）")
                sections.append("")
        sections.append(EXTRACTION_STUB)
        target = _safe_target(output_dir, filename, summary)
        if target is None:
            continue
        target.write_text("\n".join(sections), encoding="utf-8")
        summary.files_written.append(target.name)


def _write_sources(plan: Plan, items: List[SourceItem], output_dir: Path, summary: IngestSummary) -> None:
    kept = [i for i in items if i.kept]
    lines: List[str] = [
        _marker(plan),
        "",
        f"# 00 来源清单：{plan.target}",
        "",
        f"类型：{plan.kind} · 查询语言：{plan.locale} · plan 生成于 {plan.created_at} · ingest 完成于 {summary.completed_at}",
        "",
        "## 统计",
        "",
        f"- 输入 {summary.total_input} 条 → 保留 {summary.kept} 条",
        f"- 一手 {summary.by_source_type.get('primary', 0)} · 二手 {summary.by_source_type.get('secondary', 0)} · 推断 {summary.by_source_type.get('inferred', 0)} · 未标 {summary.by_source_type.get('unknown', 0)} · 一手占比 {summary.primary_ratio:.0%}",
        f"- 剔除：黑名单 {summary.dropped_blacklist} · 无效 {summary.dropped_invalid} · 重复 {summary.duplicates}",
        f"- 抓取：成功 {summary.fetched_ok} · 失败 {summary.fetch_failed}",
        f"- 空维度：{'、'.join(summary.empty_dimensions) if summary.empty_dimensions else '无'}",
        "",
    ]
    if summary.warnings:
        lines.append("## 需要处理")
        lines.append("")
        for w in summary.warnings:
            lines.append(f"- {w}")
        lines.append("")

    lines.append("## 来源清单")
    lines.append("")
    if kept:
        lines.append("| 维度 | 来源 | 类型 | 域名 | 抓取 |")
        lines.append("|------|------|------|------|------|")
        for item in kept:
            status = "✓" if item.fetched else ("✗" if item.fetch_error else "未抓")
            lines.append(
                f"| {item.dimension} | [{_cell(item.title or item.url)}]({item.url}) | {source_type_label(item.source_type)} | {item.domain} | {status} |"
            )
    else:
        lines.append("**0 条可用素材。** 不要对着空气写分析。用宿主搜索补，或在诚实边界写明信息缺口。")
    lines.append("")

    dropped = [i for i in items if i.dropped]
    dups = [i for i in items if i.duplicate_of]
    if dropped or dups:
        lines.append("## 已剔除")
        lines.append("")
        for item in dropped:
            lines.append(f"- {item.dropped}：{item.url}")
        for item in dups:
            lines.append(f"- 重复（已在 {item.duplicate_of}）：{item.url}")
        lines.append("")

    failed = [i for i in kept if i.fetch_error]
    if failed:
        lines.append("## 抓取失败（请用宿主读网页工具补）")
        lines.append("")
        for item in failed:
            lines.append(f"- {item.url} — {item.fetch_error}")
        lines.append("")

    lines.append("## 采集日志")
    lines.append("")
    lines.append("| 维度 | 查询 | 条数 | 落盘 |")
    lines.append("|------|------|------|------|")
    for q in plan.queries:
        lines.append(f"| {q.dimension} | `{q.query}` | {summary.by_dimension.get(q.dimension, 0)} | `{q.file}` |")
    lines.append("")
    lines.append("搜索由宿主 Agent 完成；本脚本只做去重、黑名单、抓取、落盘。一手 / 二手标注来自宿主，脚本未复核。")
    lines.append("")

    target = _safe_target(output_dir, SOURCES_FILENAME, summary)
    if target is None:
        return
    target.write_text("\n".join(lines), encoding="utf-8")
    summary.files_written.append(target.name)
