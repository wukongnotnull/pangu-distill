"""维基百科搜索。不需要 API key，供 DuckDuckGo HTML 被拦时降级。"""

from __future__ import annotations

import html
import re
from typing import List
from urllib.parse import quote

import requests

from crawl.base import BaseSearchEngine
from shared import SearchResult, SearchSource


def strip_wiki_markup(text: str) -> str:
    cleaned = re.sub(r"<[^>]+>", "", text or "")
    return html.unescape(cleaned).strip()


class WikipediaSearch(BaseSearchEngine):
    USER_AGENT = "pangu-distill/0.1 (https://github.com/wukongnotnull/pangu-distill)"
    TIMEOUT = 15

    def __init__(self, delay: float = 0.4):
        super().__init__(delay)
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.USER_AGENT})

    def search(self, query: str, num_results: int = 10) -> List[SearchResult]:
        query = self._validate_query(query)
        num_results = self._validate_num_results(num_results)

        results: List[SearchResult] = []
        seen = set()
        langs = self._langs(query)
        per_lang = max(3, (num_results + len(langs) - 1) // len(langs))

        for lang in langs:
            for item in self._search_lang(lang, query, per_lang):
                if item.url in seen:
                    continue
                seen.add(item.url)
                results.append(item)
                if len(results) >= num_results:
                    return results
        return results

    def _langs(self, query: str) -> List[str]:
        if any("\u4e00" <= char <= "\u9fff" for char in query):
            return ["zh", "en"]
        return ["en", "zh"]

    def _search_lang(self, lang: str, query: str, limit: int) -> List[SearchResult]:
        self._wait_before_request()
        response = self.session.get(
            f"https://{lang}.wikipedia.org/w/api.php",
            params={
                "action": "query",
                "list": "search",
                "srsearch": query,
                "srlimit": limit,
                "format": "json",
                "utf8": 1,
            },
            timeout=self.TIMEOUT,
        )
        response.raise_for_status()
        hits = response.json().get("query", {}).get("search", [])
        results = []
        for rank, hit in enumerate(hits, start=1):
            title = hit.get("title") or ""
            pageid = hit.get("pageid")
            if pageid:
                url = f"https://{lang}.wikipedia.org/?curid={pageid}"
            elif title:
                url = f"https://{lang}.wikipedia.org/wiki/{quote(title.replace(' ', '_'))}"
            else:
                continue
            results.append(
                SearchResult(
                    title=title,
                    url=url,
                    snippet=strip_wiki_markup(hit.get("snippet") or ""),
                    source=SearchSource.WIKIPEDIA,
                    rank=rank,
                )
            )
        return results
