"""保真度测试包：出题 / 答题 / 评分三方分离的文件协议。

流程：
  init  → 出模板：fidelity/questions.md、rubric.md、answers.md
  出题 Agent 填 questions.md（题）+ rubric.md（参考立场，答题不得看）
  答题 Agent 只看 questions.md + Skill 目录，填 answers.md
  blind → 把 answers.md 里的对象名遮掉，生成 answers.blind.md 给评分 Agent 盲读风格
  评分 Agent 看 answers.blind.md → answers.md → rubric.md → Skill，写 FIDELITY.md
  check --require-fidelity → 核对测试包完整、题目没抄正文、rubric 没泄漏、分数加得上

脚本不出题、不答题、不打分。它只保证三方拿到的文件分开、留痕，并让分数能被核对。
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

from distill.markdown import parse_frontmatter, split_sections

PACKET_DIR = "fidelity"
QUESTIONS_FILE = "questions.md"
RUBRIC_FILE = "rubric.md"
ANSWERS_FILE = "answers.md"
BLIND_FILE = "answers.blind.md"
SCORECARD_FILE = "FIDELITY.md"

SCORECARD: Dict[str, int] = {
    "立场一致性": 20,
    "风格辨识度": 15,
    "边缘诚实度": 15,
    "来源透明度": 10,
    "结构完整度": 10,
    "可执行性": 15,
    "可迁移性": 15,
}
THRESHOLD = 80
COLLAPSE_RATIO = 0.4
GRADES: Sequence[Tuple[int, str]] = ((85, "A"), (80, "B"), (55, "C"), (0, "D"))

QUESTION_SLOTS: Sequence[Tuple[str, str]] = (
    ("Q1", "立场"),
    ("Q2", "立场"),
    ("Q3", "立场"),
    ("Q4", "超范围"),
    ("Q5", "真实任务"),
)
QUESTION_IDS = tuple(q for q, _ in QUESTION_SLOTS)

TODO_MARK = "TODO"
MASK = "〔X〕"
NGRAM = 8
QUESTION_OVERLAP_FAIL = 0.3  # 题目 8-gram 有三成出现在正文 / examples 里，就是抄题
RUBRIC_LEAK_MIN_CHARS = 12
RUBRIC_LEAK_RATIO = 0.5
MIN_ANSWER_CHARS = 40
MIN_QUESTION_CHARS = 10

QUESTION_HEADING = re.compile(r"^##\s*(Q\d)\b(.*)$", re.MULTILINE)
# 「三个不同会话」含子串「同会话」，用 lookbehind 排掉「不同会话」。
DEPENDENT_PATTERN = re.compile(r"未独立|(?<!不)同会话|同一会话|同一个会话|自评|同一\s*个?\s*Agent", re.IGNORECASE)
NETWORK_NONE = ("none", "no", "off", "否", "无", "未联网", "禁止", "false", "0")

# ---------------------------------------------------------------------------
# 模板
# ---------------------------------------------------------------------------

QUESTIONS_TEMPLATE = """---
target: {target}
aliases: {aliases}
kind: {kind}
author: TODO（出题 Agent：模型 / 会话）
date: {date}
---
# 保真度测试题 · {target}

答题 Agent 只能看这份文件和 Skill 目录。禁止联网，禁止看 `rubric.md`。

出题规则：
- Q1–Q3 立场题：对象**公开表态过**、且 Skill 正文与 `examples/` **没写过**的问题。写场景，不提示答案。
- Q4 超范围题：落在 Skill 覆盖不到的领域，看会不会编数字、编条款、装本人。
- Q5 真实任务题：一件具体的事，要求做完，不只表态。
- 头部 `aliases` 是盲读遮名词表：除别名外，把公司 / 产品 / 招牌场合名也写进去（如 小米, MIUI, 站长大会），否则评分 Agent 靠实体名就能认出，风格辨识度测不到。

## Q1 · 立场

TODO

## Q2 · 立场

TODO

## Q3 · 立场

TODO

## Q4 · 超范围

TODO

## Q5 · 真实任务

TODO
"""

RUBRIC_TEMPLATE = """---
target: {target}
author: TODO（出题 Agent：模型 / 会话）
date: {date}
---
# 评分依据 · {target}

只给评分 Agent。答题 Agent 不得看到这份文件；写完题就把它关掉。

## Q1
- 公开立场：TODO
- 出处：TODO（URL 或 `references/distillation/09-key-quotes.md` 条目）
- 一致的标志：TODO
- 走偏的标志：TODO

## Q2
- 公开立场：TODO
- 出处：TODO
- 一致的标志：TODO
- 走偏的标志：TODO

## Q3
- 公开立场：TODO
- 出处：TODO
- 一致的标志：TODO
- 走偏的标志：TODO

## Q4
- 期望：标「框架推断」或拒绝；不给对象从未表态的具体数字 / 条款 / 方案
- 诚实的标志：TODO
- 编造的标志：TODO

## Q5
- 「做完」的标准：TODO
- 必须出现的步骤 / 默认动作：TODO
- 只喊口号的标志：TODO
"""

ANSWERS_TEMPLATE = """---
answerer: TODO（答题 Agent：模型 / 会话）
inputs: fidelity/questions.md + Skill 目录
network: none
date: {date}
---
# 答题 · {target}

激活 Skill 后按它作答。Skill 覆盖不到的地方，先写「这是框架推断」再答。不看 `rubric.md`，不联网。
每题写完整回答，不写摘要；评分 Agent 要盲读风格。

## Q1

TODO

## Q2

TODO

## Q3

TODO

## Q4

TODO

## Q5

TODO
"""

SCORECARD_TEMPLATE = """# 保真度评分卡 · {target}

**总分：NN/100 · 等级 X** | 日期：{date}
出题：<模型 / 会话> | 答题：<模型 / 会话> | 评分：<模型 / 会话> | 独立性：独立（答题与评分是两个会话）
测试包：`fidelity/questions.md` · `fidelity/answers.md` · `fidelity/answers.blind.md` · `fidelity/rubric.md`

| 维度 | 得分 | 判定 |
|------|------|------|
| 立场一致性 | NN/20 | Q1–Q3 |
| 风格辨识度 | NN/15 | 盲读 answers.blind.md：像谁、凭什么认出 |
| 边缘诚实度 | NN/15 | Q4 |
| 来源透明度 | NN/10 | 看 Skill：00-sources、一手占比、引语出处 |
| 结构完整度 | NN/10 | 看 Skill：4.5 层、模型数、边界、张力 |
| 可执行性 | NN/15 | Q5 + 模型触发 / 步骤 |
| 可迁移性 | NN/15 | Q5 |

出厂线：通过 / 不通过。崩溃维：无 / 有。

## 测试记录

| 题 | 类型 | 参考立场（rubric） | 答题摘要 | 判定 |
|----|------|--------------------|----------|------|
| Q1 | 立场 | | | 一致 / 偏离 |
| Q2 | 立场 | | | |
| Q3 | 立场 | | | |
| Q4 | 超范围 | | | 诚实 / 编造 |
| Q5 | 真实任务 | | | 能做完 / 只有口号 |

## 盲读记录

像谁，把握多大：
- (a) 未遮实体（约 NN%）：
- (b) 年份典故（约 NN%）：
- (c) 句法与判断习惯（约 NN%）：
只看 (c) 能收敛到：

## 必须改

（3–5 条，或写「无」）
"""

ROLE_PROMPTS = """三个角色，三个会话（没有子 Agent 就同会话分角色，并在 FIDELITY.md 独立性一栏写「同会话分角色（未独立）」）：

【出题 Agent】读 Skill 目录 + 公开资料，填 {questions} 和 {rubric}。
  立场题必须是对象公开表态过、Skill 正文与 examples/ 没写过的；写完把 rubric 关掉。

【答题 Agent】新会话。只给它 {questions} 和 Skill 目录的路径。禁止联网，禁止看 rubric。
  按 Skill 作答，填 {answers}；头部 answerer / network 要填。

【脚本】python3 run.py fidelity blind "{skill_dir}"   → 生成 {blind}

【评分 Agent】新会话。顺序：先只读 {blind} 写盲读记录 → 再读 {answers} → 再读 {rubric} → 最后读 Skill。
  盲读记录：像谁、把握多大；线索分三类各给比例——(a) 未遮实体（公司 / 产品 / 社群 / 场合名）、
  (b) 年份典故、(c) 句法与判断习惯；最后写只看 (c) 能收敛到什么程度。风格辨识度按这条打：
  主要靠 (a) 认出要扣分，靠 (b)(c) 给高分。(a) 多就把名字补进 aliases 重跑 blind；(b) 是本人风格，不遮。
  目录名会泄露对象：把 {blind} 复制到不含对象名的临时目录先读，写完盲读记录再告知 Skill 目录；
  旧 {scorecard} 先移走，README.md 不给读。
  按 references/fidelity-scorecard.md 七维打分，写 {scorecard}（测试记录逐题写 Q1–Q5）。

【脚本】python3 run.py check "{skill_dir}" --require-fidelity
"""


# ---------------------------------------------------------------------------
# 数据
# ---------------------------------------------------------------------------


@dataclass
class Question:
    qid: str
    kind: str
    body: str

    @property
    def filled(self) -> bool:
        return TODO_MARK not in self.body and len(normalize(self.body)) >= MIN_QUESTION_CHARS


@dataclass
class Questions:
    meta: Dict[str, str]
    items: Dict[str, Question]

    @property
    def target(self) -> str:
        return self.meta.get("target", "")

    @property
    def aliases(self) -> List[str]:
        return split_aliases(self.meta.get("aliases", ""))


@dataclass
class Answers:
    meta: Dict[str, str]
    items: Dict[str, str]

    @property
    def network_declared_off(self) -> bool:
        value = self.meta.get("network", "").strip().lower()
        return bool(value) and any(value.startswith(tok) for tok in NETWORK_NONE)

    @property
    def answerer(self) -> str:
        return self.meta.get("answerer", "").strip()


@dataclass
class Scorecard:
    total: Optional[int]
    grade: Optional[str]
    rows: List[Tuple[str, int, int]]
    independence: Optional[str]  # 「独立性：」字段原文；None = 没写字段
    declared_independent: bool
    question_refs: Set[str] = field(default_factory=set)
    roles: Dict[str, str] = field(default_factory=dict)  # 出题 / 答题 / 评分

    @property
    def row_sum(self) -> int:
        return sum(score for name, score, _ in self.rows if name in SCORECARD)

    @property
    def dimension_names(self) -> Set[str]:
        return {name for name, _, _ in self.rows}


@dataclass
class Finding:
    level: str  # FAIL / WARN / PASS
    code: str
    message: str


# ---------------------------------------------------------------------------
# 文本工具
# ---------------------------------------------------------------------------

_PUNCT = re.compile(r"[\s\W_]+", re.UNICODE)


def normalize(text: str) -> str:
    """去空白与标点，小写。只留汉字 / 字母 / 数字，给 n-gram 比对用。"""
    return _PUNCT.sub("", text).lower()


def ngrams(text: str, n: int = NGRAM) -> Set[str]:
    norm = normalize(text)
    if len(norm) < n:
        return {norm} if norm else set()
    return {norm[i : i + n] for i in range(len(norm) - n + 1)}


def overlap_ratio(needle: str, haystack_grams: Set[str], n: int = NGRAM) -> float:
    grams = ngrams(needle, n)
    if not grams:
        return 0.0
    return len(grams & haystack_grams) / len(grams)


def split_aliases(raw: str) -> List[str]:
    parts = re.split(r"[,，;；、|]", raw or "")
    return [p.strip().strip("[]\"'") for p in parts if p.strip().strip("[]\"'")]


def grade_for(total: int) -> str:
    for floor, grade in GRADES:
        if total >= floor:
            return grade
    return "D"


def today() -> str:
    return date.today().isoformat()


# ---------------------------------------------------------------------------
# 解析
# ---------------------------------------------------------------------------


def _split_by_question(body: str) -> Dict[str, Tuple[str, str]]:
    """按 `## Qn` 切段，返回 {qid: (标题剩余部分, 正文)}。"""
    matches = list(QUESTION_HEADING.finditer(body))
    out: Dict[str, Tuple[str, str]] = {}
    for i, m in enumerate(matches):
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        out[m.group(1).upper()] = (m.group(2).strip(), body[start:end].strip())
    return out


def parse_questions(text: str) -> Questions:
    meta, body = parse_frontmatter(text)
    items: Dict[str, Question] = {}
    expected_kind = dict(QUESTION_SLOTS)
    for qid, (rest, content) in _split_by_question(body).items():
        kind = ""
        for candidate in ("立场", "超范围", "真实任务", "任务"):
            if candidate in rest:
                kind = "真实任务" if candidate == "任务" else candidate
                break
        items[qid] = Question(qid=qid, kind=kind or expected_kind.get(qid, ""), body=content)
    return Questions(meta=meta, items=items)


def parse_answers(text: str) -> Answers:
    meta, body = parse_frontmatter(text)
    items = {qid: content for qid, (_, content) in _split_by_question(body).items()}
    return Answers(meta=meta, items=items)


_ROW = re.compile(r"^\|\s*([^|]+?)\s*\|\s*(\d{1,3})\s*/\s*(\d{1,3})\s*\|", re.MULTILINE)


def parse_scorecard(text: str) -> Scorecard:
    total = None
    m = re.search(r"总分[：:]\s*(\d{1,3})\s*/\s*100", text)
    if m:
        total = int(m.group(1))
    grade = None
    g = re.search(r"等级\s*([ABCD])\b", text)
    if g:
        grade = g.group(1)

    rows: List[Tuple[str, int, int]] = []
    for rm in _ROW.finditer(text):
        name = rm.group(1).strip().replace(" ", "")
        if name in ("维度", "---") or set(name) <= set("-: "):
            continue
        rows.append((name, int(rm.group(2)), int(rm.group(3))))

    independence = None
    im = re.search(r"独立性[：:]\s*([^|\n]+)", text)
    if im:
        independence = im.group(1).strip()
    if independence is not None:
        declared = "独立" in independence and not DEPENDENT_PATTERN.search(independence)
    else:
        declared = "独立" in text and not DEPENDENT_PATTERN.search(text)

    roles: Dict[str, str] = {}
    for role in ("出题", "答题", "评分"):
        rm2 = re.search(rf"(?<![/／]){role}[：:]\s*([^|\n]+)", text)
        if rm2:
            roles[role] = rm2.group(1).strip()

    refs = {q for q in QUESTION_IDS if re.search(rf"\b{q}\b", text)}
    return Scorecard(
        total=total,
        grade=grade,
        rows=rows,
        independence=independence,
        declared_independent=declared,
        question_refs=refs,
        roles=roles,
    )


# ---------------------------------------------------------------------------
# init / blind
# ---------------------------------------------------------------------------


def packet_dir(skill_dir: Path) -> Path:
    return Path(skill_dir) / PACKET_DIR


def init_packet(
    skill_dir: Path,
    target: str,
    aliases: Iterable[str] = (),
    kind: str = "person",
    force: bool = False,
) -> Tuple[List[Path], List[Path]]:
    """写三份模板。已存在的文件不动（除非 force）。返回 (写了, 跳过)。"""
    pdir = packet_dir(skill_dir)
    pdir.mkdir(parents=True, exist_ok=True)
    alias_text = ", ".join(a for a in aliases if a) or ""
    fills = {"target": target, "aliases": alias_text, "kind": kind, "date": today()}
    written: List[Path] = []
    skipped: List[Path] = []
    for name, template in (
        (QUESTIONS_FILE, QUESTIONS_TEMPLATE),
        (RUBRIC_FILE, RUBRIC_TEMPLATE),
        (ANSWERS_FILE, ANSWERS_TEMPLATE),
    ):
        path = pdir / name
        if path.exists() and not force:
            skipped.append(path)
            continue
        path.write_text(template.format(**fills), encoding="utf-8")
        written.append(path)
    return written, skipped


def role_prompts(skill_dir: Path) -> str:
    pdir = f"{PACKET_DIR}/"
    return ROLE_PROMPTS.format(
        skill_dir=skill_dir,
        questions=pdir + QUESTIONS_FILE,
        rubric=pdir + RUBRIC_FILE,
        answers=pdir + ANSWERS_FILE,
        blind=pdir + BLIND_FILE,
        scorecard=SCORECARD_FILE,
    )


def _slug_words(skill_dir: Path) -> List[str]:
    name = Path(skill_dir).name
    if name.startswith("pangu-"):
        name = name[len("pangu-") :]
    words = [name] + [w for w in name.split("-") if len(w) >= 4]
    return [w for w in words if w and w != "distill"]


# 别名扩展：出题者写「阿里巴巴」「查理·芒格」「Charlie Munger」，答题里出现的往往是
# 「阿里」「查理芒格」「芒格」「Munger」。脚本补这些变体，免得盲读第二段就被实体名点破。
_CJK_RE = re.compile(r"^[\u4e00-\u9fff]+$")
_LATIN_WORD_RE = re.compile(r"^[A-Za-z][A-Za-z'\-]*$")
_NAME_SEPARATORS = "·•・.．・‧ "
_ORG_SUFFIXES = ("股份有限公司", "有限公司", "控股", "集团", "公司", "基金", "年会", "股东会", "股东大会")
# 中文四字以上名字的前两字常是简称（阿里巴巴→阿里、西科金融→西科、南加州大学→南加），
# 但这些前两字是普通词，遮了会把正文打烂，不自动加；要遮请在 aliases 里明写。
GENERIC_SHORT = frozenset(
    "每日 第一 第二 中国 美国 日本 英国 德国 公司 集团 大学 学院 国际 全球 世界 时代 未来 科技 "
    "通用 长期 短期 资本 管理 投资 银行 金融 教育 新闻 日报 人民 东方 西方 北京 上海 深圳 香港 "
    "台湾 南方 北方 中央 国家 政府 市场 经济 社会 文化 历史 现代 传统 互联 网络 在线 数字 智能 "
    "价值 成长 创新 创业 产品 用户 微信 苹果".split()
)
SHORT_LEN = 2
SHORT_MIN_FULL_LEN = 4


def _strip_org_suffix(name: str) -> str:
    for suf in sorted(_ORG_SUFFIXES, key=len, reverse=True):
        if name.endswith(suf) and len(name) - len(suf) >= 2:
            return name[: -len(suf)]
    return name


def expand_aliases(names: Iterable[str], body: str = "") -> Tuple[List[str], List[str]]:
    """返回 (全部名字含变体, 自动补出来的变体)。

    规则（全部是机器能判的）：
    - 去掉《》「」“” 等书名 / 引号
    - 中间带 · • 空格 的名字：去掉分隔符的整体、以及各段（段长 ≥2）
    - 机构后缀：阿里巴巴集团 → 阿里巴巴
    - 拉丁多词名：最后一个词（≥5 字母，首字母大写）——Charlie Munger → Munger
    - 中文 ≥4 字的名字：前两字作简称候选，条件是它在正文里独立出现过（不只作为全名的一部分），
      且不在 GENERIC_SHORT 里
    """
    base: List[str] = []
    for n in names:
        n = (n or "").strip().strip("《》「」『』“”\"'[]")
        if n:
            base.append(n)
    auto: List[str] = []
    seen = set(base)

    def add(v: str) -> None:
        v = v.strip()
        if len(v) >= 2 and v not in seen:
            seen.add(v)
            auto.append(v)

    for n in list(base):
        core = _strip_org_suffix(n)
        if core != n:
            add(core)
        for cand in (n, core):
            parts = [p for p in re.split("[%s]+" % re.escape(_NAME_SEPARATORS), cand) if p]
            if len(parts) >= 2:
                joined = "".join(parts)
                if all(_CJK_RE.match(p) for p in parts):
                    add(joined)
                    for p in parts:
                        if len(p) >= 2:
                            add(p)
                elif all(_LATIN_WORD_RE.match(p) for p in parts):
                    last = parts[-1]
                    if len(last) >= 5 and last[0].isupper():
                        add(last)

    if body:
        for n in list(seen):
            if _CJK_RE.match(n) and len(n) >= SHORT_MIN_FULL_LEN:
                short = n[:SHORT_LEN]
                if short in GENERIC_SHORT or short in seen:
                    continue
                # 独立出现：正文里有不属于任何已知全名的 short
                standalone = body
                for full in sorted(seen, key=len, reverse=True):
                    if full != short and short in full:
                        standalone = standalone.replace(full, "")
                if short in standalone:
                    add(short)

    return base + auto, auto


_LATIN_STOP = frozenset(
    "the a an and or but of to in on at for with by from as is are was were be been it its this that "
    "these those i you he she we they my your our their q1 q2 q3 q4 q5 ceo cfo cto coo ai ipo pe eps "
    "roe roic gdp usd rmb ok no yes skill app pro day kpi okr sku roi faq api pdf url".split()
)
_LATIN_TOKEN_RE = re.compile(r"(?<![A-Za-z])[A-Z][A-Za-z]{2,}(?![A-Za-z])")


def suspect_entities(masked_body: str, limit: int = 15) -> List[str]:
    """遮完之后还留在正文里、首字母大写的拉丁词（公司、媒体、人名多半长这样）。

    只报不遮——是不是要遮由出题者判断，然后写进 aliases 或 --alias。
    中文实体没有大小写可依，脚本不猜；出题时把公司 / 场合的中文名写进 aliases。
    """
    counts: Dict[str, int] = {}
    for m in _LATIN_TOKEN_RE.finditer(masked_body):
        tok = m.group(0)
        if tok.lower() in _LATIN_STOP:
            continue
        counts[tok] = counts.get(tok, 0) + 1
    ranked = sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return [tok for tok, _ in ranked[:limit]]


def _name_pattern(name: str) -> "re.Pattern[str]":
    if _LATIN_WORD_RE.match(name):
        # 拉丁词加边界，允许所有格 / 复数：Munger、Munger's、Mungers 都遮，dailymotion 不遮 Daily
        return re.compile(r"(?<![A-Za-z])%s(?:'s|s)?(?![A-Za-z])" % re.escape(name), re.IGNORECASE)
    return re.compile(re.escape(name), re.IGNORECASE)


def mask_names(text: str, names: Iterable[str]) -> Tuple[str, int]:
    """把对象名及别名全部替换成 MASK。长名先替，避免短名先吃掉一半。"""
    count = 0
    ordered = sorted({n.strip() for n in names if n and n.strip()}, key=len, reverse=True)
    for name in ordered:
        text, n = _name_pattern(name).subn(MASK, text)
        count += n
    return text, count


def blind_answers(
    skill_dir: Path,
    extra_aliases: Iterable[str] = (),
    expand: bool = True,
    report: Optional[Dict[str, List[str]]] = None,
) -> Tuple[Path, int, List[str]]:
    """生成 answers.blind.md。返回 (路径, 遮掉几处, 用了哪些名字)。

    expand=True 时按 expand_aliases 补简称 / 变体；头部 `auto_aliases` 只记数量（名字写进去会泄给评分 Agent），
    传 report={} 可拿到 report["auto"] 与 report["suspects"]。
    """
    pdir = packet_dir(skill_dir)
    answers_path = pdir / ANSWERS_FILE
    if not answers_path.is_file():
        raise FileNotFoundError(f"缺 {answers_path}，答题 Agent 还没写")
    names: List[str] = list(extra_aliases)
    questions_path = pdir / QUESTIONS_FILE
    if questions_path.is_file():
        q = parse_questions(questions_path.read_text(encoding="utf-8", errors="replace"))
        if q.target:
            names.append(q.target)
        names.extend(q.aliases)
    names.extend(_slug_words(skill_dir))
    skill_md = Path(skill_dir) / "SKILL.md"
    if skill_md.is_file():
        meta, body = parse_frontmatter(skill_md.read_text(encoding="utf-8", errors="replace"))
        h1 = re.search(r"^#\s+(.+?)\s*$", body, re.MULTILINE)
        if h1:
            # 「雷军 · 思维操作系统」→ 只取名字那一段
            first = re.split(r"[·:：—\-|]", h1.group(1))[0].strip()
            if 1 < len(first) <= 20:
                names.append(first)

    raw = answers_path.read_text(encoding="utf-8", errors="replace")
    meta, body = parse_frontmatter(raw)
    auto: List[str] = []
    if expand:
        names, auto = expand_aliases(names, body)
    masked_body, count = mask_names(body, names)
    if report is not None:
        report["auto"] = list(auto)
        report["suspects"] = suspect_entities(masked_body)
    # 头部只写数量，不写名字：评分 Agent 先读这份，名字写进来就泄了
    header = (
        "---\n"
        f"blind_of: {ANSWERS_FILE}\n"
        f"masked: {count}\n"
        f"auto_aliases: {len(auto)}\n"
        f"answerer: {meta.get('answerer', '')}\n"
        f"date: {today()}\n"
        "---\n"
        f"# 盲读稿（对象名已替换为 {MASK}）\n\n"
        "评分 Agent 先读这份，写下「像谁、把握多大」，线索分三类各给比例：(a) 未遮实体 / (b) 年份典故 / (c) 句法与判断习惯，"
        "再写只看 (c) 能收敛到什么程度；然后才打开 answers.md 和 Skill。\n"
    )
    out = pdir / BLIND_FILE
    out.write_text(header + masked_body.lstrip("\n"), encoding="utf-8")
    used = sorted({n for n in names if n}, key=len, reverse=True)
    return out, count, used


# ---------------------------------------------------------------------------
# 核对
# ---------------------------------------------------------------------------


def _skill_corpus_grams(skill_dir: Path) -> Set[str]:
    grams: Set[str] = set()
    skill_md = Path(skill_dir) / "SKILL.md"
    if skill_md.is_file():
        grams |= ngrams(skill_md.read_text(encoding="utf-8", errors="replace"))
    examples = Path(skill_dir) / "examples"
    if examples.is_dir():
        for p in examples.glob("*.md"):
            grams |= ngrams(p.read_text(encoding="utf-8", errors="replace"))
    return grams


def _template_lines() -> Set[str]:
    lines: Set[str] = set()
    for tpl in (QUESTIONS_TEMPLATE, RUBRIC_TEMPLATE, ANSWERS_TEMPLATE):
        for line in tpl.split("\n"):
            norm = normalize(line)
            if norm:
                lines.add(norm)
    return lines


def inspect_packet(skill_dir: Path) -> List[Finding]:
    """核对 fidelity/ 测试包。FAIL 在 --require-fidelity 下阻断，否则由调用方降为 WARN。"""
    skill_dir = Path(skill_dir)
    pdir = packet_dir(skill_dir)
    out: List[Finding] = []

    if not pdir.is_dir():
        out.append(Finding("FAIL", "fidelity-packet", f"缺 {PACKET_DIR}/ 测试包：先跑 run.py fidelity init"))
        return out

    q_path = pdir / QUESTIONS_FILE
    a_path = pdir / ANSWERS_FILE
    r_path = pdir / RUBRIC_FILE
    b_path = pdir / BLIND_FILE

    questions: Optional[Questions] = None
    if not q_path.is_file():
        out.append(Finding("FAIL", "fidelity-questions", f"缺 {PACKET_DIR}/{QUESTIONS_FILE}"))
    else:
        questions = parse_questions(q_path.read_text(encoding="utf-8", errors="replace"))
        corpus = _skill_corpus_grams(skill_dir)
        missing = [q for q in QUESTION_IDS if q not in questions.items]
        if missing:
            out.append(Finding("FAIL", "fidelity-questions", "题目缺 " + "、".join(missing)))
        unfilled = [q for q, item in questions.items.items() if not item.filled]
        if unfilled:
            out.append(Finding("FAIL", "fidelity-questions", "题目还是 TODO / 太短：" + "、".join(unfilled)))
        expected = dict(QUESTION_SLOTS)
        for qid, item in questions.items.items():
            want = expected.get(qid)
            if want and item.kind and item.kind != want:
                out.append(Finding("WARN", "fidelity-questions", f"{qid} 标成「{item.kind}」，协议要求「{want}」"))
            if item.filled and corpus:
                ratio = overlap_ratio(item.body, corpus)
                if ratio >= QUESTION_OVERLAP_FAIL:
                    out.append(
                        Finding("FAIL", "fidelity-questions", f"{qid} 与 SKILL.md / examples 重合 {ratio:.0%}，题目抄了正文")
                    )
        if TODO_MARK in questions.meta.get("author", ""):
            out.append(Finding("WARN", "fidelity-questions", "questions.md 没写出题 Agent（author）"))
        if not out or all(f.code != "fidelity-questions" or f.level != "FAIL" for f in out):
            out.append(Finding("PASS", "fidelity-questions", f"题目 {len(questions.items)} 道，未抄正文"))

    template_norms = _template_lines()
    rubric_lines: List[str] = []
    if not r_path.is_file():
        out.append(Finding("WARN", "fidelity-rubric", f"缺 {PACKET_DIR}/{RUBRIC_FILE}，评分没有事先写下的参考立场"))
    else:
        rubric_text = r_path.read_text(encoding="utf-8", errors="replace")
        _, rubric_body = parse_frontmatter(rubric_text)
        todo_count = rubric_body.count(TODO_MARK)
        if todo_count:
            out.append(Finding("FAIL", "fidelity-rubric", f"rubric.md 还有 {todo_count} 处 TODO，参考立场没写完"))
        for line in rubric_body.split("\n"):
            content = re.sub(r"^\s*[-*]\s*", "", line)
            content = re.sub(r"^[^：:]{1,12}[：:]", "", content).strip()
            norm = normalize(content)
            if len(norm) >= RUBRIC_LEAK_MIN_CHARS and norm not in template_norms:
                rubric_lines.append(content)

    answers: Optional[Answers] = None
    if not a_path.is_file():
        out.append(Finding("FAIL", "fidelity-answers", f"缺 {PACKET_DIR}/{ANSWERS_FILE}，答题 Agent 还没答"))
    else:
        answers = parse_answers(a_path.read_text(encoding="utf-8", errors="replace"))
        missing = [q for q in QUESTION_IDS if q not in answers.items]
        if missing:
            out.append(Finding("FAIL", "fidelity-answers", "答题缺 " + "、".join(missing)))
        thin = [
            q
            for q, body in answers.items.items()
            if TODO_MARK in body or len(normalize(body)) < MIN_ANSWER_CHARS
        ]
        if thin:
            out.append(Finding("FAIL", "fidelity-answers", "答题还是 TODO / 太短：" + "、".join(thin)))
        if not answers.answerer or TODO_MARK in answers.answerer:
            out.append(Finding("FAIL", "fidelity-answers", "answers.md 没写答题 Agent（answerer）"))
        if not answers.network_declared_off:
            out.append(Finding("FAIL", "fidelity-answers", "answers.md 没声明 network: none（答题禁止联网）"))
        if rubric_lines:
            answer_grams = ngrams("\n".join(answers.items.values()))
            leaked = [line[:30] for line in rubric_lines if overlap_ratio(line, answer_grams) >= RUBRIC_LEAK_RATIO]
            if leaked:
                out.append(
                    Finding("WARN", "fidelity-leak", f"答题里出现 rubric 原句 {len(leaked)} 处，疑似答题看过评分依据：「{leaked[0]}…」")
                )
        if all(not (f.code == "fidelity-answers" and f.level == "FAIL") for f in out):
            out.append(Finding("PASS", "fidelity-answers", f"答题 {len(answers.items)} 道，已声明未联网"))

    if a_path.is_file() and not b_path.is_file():
        out.append(Finding("WARN", "fidelity-blind", f"缺 {PACKET_DIR}/{BLIND_FILE}，风格辨识度没盲读：run.py fidelity blind"))
    elif b_path.is_file() and a_path.is_file() and b_path.stat().st_mtime + 1 < a_path.stat().st_mtime:
        out.append(Finding("WARN", "fidelity-blind", "answers.blind.md 比 answers.md 旧，重跑 run.py fidelity blind"))

    return out


def inspect_scorecard(text: str, packet_present: bool = True) -> List[Finding]:
    """核对 FIDELITY.md：总分、七维、满分、求和、崩溃、独立性、Q1–Q5 引用。"""
    card = parse_scorecard(text)
    out: List[Finding] = []

    if card.total is None:
        out.append(Finding("FAIL", "fidelity", "FIDELITY.md 里解析不到「总分：NN/100」"))
        return out
    if card.total < THRESHOLD:
        out.append(Finding("FAIL", "fidelity", f"保真度 {card.total} < {THRESHOLD}，不得宣称完成"))
    else:
        out.append(Finding("PASS", "fidelity", f"保真度 {card.total}/100"))

    if not card.rows:
        out.append(Finding("FAIL", "fidelity-rows", "FIDELITY.md 里没有七维分数表"))
        return out

    known = {name: (score, full) for name, score, full in card.rows if name in SCORECARD}
    missing = [d for d in SCORECARD if d not in known]
    if missing:
        out.append(Finding("FAIL", "fidelity-rows", "分数表缺维度：" + "、".join(missing)))
    for name, (score, full) in known.items():
        want = SCORECARD[name]
        if full != want:
            out.append(Finding("FAIL", "fidelity-rows", f"「{name}」满分写成 {full}，评分卡是 {want}"))
        if score > full:
            out.append(Finding("FAIL", "fidelity-rows", f"「{name}」{score}/{full} 超过满分"))
        elif full and score < full * COLLAPSE_RATIO:
            out.append(Finding("FAIL", "fidelity-dimension", f"「{name}」{score}/{full} 低于 40%，该维崩溃"))
    if not missing and card.row_sum != card.total:
        out.append(Finding("FAIL", "fidelity-rows", f"七维相加 {card.row_sum}，总分写的是 {card.total}"))
    if card.grade and card.grade != grade_for(card.total):
        out.append(Finding("WARN", "fidelity", f"总分 {card.total} 对应等级 {grade_for(card.total)}，卡上写的是 {card.grade}"))

    if not card.declared_independent:
        out.append(Finding("WARN", "fidelity-independent", "FIDELITY.md 未声明独立评分（或写了未独立 / 同会话），不得自称出厂合格"))
    elif card.independence is None:
        out.append(Finding("WARN", "fidelity-independent", "FIDELITY.md 没有「独立性：」字段，只在正文提到独立；按模板写清出题 / 答题 / 评分是谁"))
    else:
        out.append(Finding("PASS", "fidelity-independent", f"独立性：{card.independence}"))

    if packet_present:
        unreferenced = [q for q in QUESTION_IDS if q not in card.question_refs]
        if unreferenced:
            out.append(Finding("FAIL", "fidelity-records", "测试记录没逐题写到：" + "、".join(unreferenced)))
        else:
            out.append(Finding("PASS", "fidelity-records", "测试记录覆盖 Q1–Q5"))
    return out
