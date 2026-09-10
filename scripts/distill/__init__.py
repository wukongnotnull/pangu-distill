"""
distill 模块 - 蒸馏流水线的确定性部分

plan   → 按对象类型出六路查询计划，交给宿主 Agent 用自己的搜索工具执行
ingest → 接收宿主搜到的结果，去重、过黑名单、抓正文，落成 references/distillation/ 底稿
check  → 机器校验产物：命名、4.5 层、证据三件套、FIDELITY + fidelity/ 测试包
fidelity → 保真度测试包：init 出题模板、blind 遮名，出题 / 答题 / 评分三方分离
local  → 本地素材（PDF / Word / 字幕 / 音视频）读取

搜索本身不在脚本里做：宿主的联网搜索远强于无头爬虫。
"""

from .dimensions import (
    EMPTY_COLLECTION_HINT,
    SelfKindError,
    UnknownKindError,
    dimensions_for,
    normalize_kind,
    query_locale,
)
from .plan import Plan, PlanQuery, build_plan, load_plan
from .ingest import IngestSummary, SourceItem, ingest, load_results
from .check import CheckReport, Finding, run_check
from .fidelity import blind_answers, init_packet, inspect_packet, inspect_scorecard, parse_scorecard

__all__ = [
    "EMPTY_COLLECTION_HINT",
    "SelfKindError",
    "UnknownKindError",
    "dimensions_for",
    "normalize_kind",
    "query_locale",
    "Plan",
    "PlanQuery",
    "build_plan",
    "load_plan",
    "IngestSummary",
    "SourceItem",
    "ingest",
    "load_results",
    "CheckReport",
    "Finding",
    "run_check",
    "blind_answers",
    "init_packet",
    "inspect_packet",
    "inspect_scorecard",
    "parse_scorecard",
]
