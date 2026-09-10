"""按蒸馏类型选六路查询。思想 / 现象不问生平。中文人物表达维不含 Twitter。"""

from __future__ import annotations

from typing import Dict, Optional


KIND_ALIASES = {
    "d1": "person",
    "person": "person",
    "人物": "person",
    "d2": "content",
    "content": "content",
    "内容": "content",
    "d3": "idea",
    "idea": "idea",
    "思想": "idea",
    "d4": "phenomenon",
    "phenomenon": "phenomenon",
    "现象": "phenomenon",
    "d5": "self",
    "self": "self",
    "自我": "self",
}

PERSON_DIMENSIONS: Dict[str, str] = {
    "writings": "{target} 著作 书单 论文 长文",
    "conversations": "{target} 访谈 播客 演讲",
    "expression": "{target} 社交媒体 观点 口癖",
    "critics": "{target} 批评 争议 负面评价 局限",
    "decisions": "{target} 决策 投资 关键选择 复盘",
    "timeline": "{target} 生平 时间线 里程碑",
}

CONTENT_DIMENSIONS: Dict[str, str] = {
    "writings": "{target} 原著 章节 核心论点",
    "conversations": "{target} 作者 访谈 演讲 播客",
    "critics": "{target} 书评 批评 误读",
    "applications": "{target} 应用 案例 实践",
    "assumptions": "{target} 隐藏假设 前提 边界",
    "adjacent": "{target} 同类著作 对照",
}

IDEA_DIMENSIONS: Dict[str, str] = {
    "writings": "{target} 原著 论文 提出者 长文",
    "conversations": "{target} 访谈 演讲 提出者 口述",
    "critics": "{target} 批评 误用 局限 反例",
    "applications": "{target} 应用 案例 决策 工程",
    "origins": "{target} 起源 历史 提出",
    "adjacent": "{target} 相邻思想 还原论 系统思维 类比",
}

PHENOMENON_DIMENSIONS: Dict[str, str] = {
    "mechanism": "{target} 机制 原因 怎么发生",
    "accidents": "{target} 偶然 运气 不可复制",
    "replicability": "{target} 可复制 条件 失败",
    "critics": "{target} 批评 质疑 另一种解释",
    "timeline": "{target} 时间线 节点 演变",
    "adjacent": "{target} 同类现象 对照",
}

PERSON_DIMENSIONS_EN: Dict[str, str] = {
    "writings": "{target} books letters essays writings shareholder letter",
    "conversations": "{target} interview podcast speech talk",
    "expression": "{target} twitter quotes style catchphrase",
    "critics": "{target} criticism controversy critique",
    "decisions": "{target} decisions strategy choices review",
    "timeline": "{target} biography timeline milestones",
}

CONTENT_DIMENSIONS_EN: Dict[str, str] = {
    "writings": "{target} book chapters thesis arguments",
    "conversations": "{target} author interview speech podcast",
    "critics": "{target} review critique misreading",
    "applications": "{target} applications cases practice",
    "assumptions": "{target} hidden assumptions premises limits",
    "adjacent": "{target} similar books comparison",
}

IDEA_DIMENSIONS_EN: Dict[str, str] = {
    "writings": "{target} original texts papers founder essays",
    "conversations": "{target} interview speech founder remarks",
    "critics": "{target} criticism misuse limits counterexamples",
    "applications": "{target} applications cases decisions engineering",
    "origins": "{target} origin history who proposed",
    "adjacent": "{target} adjacent ideas reductionism systems analogy",
}

PHENOMENON_DIMENSIONS_EN: Dict[str, str] = {
    "mechanism": "{target} mechanism causes how it happens",
    "accidents": "{target} contingency luck not replicable",
    "replicability": "{target} replicable conditions failures",
    "critics": "{target} criticism alternative explanations",
    "timeline": "{target} timeline milestones evolution",
    "adjacent": "{target} similar phenomena comparison",
}

KIND_DIMENSIONS = {
    "person": PERSON_DIMENSIONS,
    "content": CONTENT_DIMENSIONS,
    "idea": IDEA_DIMENSIONS,
    "phenomenon": PHENOMENON_DIMENSIONS,
}

KIND_DIMENSIONS_EN = {
    "person": PERSON_DIMENSIONS_EN,
    "content": CONTENT_DIMENSIONS_EN,
    "idea": IDEA_DIMENSIONS_EN,
    "phenomenon": PHENOMENON_DIMENSIONS_EN,
}

DEFAULT_DIMENSIONS = PERSON_DIMENSIONS

# 维度 → references/distillation/ 里的落盘文件。多个维度可以共用一个文件（按节追加）。
DIMENSION_FILES: Dict[str, str] = {
    "writings": "01-writings.md",
    "mechanism": "01-writings.md",
    "conversations": "02-conversations.md",
    "expression": "03-expression-dna.md",
    "critics": "04-limitations.md",
    "assumptions": "04-limitations.md",
    "replicability": "04-limitations.md",
    "decisions": "05-decisions.md",
    "applications": "05-decisions.md",
    "accidents": "05-decisions.md",
    "timeline": "06-timeline.md",
    "origins": "06-timeline.md",
    "adjacent": "07-similar-objects.md",
}

DIMENSION_LABELS: Dict[str, str] = {
    "writings": "著作 / 长文",
    "conversations": "访谈 / 播客 / 演讲",
    "expression": "表达 / 社交媒体",
    "critics": "外部评价 / 批评",
    "decisions": "重大决策",
    "timeline": "时间线",
    "adjacent": "同类对照",
    "applications": "应用案例",
    "assumptions": "隐藏假设 / 前提",
    "origins": "起源",
    "mechanism": "底层机制",
    "accidents": "偶然因素",
    "replicability": "可复制性",
}

# 每一路要找什么、什么时候可以停。摘自 research-guide.md 的六路表。
DIMENSION_HINTS: Dict[str, str] = {
    "writings": "≥2 篇长文或 1 本书核心；官方渠道 / 本人原文优先；核心论点开始重复就停",
    "conversations": "≥1 段深度对话；即兴问答优于演讲；找到被追问后的立场变化就停",
    "expression": "≥20 条本人发言；争议发言优于日常分享；风格可辨认就停",
    "critics": "≥2 个不同视角，正负评价都要；失败必须是本人承认的才算失败",
    "decisions": "≥2 个决策，每个都有背景 + 当时想法 + 事后反思",
    "timeline": "关键转折从成名前到最近 12 个月",
    "adjacent": "2–3 个同类对象对照，找差异而不是相似",
    "applications": "≥2 个应用案例，含至少 1 个失败或误用",
    "assumptions": "隐藏前提、适用边界、什么时候不成立",
    "origins": "起源场景、提出者原文、最早的表述",
    "mechanism": "底层机制：谁、在什么条件下、为什么发生",
    "accidents": "偶然因素、运气、不可复制的部分",
    "replicability": "可复制的条件 + 试图复制但失败的案例",
}

# 永远不作为来源（research-guide.md）。公号原文可作一手，洗稿号仍在黑名单。
SOURCE_BLACKLIST = (
    "zhihu.com",
    "baike.baidu.com",
)

EMPTY_COLLECTION_HINT = """脚本没有拿到任何可用素材。
搜索由宿主 Agent 的搜索工具完成，脚本只负责 plan / ingest / check。
请按 plan.json 里的六路查询用宿主搜索补采集，把结果写成 results.json 再跑 ingest。
采不到就把缺口写进 00-sources.md。不要假装采过，不要对着 0 条素材写分析。"""


def dimension_file(dimension: str) -> str:
    """维度对应的底稿文件名；未知维度落到 10-<维度>.md。"""
    return DIMENSION_FILES.get(dimension, f"10-{dimension}.md")


def dimension_label(dimension: str) -> str:
    return DIMENSION_LABELS.get(dimension, dimension)


def dimension_hint(dimension: str) -> str:
    return DIMENSION_HINTS.get(dimension, "标 URL 和一手 / 二手 / 推断")


class UnknownKindError(ValueError):
    pass


class SelfKindError(ValueError):
    """D5 自我蒸馏不应走网页 collect。"""


def normalize_kind(kind: Optional[str]) -> str:
    if not kind:
        return "person"
    key = kind.strip().lower()
    if key in KIND_ALIASES:
        return KIND_ALIASES[key]
    raise UnknownKindError(f"未知采集类型: {kind}（person/content/idea/phenomenon/self）")


def query_locale(target: Optional[str]) -> str:
    """无汉字且有拉丁字母 → en，其余 → zh。"""
    if not target:
        return "zh"
    has_cjk = any("\u4e00" <= char <= "\u9fff" for char in target)
    has_latin = any(char.isascii() and char.isalpha() for char in target)
    if has_latin and not has_cjk:
        return "en"
    return "zh"


def dimensions_for(
    kind: Optional[str] = None,
    target: Optional[str] = None,
    locale: Optional[str] = None,
) -> Dict[str, str]:
    resolved = normalize_kind(kind)
    if resolved == "self":
        raise SelfKindError("自我蒸馏请用 collect-local，不要出网络查询计划（plan / ingest）")
    resolved_locale = locale or query_locale(target)
    pack = KIND_DIMENSIONS_EN if resolved_locale == "en" else KIND_DIMENSIONS
    return dict(pack[resolved])
