"""
crawl 模块 - 抓取与保底搜索

主采集路径是宿主 Agent 自己的搜索工具（见 distill.plan / distill.ingest）。
这里只有：正文抓取器（ingest 用）、DuckDuckGo / 维基百科保底搜索（run.py search 用）。
"""

from .base import BlockedError
from .chain import CrawlerSearch
from .duckduckgo import DuckDuckGoSearch
from .wikipedia import WikipediaSearch
from .fetcher import ContentFetcher

__all__ = [
    "BlockedError",
    "CrawlerSearch",
    "DuckDuckGoSearch",
    "WikipediaSearch",
    "ContentFetcher",
]
