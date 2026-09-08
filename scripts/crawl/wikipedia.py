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


def has_cjk(text: str) -> bool:
    return any("\u4e00" <= char <= "\u9fff" for char in text or "")


def simplify_query(query: str) -> str:
    """抽出对象名。首词是汉字则只留它，避免 Twitter / 著作等后缀反客为主。"""
    words = [part for part in (query or "").split() if part]
    if words and has_cjk(words[0]):
        return words[0]
    latin = " ".join(re.findall(r"[A-Za-z][A-Za-z'.-]*", query or ""))
    if latin:
        return latin
    return words[0] if words else (query or "")


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
        core = simplify_query(query)

        # 中文六路后缀会把 list=search 带跑（古龙、春晚、張曼玉）。
        # 有汉字时先搜对象名；名字有结果就停，不再把整句后缀丢进去。
        if has_cjk(query) and core and core != query:
            named = self._search_all_langs(core, num_results)
            if named:
                return named
            return self._search_all_langs(query, num_results)

        results = self._search_all_langs(query, num_results)
        if results:
            return results
        if core and core != query:
            return self._search_all_langs(core, num_results)
        return []

    def _search_all_langs(self, query: str, num_results: int) -> List[SearchResult]:
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
        if has_cjk(query):
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
