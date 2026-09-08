"""
降级触发器和备选爬虫
"""

from typing import List, Optional

from .models import SearchResult, ContentResult, SearchSource


class FallbackTrigger:
    """降级触发器"""

    # 可降级的错误类型
    FALLBACK_ERRORS = (
        "ToolNotFoundError",
        "TimeoutError",
        "RateLimitError",
        "BlockedError",
        "AgentToolError",
    )

    @classmethod
    def should_fallback(cls, error: Exception) -> bool:
        """判断是否需要降级到爬虫"""
        error_name = type(error).__name__
        return error_name in cls.FALLBACK_ERRORS or "timeout" in str(error).lower()

    @classmethod
    def get_fallback_reason(cls, error: Exception) -> str:
        """获取降级原因"""
        return f"Agent 工具失败: {type(error).__name__}: {str(error)[:100]}"


class CrawlerFallback:
    """
    备选爬虫

    当 Agent 工具不可用或失败时使用
    """

    def __init__(self, engine: str = "duckduckgo"):
        self.engine = engine
        self._search_impl = None
        self._fetch_impl = None

    def _get_search_impl(self):
        """获取搜索实现"""
        if self._search_impl is None:
            if self.engine == "duckduckgo":
                from ..crawl.duckduckgo import DuckDuckGoSearch
                self._search_impl = DuckDuckGoSearch()
            elif self.engine == "bing":
                from ..crawl.bing import BingSearch
                self._search_impl = BingSearch()
            else:
                from ..crawl.duckduckgo import DuckDuckGoSearch
                self._search_impl = DuckDuckGoSearch()
        return self._search_impl

    def _get_fetch_impl(self):
        """获取抓取实现"""
        if self._fetch_impl is None:
            from ..crawl.fetcher import ContentFetcher
            self._fetch_impl = ContentFetcher()
        return self._fetch_impl

    def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        """DuckDuckGo HTML 被拦时降级到维基百科。"""
        errors: List[str] = []

        try:
            impl = self._get_search_impl()
            results = impl.search(query, num_results)
            if results:
                for item in results:
                    if item.source == SearchSource.UNKNOWN:
                        item.source = (
                            SearchSource.DUCKDUCKGO
                            if self.engine == "duckduckgo"
                            else SearchSource.BING
                        )
                return results
        except Exception as exc:
            errors.append(f"{self.engine}: {exc}")

        try:
            from crawl.wikipedia import WikipediaSearch

            wiki = WikipediaSearch()
            results = wiki.search(query, num_results)
            if results:
                return results
        except Exception as exc:
            errors.append(f"wikipedia: {exc}")

        return []

    def fetch(self, url: str) -> ContentResult:
        """抓取内容"""
        impl = self._get_fetch_impl()
        return impl.fetch(url)
