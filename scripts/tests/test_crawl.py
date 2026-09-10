import pytest

from crawl.base import BlockedError
from crawl.chain import CrawlerSearch
from crawl.duckduckgo import DuckDuckGoSearch
from crawl.wikipedia import (
    WikipediaSearch,
    fold_cjk,
    has_cjk,
    mentions_name,
    merge_hits,
    name_aliases,
    simplify_query,
    split_wiki_query,
    strip_wiki_markup,
)
from shared import SearchResult, SearchSource


def _hit(title, curid, snippet="", lang="zh"):
    return SearchResult(
        title=title,
        url=f"https://{lang}.wikipedia.org/?curid={curid}",
        snippet=snippet,
        source=SearchSource.WIKIPEDIA,
    )


def test_simplify_query_keeps_object_name_only():
    assert simplify_query("Jeff Bezos 著作 书单 论文 长文") == "Jeff Bezos"
    assert simplify_query("第一性原理 原著 论文") == "第一性原理"
    assert simplify_query("张小龙 著作 书单 论文 长文") == "张小龙"
    assert has_cjk("张小龙 生平") is True
    assert has_cjk("Jeff Bezos biography") is False
    assert split_wiki_query("张小龙 著作 书单 论文 长文") == ("张小龙", "著作")
    assert split_wiki_query("Jeff Bezos 著作 书单") == ("Jeff Bezos", "著作")
    assert fold_cjk("張小龍") == "张小龙"


def test_strip_wiki_markup():
    raw = '在哲学与科学领域，<span class="searchmatch">第一</span>原理'
    assert "span" not in strip_wiki_markup(raw)
    assert "第一" in strip_wiki_markup(raw)


def test_ddg_raises_on_captcha_page():
    html = '<div class="anomaly-modal__puzzle"></div>'
    with pytest.raises(BlockedError):
        DuckDuckGoSearch._raise_if_blocked(html)


def test_wikipedia_maps_api_hits(monkeypatch):
    class FakeResp:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "query": {
                    "search": [
                        {"title": "第一原理", "pageid": 123, "snippet": "在哲学与科学领域，<span>第一</span>原理"}
                    ]
                }
            }

    wiki = WikipediaSearch(delay=0)
    monkeypatch.setattr(wiki.session, "get", lambda *a, **k: FakeResp())
    hits = wiki._search_lang("zh", "第一性原理", 5)
    assert hits[0].url == "https://zh.wikipedia.org/?curid=123"
    assert hits[0].source == SearchSource.WIKIPEDIA


def test_wikipedia_chinese_uses_name_even_when_suffix_hits(monkeypatch):
    wiki = WikipediaSearch(delay=0)
    calls = []

    def fake_all(query, num_results):
        calls.append(query)
        if query == "张小龙":
            return [_hit("張小龍", 1, "微信")]
        return [_hit("古龙", 2, "著作")]

    monkeypatch.setattr(wiki, "_search_all_langs", fake_all)
    hits = wiki.search("张小龙 著作 书单 论文 长文", 5)
    assert calls[0] == "张小龙"
    assert '"张小龙" 著作' in calls
    assert hits[0].title == "張小龍"
    assert all(hit.title != "古龙" for hit in hits)


def test_wikipedia_keeps_hint_hits_that_name_the_person(monkeypatch):
    wiki = WikipediaSearch(delay=0)

    def fake_all(query, num_results):
        if query == "雷军":
            return [_hit("雷军", 1, "小米")]
        if query == '"雷军" 演讲':
            return [_hit("Are you OK", 9, "源自企业家雷军在印度的营销演讲"), _hit("李彦宏", 8, "中科大演讲砸场")]
        return [_hit("古龙", 2, "著作")]

    monkeypatch.setattr(wiki, "_search_all_langs", fake_all)
    titles = [item.title for item in wiki.search("雷军 演讲 公开课", 5)]
    assert titles[0] == "Are you OK"
    assert "雷军" in titles
    assert "李彦宏" not in titles


def test_mentions_name_folds_traditional_and_rejects_lists():
    seed = _hit("張小龍", 1, "微信")
    aliases = name_aliases("张小龙", [seed])
    assert "張小龍" in aliases
    assert mentions_name(seed, "张小龙", aliases)
    assert mentions_name(_hit("古龙", 2, "武侠著作"), "张小龙", aliases) is False
    assert mentions_name(_hit("张茵", 4, "福布斯：张茵、张近东、雷军"), "雷军", ["雷军"]) is False
    assert mentions_name(_hit("高山下的花环", 5, "电话打到雷军长的指挥所"), "雷军", ["雷军"]) is False
    merged = merge_hits([_hit("古龙", 2)], [seed], 2)
    assert [item.title for item in merged] == ["古龙", "張小龍"]


def test_chain_records_skipped_engines(monkeypatch):
    chain = CrawlerSearch(delay=0)

    class Blocked:
        def search(self, query, n):
            raise BlockedError("验证页")

    class Wiki:
        def search(self, query, n):
            return [_hit("雷军", 1)]

    chain._ddg = Blocked()
    chain._wiki = Wiki()
    results = chain.search("雷军 演讲", 5)
    assert results[0].title == "雷军"
    assert chain.last_errors and "duckduckgo" in chain.last_errors[0]
    assert "BlockedError" in chain.last_errors[0]


def test_chain_returns_empty_and_errors_when_everything_fails():
    chain = CrawlerSearch(delay=0)

    class Boom:
        def search(self, query, n):
            raise RuntimeError("down")

    chain._ddg = Boom()
    chain._wiki = Boom()
    assert chain.search("x", 3) == []
    assert len(chain.last_errors) == 2
