"""按蒸馏类型选六路查询。人物默认不变；思想 / 现象不再问生平或 Twitter。"""

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
    "expression": "{target} Twitter 社交媒体 观点 口癖",
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

KIND_DIMENSIONS = {
    "person": PERSON_DIMENSIONS,
    "content": CONTENT_DIMENSIONS,
    "idea": IDEA_DIMENSIONS,
    "phenomenon": PHENOMENON_DIMENSIONS,
}

DEFAULT_DIMENSIONS = PERSON_DIMENSIONS

EMPTY_COLLECTION_HINT = """脚本搜索源都空了（Agent 搜索不可用，或爬虫被拦）。
请用当前宿主的搜索工具补采集，并把失败写进 00-sources.md。不要假装采过。
不要对着 0 条素材写分析报告。"""


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


def dimensions_for(kind: Optional[str] = None) -> Dict[str, str]:
    resolved = normalize_kind(kind)
    if resolved == "self":
        raise SelfKindError("自我蒸馏请用 collect-local，不要跑网页 collect / team")
    return dict(KIND_DIMENSIONS[resolved])
