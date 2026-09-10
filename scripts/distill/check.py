"""机器校验蒸馏产物。

只查能用代码判定的东西：命名、目录、YAML 头、4.5 层是否齐、模型数量与四件事、
边界 / 张力条数、证据三件套、examples、禁忌词、FIDELITY 分数与维度崩溃。
「像不像、诚不诚实」交给 skill-vetter 和独立评分 Agent，脚本不碰。

判定：FAIL = 不许进入下一 Phase；WARN = 要在诚实边界或 FIDELITY 写明；PASS = 过。
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from host_paths import SKILL_SLUG, product_skill_name

FAIL = "FAIL"
WARN = "WARN"
PASS = "PASS"

LAYER_PATTERNS = {
    "身份卡": r"身份卡",
    "心智模型": r"心智模型|核心机制",
    "表达 DNA": r"表达\s*DNA|表达指纹",
    "决策框架": r"决策框架",
    "诚实边界": r"诚实边界",
}
TENSION_PATTERN = r"张力"
MODEL_HEADING = re.compile(r"^###\s*模型\s*\d+", re.MULTILINE)
MODEL_PARTS = {
    "形成故事": (r"形成故事|这个论点从哪来|论点从哪来|起源", FAIL),
    "触发条件": (r"触发", FAIL),
    "推理步骤": (r"推理步骤|\*\*步骤\*\*|步骤[：:]", FAIL),
    "局限": (r"局限|失效|边界", WARN),
}
FORBIDDEN_WORDS = ("赋能", "抓手", "闭环", "对齐")
FORBIDDEN_CONTEXT_OK = ("禁忌", "禁止", "走歪", "不用", "为零", "反模式", "AI 味", "AI味", "不说", "不写", "禁用", "出现")
TRIGGER_MARKERS = ("「", "触发", "当用户", "时使用", "when ", "use when", "说「", "会怎么看", "蒸馏")
EVIDENCE_FILES = ("00-sources.md", "08-extraction-notes.md", "09-key-quotes.md")
MAX_SKILL_LINES = 500
MAX_REFERENCE_BYTES = 200_000
FIDELITY_THRESHOLD = 80
DIMENSION_COLLAPSE_RATIO = 0.4


@dataclass
class Finding:
    level: str
    code: str
    message: str

    def to_dict(self) -> dict:
        return {"level": self.level, "code": self.code, "message": self.message}


@dataclass
class CheckReport:
    skill_dir: str
    findings: List[Finding] = field(default_factory=list)
    kind: str = "generic"

    def add(self, level: str, code: str, message: str) -> None:
        self.findings.append(Finding(level, code, message))

    def fail(self, code: str, message: str) -> None:
        self.add(FAIL, code, message)

    def warn(self, code: str, message: str) -> None:
        self.add(WARN, code, message)

    def ok(self, code: str, message: str) -> None:
        self.add(PASS, code, message)

    @property
    def failures(self) -> List[Finding]:
        return [f for f in self.findings if f.level == FAIL]

    @property
    def warnings(self) -> List[Finding]:
        return [f for f in self.findings if f.level == WARN]

    @property
    def passed(self) -> bool:
        return not self.failures

    def to_dict(self) -> dict:
        return {
            "skill_dir": self.skill_dir,
            "kind": self.kind,
            "passed": self.passed,
            "fail_count": len(self.failures),
            "warn_count": len(self.warnings),
            "findings": [f.to_dict() for f in self.findings],
        }

    def to_text(self) -> str:
        lines = [f"check {self.skill_dir}（{self.kind}）", ""]
        for f in self.findings:
            lines.append(f"[{f.level}] {f.code}: {f.message}")
        lines.append("")
        verdict = "通过" if self.passed else "未通过"
        lines.append(f"结果：{verdict} · FAIL {len(self.failures)} · WARN {len(self.warnings)}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# 解析
# ---------------------------------------------------------------------------


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


def count_list_items(text: str) -> int:
    return len(re.findall(r"^\s*(?:[-*+]|\d+[.、)])\s+\S", text, re.MULTILINE))


def split_models(text: str) -> List[Tuple[str, str]]:
    matches = list(MODEL_HEADING.finditer(text))
    models: List[Tuple[str, str]] = []
    for i, m in enumerate(matches):
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        chunk = text[start:end]
        title = chunk.split("\n", 1)[0].lstrip("# ").strip()
        models.append((title, chunk))
    return models


def forbidden_hits(body: str) -> List[Tuple[int, str, str]]:
    hits: List[Tuple[int, str, str]] = []
    for lineno, line in enumerate(body.split("\n"), 1):
        if any(ok in line for ok in FORBIDDEN_CONTEXT_OK):
            continue
        present = [word for word in FORBIDDEN_WORDS if word in line]
        if len(present) >= 3:
            continue  # 一行列出三个以上，是在罗列禁忌词，不是在用
        for word in present:
            hits.append((lineno, word, line.strip()[:60]))
    return hits


def parse_fidelity(text: str) -> Tuple[Optional[int], List[Tuple[str, int, int]], bool]:
    """返回 (总分, [(维度, 得分, 满分)], 是否声明独立)。"""
    total = None
    m = re.search(r"总分[：:]\s*(\d{1,3})\s*/\s*100", text)
    if m:
        total = int(m.group(1))
    rows: List[Tuple[str, int, int]] = []
    for rm in re.finditer(r"^\|\s*([^|]+?)\s*\|\s*(\d{1,3})\s*/\s*(\d{1,3})\s*\|", text, re.MULTILINE):
        name = rm.group(1).strip()
        if name in ("维度", "---") or set(name) <= set("-: "):
            continue
        rows.append((name, int(rm.group(2)), int(rm.group(3))))
    declared_independent = "独立" in text and not re.search(r"未独立|同会话|同一会话|自评", text)
    return total, rows, declared_independent


# ---------------------------------------------------------------------------
# 检查项
# ---------------------------------------------------------------------------


def infer_kind(body: str, sections: List[Tuple[str, str]]) -> str:
    if find_section(sections, r"角色协议") or re.search(r"栽过的跟头", body):
        return "person"
    if find_section(sections, r"口头信念|实际选择"):
        return "self"
    return "generic"


def run_check(
    skill_dir: Path,
    require_fidelity: bool = False,
    quick: bool = False,
    kind: Optional[str] = None,
) -> CheckReport:
    skill_dir = Path(skill_dir).resolve()
    report = CheckReport(skill_dir=str(skill_dir))

    if not skill_dir.is_dir():
        report.fail("dir", f"目录不存在：{skill_dir}")
        return report

    _check_name(skill_dir, report)

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        report.fail("skill-md", "缺 SKILL.md")
        _check_files(skill_dir, report, require_fidelity)
        return report

    text = skill_md.read_text(encoding="utf-8", errors="replace")
    meta, body = parse_frontmatter(text)
    sections = split_sections(body)
    report.kind = kind or infer_kind(body, sections)

    _check_frontmatter(meta, skill_dir.name, report)
    _check_layers(sections, report)
    _check_models(body, sections, report, quick)
    _check_boundaries(sections, report)
    _check_tensions(sections, report)
    _check_style(body, text, report)
    _check_files(skill_dir, report, require_fidelity)
    _check_ingest_summary(skill_dir, report)
    return report


def _check_name(skill_dir: Path, report: CheckReport) -> None:
    name = skill_dir.name
    if name == SKILL_SLUG:
        report.fail("name", f"目录名 {name} 是母体保留名")
        return
    try:
        expected = product_skill_name(name)
    except ValueError as exc:
        report.fail("name", str(exc))
        return
    if expected != name:
        report.fail("name", f"目录名应为 {expected}，实际 {name}")
    else:
        report.ok("name", f"目录名 {name}")


def _check_frontmatter(meta: Dict[str, str], dirname: str, report: CheckReport) -> None:
    if not meta:
        report.fail("yaml", "SKILL.md 缺 YAML 头（--- name / description ---）")
        return
    name = meta.get("name", "")
    if not name:
        report.fail("yaml-name", "YAML 缺 name")
    elif name != dirname:
        report.fail("yaml-name", f"YAML name={name} 与目录名 {dirname} 不一致")
    else:
        report.ok("yaml-name", f"name={name}")
    desc = meta.get("description", "")
    if len(desc) < 15:
        report.fail("yaml-desc", "description 太短或缺失，必须说明何时触发")
    elif not any(marker in desc for marker in TRIGGER_MARKERS):
        report.warn("yaml-desc", "description 里看不到触发场景（「蒸馏XX」「XX 会怎么看」「当用户…时使用」）")
    else:
        report.ok("yaml-desc", "description 含触发场景")


def _check_layers(sections: List[Tuple[str, str]], report: CheckReport) -> None:
    missing = [layer for layer, pattern in LAYER_PATTERNS.items() if not find_section(sections, pattern)]
    if not missing:
        report.ok("layers", "4.5 层标题齐全")
        return
    for layer in missing:
        if layer == "表达 DNA" and report.kind != "person":
            report.warn("layers", "缺「表达 DNA」节（非人物类可接受，但要保留原作语气说明）")
        else:
            report.fail("layers", f"缺「{layer}」节")


def _check_models(body: str, sections: List[Tuple[str, str]], report: CheckReport, quick: bool) -> None:
    section = find_section(sections, LAYER_PATTERNS["心智模型"])
    scope = section[1] if section else body
    models = split_models(scope)
    if not models:
        models = split_models(body)
    n = len(models)
    low = 2 if quick else 3
    if n < low:
        report.fail("models-count", f"心智模型 {n} 个，至少 {low} 个（用 ### 模型 N 作标题）")
    elif n > 7:
        report.fail("models-count", f"心智模型 {n} 个，超过 7 个说明没提炼")
    elif n == 2:
        report.warn("models-count", "心智模型只有 2 个（快速版），诚实边界要加大")
    else:
        report.ok("models-count", f"心智模型 {n} 个")

    for title, chunk in models:
        for part, (pattern, level) in MODEL_PARTS.items():
            if not re.search(pattern, chunk):
                report.add(level, "model-parts", f"「{title}」缺{part}")
    if models and not report_has(report, "model-parts"):
        report.ok("model-parts", "每个模型都有形成故事 / 触发 / 步骤 / 局限")


def report_has(report: CheckReport, code: str) -> bool:
    return any(f.code == code and f.level != PASS for f in report.findings)


def _check_boundaries(sections: List[Tuple[str, str]], report: CheckReport) -> None:
    section = find_section(sections, LAYER_PATTERNS["诚实边界"])
    if not section:
        return
    _, text = section
    n = count_list_items(text)
    if n < 3:
        report.fail("boundaries", f"诚实边界只有 {n} 条，至少 3 条（做不到 / 信息缺口 / 何时不该用）")
    else:
        report.ok("boundaries", f"诚实边界 {n} 条")
    if report.kind == "person" and not re.search(r"不该用|不该来|不适用|谁不该|别来问|不要用我", text):
        report.warn("boundaries", "人物类诚实边界里没看到「什么情况下不该用我」")
    if not re.search(r"缺口|不足|没有|无", text):
        report.warn("boundaries", "诚实边界里没看到信息缺口")


def _check_tensions(sections: List[Tuple[str, str]], report: CheckReport) -> None:
    section = find_section(sections, TENSION_PATTERN)
    if not section:
        report.fail("tensions", "缺「内在张力」节（≥2 对，不调和）")
        return
    n = count_list_items(section[1])
    if n < 2:
        report.fail("tensions", f"内在张力只有 {n} 对，至少 2 对")
    else:
        report.ok("tensions", f"内在张力 {n} 对")


def _check_style(body: str, full_text: str, report: CheckReport) -> None:
    hits = forbidden_hits(full_text)
    if hits:
        sample = "；".join(f"L{ln}「{w}」" for ln, w, _ in hits[:5])
        report.warn("style", f"正文出现禁忌词 {len(hits)} 处：{sample}")
    else:
        report.ok("style", "无 赋能 / 抓手 / 闭环 / 对齐")
    lines = full_text.count("\n") + 1
    if lines > MAX_SKILL_LINES:
        report.warn("length", f"SKILL.md {lines} 行，超过约 {MAX_SKILL_LINES} 行；细节应进 references/")
    else:
        report.ok("length", f"SKILL.md {lines} 行")


def _check_files(skill_dir: Path, report: CheckReport, require_fidelity: bool) -> None:
    if not (skill_dir / "README.md").is_file():
        report.fail("readme", "缺 README.md")
    else:
        report.ok("readme", "README.md 存在")

    dist = skill_dir / "references" / "distillation"
    for name in EVIDENCE_FILES:
        path = dist / name
        if not path.is_file():
            report.fail("evidence", f"缺 references/distillation/{name}")
        elif len(path.read_text(encoding="utf-8", errors="replace").strip()) < 80:
            report.fail("evidence", f"references/distillation/{name} 内容太少")
    if not report_has(report, "evidence"):
        report.ok("evidence", "证据三件套齐全")

    examples = skill_dir / "examples"
    n_examples = len(list(examples.glob("*.md"))) if examples.is_dir() else 0
    if n_examples == 0:
        report.fail("examples", "examples/ 里没有输入 → 输出示例")
    else:
        report.ok("examples", f"examples/ {n_examples} 个")

    refs = skill_dir / "references"
    if refs.is_dir():
        big = [p for p in refs.rglob("*") if p.is_file() and p.stat().st_size > MAX_REFERENCE_BYTES and p.name != "ingest_result.json"]
        for p in big:
            report.warn("references-size", f"{p.relative_to(skill_dir)} 超过 {MAX_REFERENCE_BYTES // 1000}KB，疑似整书 / 整篇原文")
        if (dist / "ingest_result.json").is_file():
            report.warn("references-size", "references/distillation/ingest_result.json 是工作文件，交付前删除")

    fidelity = skill_dir / "FIDELITY.md"
    if not fidelity.is_file():
        if require_fidelity:
            report.fail("fidelity", "缺 FIDELITY.md（Phase 3 出厂必须）")
        else:
            report.warn("fidelity", "FIDELITY.md 尚未生成（Phase 3 前正常）")
        return
    total, rows, independent = parse_fidelity(fidelity.read_text(encoding="utf-8", errors="replace"))
    if total is None:
        report.fail("fidelity", "FIDELITY.md 里解析不到「总分：NN/100」")
    elif total < FIDELITY_THRESHOLD:
        report.fail("fidelity", f"保真度 {total} < {FIDELITY_THRESHOLD}，不得宣称完成")
    else:
        report.ok("fidelity", f"保真度 {total}/100")
    for name, score, full in rows:
        if full and score < full * DIMENSION_COLLAPSE_RATIO:
            report.fail("fidelity-dimension", f"「{name}」{score}/{full} 低于 40%，该维崩溃")
    if not rows:
        report.warn("fidelity", "FIDELITY.md 里没有七维分数表")
    if not independent:
        report.warn("fidelity-independent", "FIDELITY.md 未声明独立评分（或写了未独立 / 同会话），不得自称出厂合格")


def _check_ingest_summary(skill_dir: Path, report: CheckReport) -> None:
    path = skill_dir / "references" / "distillation" / "ingest_summary.json"
    if not path.is_file():
        return
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        report.warn("ingest", "ingest_summary.json 无法解析")
        return
    kept = int(data.get("kept", 0))
    if kept == 0:
        report.warn("ingest", "ingest 保留 0 条，00-sources.md 必须写明脚本层为空")
        return
    ratio = float(data.get("primary_ratio", 0))
    if ratio < 0.5:
        report.warn("ingest", f"一手占比 {ratio:.0%} < 50%，诚实边界要写明")
    else:
        report.ok("ingest", f"ingest 保留 {kept} 条，一手占比 {ratio:.0%}")
    empty = data.get("empty_dimensions") or []
    if empty:
        report.warn("ingest", "空维度：" + "、".join(empty))
