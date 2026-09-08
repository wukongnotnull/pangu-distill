"""维基百科搜索。不需要 API key，供 DuckDuckGo HTML 被拦时降级。"""

from __future__ import annotations

import html
import re
from typing import Iterable, List, Optional, Sequence, Tuple
from urllib.parse import quote

import requests

from crawl.base import BaseSearchEngine
from shared import SearchResult, SearchSource


def strip_wiki_markup(text: str) -> str:
    cleaned = re.sub(r"<[^>]+>", "", text or "")
    return html.unescape(cleaned).strip()


def has_cjk(text: str) -> bool:
    return any("\u4e00" <= char <= "\u9fff" for char in text or "")


_TRAD2SIMP = {
    "張": "张",
    "國": "国",
    "學": "学",
    "經": "经",
    "歷": "历",
    "東": "东",
    "門": "门",
    "軍": "军",
    "龍": "龙",
    "馬": "马",
    "語": "语",
    "時": "时",
    "書": "书",
    "陳": "陈",
    "劉": "刘",
    "楊": "杨",
    "黃": "黄",
    "吳": "吴",
    "鄭": "郑",
    "趙": "赵",
    "錢": "钱",
    "孫": "孙",
    "後": "后",
    "與": "与",
    "這": "这",
    "過": "过",
    "個": "个",
    "開": "开",
    "關": "关",
    "現": "现",
    "點": "点",
    "業": "业",
    "發": "发",
    "實": "实",
    "體": "体",
    "機": "机",
    "車": "车",
    "氣": "气",
    "漢": "汉",
    "無": "无",
    "於": "于",
    "對": "对",
    "團": "团",
    "彙": "汇",
    "風": "风",
    "華": "华",
    "爾": "尔",
    "長": "长",
    "齊": "齐",
    "萬": "万",
    "兩": "两",
    "來": "来",
    "還": "还",
    "說": "说",
    "會": "会",
    "從": "从",
    "當": "当",
    "應": "应",
    "種": "种",
    "為": "为",
    "麼": "么",
    "隻": "只",
}


def fold_cjk(text: str) -> str:
    """繁体折成简体，便于 张小龙 / 張小龍 对上。"""
    return "".join(_TRAD2SIMP.get(char, char) for char in text or "")


def simplify_query(query: str) -> str:
    """抽出对象名。首词是汉字则只留它，避免 Twitter / 著作等后缀反客为主。"""
    words = [part for part in (query or "").split() if part]
    if words and has_cjk(words[0]):
        return words[0]
    latin = " ".join(re.findall(r"[A-Za-z][A-Za-z'.-]*", query or ""))
    if latin:
        return latin
    return words[0] if words else (query or "")


def split_wiki_query(query: str) -> Tuple[str, Optional[str]]:
    """对象名 + 第一个维关键词。不要把著作/书单/论文整串丢给维基。"""
    core = simplify_query(query)
    rest = (query or "").strip()
    if core and rest.startswith(core):
        rest = rest[len(core) :].strip()
    hint = rest.split()[0] if rest.split() else None
    if hint and fold_cjk(hint) == fold_cjk(core):
        hint = None
    return core, hint


def name_aliases(name: str, seed: Sequence[SearchResult]) -> List[str]:
    aliases = [name] if name else []
    folded = fold_cjk(name)
    for hit in seed:
        title = hit.title or ""
        if title and fold_cjk(title) == folded:
            aliases.append(title)
    seen = set()
    unique: List[str] = []
    for alias in aliases:
        if alias and alias not in seen:
            seen.add(alias)
            unique.append(alias)
    return unique


def cjk_letters(text: str) -> str:
    return "".join(char for char in fold_cjk(text or "") if "\u4e00" <= char <= "\u9fff")


def looks_like_other_person(title: str, aliases: Sequence[str]) -> bool:
    """2–3 个汉字的标题多半是另一个人名。摘要里带一句对象名不够。"""
    compact = cjk_letters(title)
    if not (2 <= len(compact) <= 3):
        return False
    for alias in aliases:
        if compact == cjk_letters(alias):
            return False
    return True


def name_in_text(text: str, alias: str) -> bool:
    """对象名出现在正文里。排除「雷军长」这种后接「长」的假阳性。"""
    if not alias:
        return False
    folded_text = fold_cjk(text or "")
    folded_alias = fold_cjk(alias)
    if not folded_alias:
        return False
    start = 0
    while True:
        index = folded_text.find(folded_alias, start)
        if index < 0:
            return False
        after = folded_text[index + len(folded_alias) : index + len(folded_alias) + 1]
        if after == "长":
            start = index + 1
            continue
        return True


def mentions_name(
    hit: SearchResult,
    name: str,
    aliases: Sequence[str],
    seed_urls: Optional[Iterable[str]] = None,
) -> bool:
    if seed_urls is not None and hit.url in set(seed_urls):
        return True
    if looks_like_other_person(hit.title, aliases):
        return any(name_in_text(hit.title or "", alias) for alias in aliases)
    blob = f"{hit.title or ''} {hit.snippet or ''}"
    return any(name_in_text(blob, alias) for alias in aliases)


def merge_hits(
    preferred: Sequence[SearchResult],
    fallback: Sequence[SearchResult],
    limit: int,
) -> List[SearchResult]:
    seen = set()
    merged: List[SearchResult] = []
    for hit in list(preferred) + list(fallback):
        if not hit.url or hit.url in seen:
            continue
        seen.add(hit.url)
        merged.append(hit)
        if len(merged) >= limit:
            break
    return merged


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
        core, hint = split_wiki_query(query)

        # 有汉字：先钉住对象名，再用「名字 + 一维」补区分。
        # 整句后缀（著作 书单 论文）仍会带跑，不直接丢给 list=search。
        if has_cjk(query) and core and core != query:
            seed = self._search_all_langs(core, num_results)
            if not seed:
                return self._search_all_langs(query, num_results)
            if not hint:
                return seed
            return merge_hits(
                self._hint_hits(core, hint, seed, num_results),
                seed,
                num_results,
            )

        results = self._search_all_langs(query, num_results)
        if results:
            return results
        if core and core != query:
            return self._search_all_langs(core, num_results)
        return []

    def _hint_hits(
        self,
        core: str,
        hint: str,
        seed: Sequence[SearchResult],
        num_results: int,
    ) -> List[SearchResult]:
        aliases = name_aliases(core, seed)
        quoted = self._search_all_langs(f'"{core}" {hint}', num_results)
        kept = [hit for hit in quoted if mentions_name(hit, core, aliases)]
        if kept:
            return kept
        raw = self._search_all_langs(f"{core} {hint}", num_results)
        return [hit for hit in raw if mentions_name(hit, core, aliases)]

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
