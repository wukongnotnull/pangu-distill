"""保底搜索链：DuckDuckGo HTML → 维基百科。

这不是主采集路径。主路径是 plan → 宿主搜索 → ingest。
这条链只给 `run.py search` 做无宿主时的兜底，以及给测试用。每次搜索后 `last_errors`
记录被跳过的引擎和原因，CLI 会原样打印，不再静默吞掉。
"""

from __future__ import annotations

from typing import List

from shared import SearchResult


class CrawlerSearch:
    def __init__(self, delay: float = 2.0):
        self.delay = delay
        self.last_errors: List[str] = []
        self._ddg = None
        self._wiki = None

    def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        self.last_errors = []

        try:
            if self._ddg is None:
                from crawl.duckduckgo import DuckDuckGoSearch

                self._ddg = DuckDuckGoSearch(delay=self.delay)
            results = self._ddg.search(query, num_results)
            if results:
                return results
            self.last_errors.append("duckduckgo: 0 条")
        except Exception as exc:
            self.last_errors.append(f"duckduckgo: {type(exc).__name__}: {exc}")

        try:
            if self._wiki is None:
                from crawl.wikipedia import WikipediaSearch

                self._wiki = WikipediaSearch()
            results = self._wiki.search(query, num_results)
            if results:
                return results
            self.last_errors.append("wikipedia: 0 条")
        except Exception as exc:
            self.last_errors.append(f"wikipedia: {type(exc).__name__}: {exc}")

        return []
