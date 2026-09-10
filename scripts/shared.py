"""
共享类型定义

所有模块共享的枚举和数据类
避免重复定义导致的不一致问题
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class SearchSource(Enum):
    """搜索结果来自哪里。HOST = 宿主 Agent 自己的搜索工具。"""
    HOST = "host"
    DUCKDUCKGO = "duckduckgo"
    WIKIPEDIA = "wikipedia"
    UNKNOWN = "unknown"


class ContentLanguage(Enum):
    """内容语言"""
    ZH = "zh"
    EN = "en"
    MIXED = "mixed"
    UNKNOWN = "unknown"


@dataclass
class SearchResult:
    """单条搜索结果"""
    title: str
    url: str
    snippet: str
    source: SearchSource = SearchSource.UNKNOWN
    rank: int = 0
    retrieved_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "source": self.source.value,
            "rank": self.rank,
            "retrieved_at": self.retrieved_at.isoformat(),
        }


@dataclass
class ContentResult:
    """单条内容抓取结果"""
    url: str
    title: str
    content: str
    word_count: int = 0
    language: ContentLanguage = ContentLanguage.UNKNOWN
    fetched_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "url": self.url,
            "title": self.title,
            "content": self.content,
            "word_count": self.word_count,
            "language": self.language.value,
            "fetched_at": self.fetched_at.isoformat(),
        }
