import pytest

from crawl.base import BlockedError
from crawl.duckduckgo import DuckDuckGoSearch
from crawl.wikipedia import (
    fold_cjk,
    has_cjk,
    mentions_name,
    merge_hits,
    name_aliases,
    simplify_query,
    split_wiki_query,
    strip_wiki_markup,
)
from search.dimensions import (
    IDEA_DIMENSIONS,
    PERSON_DIMENSIONS,
    PERSON_DIMENSIONS_EN,
    SelfKindError,
    dimensions_for,
    normalize_kind,
    query_locale,
)
from search.models import CollectionResult
from search.multi_agent import MasterSearchPipeline
from search.pipeline import SearchPipeline
from shared import SearchSource


def test_kind_aliases_and_idea_has_no_biography():
    assert normalize_kind("D3") == "idea"
    assert normalize_kind("思想") == "idea"
    idea = dimensions_for("idea")
    assert idea == IDEA_DIMENSIONS
    blob = " ".join(idea.values())
    assert "生平" not in blob
    assert "Twitter" not in blob
    assert "起源" in idea["origins"]


def test_latin_target_uses_english_person_dimensions():
    assert query_locale("Jeff Bezos") == "en"
    assert query_locale("张一鸣") == "zh"
    assert query_locale("贝索斯 Bezos") == "zh"
    en = dimensions_for("person", target="Jeff Bezos")
    zh = dimensions_for("person", target="张一鸣")
    assert en == PERSON_DIMENSIONS_EN
    assert zh == PERSON_DIMENSIONS
    assert "生平" not in " ".join(en.values())
    assert "biography" in en["timeline"]
    assert "shareholder letter" in en["writings"]


def test_zh_person_expression_drops_twitter():
    zh = dimensions_for("person", target="张小龙")
    en = dimensions_for("person", target="Jeff Bezos")
    assert "Twitter" not in zh["expression"]
    assert "Twitter" not in " ".join(zh.values())
    assert "twitter" in en["expression"]


def test_simplify_query_keeps_object_name_only():
    assert simplify_query("Jeff Bezos 著作 书单 论文 长文") == "Jeff Bezos"
    assert simplify_query("第一性原理 原著 论文") == "第一性原理"
    assert simplify_query("张小龙 著作 书单 论文 长文") == "张小龙"
    assert simplify_query("张小龙 Twitter 社交媒体 观点 口癖") == "张小龙"
    assert simplify_query("贝索斯 Bezos 著作") == "贝索斯"
    assert has_cjk("张小龙 生平") is True
    assert has_cjk("Jeff Bezos biography") is False
    assert split_wiki_query("张小龙 著作 书单 论文 长文") == ("张小龙", "著作")
    assert split_wiki_query("雷军 社交媒体 观点 口癖") == ("雷军", "社交媒体")
    assert split_wiki_query("Jeff Bezos 著作 书单") == ("Jeff Bezos", "著作")
    assert fold_cjk("張小龍") == "张小龙"


def test_self_kind_refuses_web_collect():
    with pytest.raises(SelfKindError):
        dimensions_for("self")


def test_strip_wiki_markup():
    raw = '在哲学与科学领域，<span class="searchmatch">第一</span>原理'
    assert "span" not in strip_wiki_markup(raw)
    assert "第一" in strip_wiki_markup(raw)


def test_ddg_raises_on_captcha_page():
    html = '<div class="anomaly-modal__puzzle"></div>'
    with pytest.raises(BlockedError):
        DuckDuckGoSearch._raise_if_blocked(html)


def test_collect_dimension_empty_is_failure():
    pipeline = SearchPipeline(prefer_agent=False)

    class EmptyTool:
        def search(self, query, num_results=10):
            return []

        def fetch(self, url):
            raise AssertionError("should not fetch")

    pipeline.search_tool = EmptyTool()
    result = pipeline.collect_dimension("writings", "第一性原理 原著")
    assert result.success is False
    assert result.error == "no search results"
    assert result.results == []


def test_collection_result_success_follows_counts():
    empty = CollectionResult(target="x")
    assert empty.success is False
    empty.total_results = 3
    assert empty.success is True
    payload = empty.to_dict()
    assert payload["success"] is True


def test_team_stops_without_analyst_reports():
    pipeline = MasterSearchPipeline(max_agents=3)

    class EmptyTool:
        def search(self, query, num_results=10):
            return []

        def fetch(self, url):
            raise AssertionError("should not fetch")

    pipeline.search_tool = EmptyTool()
    result = pipeline.collect("第一性原理", {"writings": "{target} 原著"}, num_results=3)
    assert result.all_results == []
    assert result.analyst_outputs == []
    assert "不写空分析" in result.master_output
    assert "宿主" in result.master_output


def test_wikipedia_maps_api_hits(monkeypatch):
    from crawl.wikipedia import WikipediaSearch

    class FakeResp:
        def raise_for_status(self):
            return None

        def json(self):
            return {
                "query": {
                    "search": [
                        {
                            "title": "第一原理",
                            "pageid": 123,
                            "snippet": "在哲学与科学领域，<span>第一</span>原理",
                        }
                    ]
                }
            }

    wiki = WikipediaSearch(delay=0)
    monkeypatch.setattr(wiki.session, "get", lambda *a, **k: FakeResp())
    hits = wiki._search_lang("zh", "第一性原理", 5)
    assert hits[0].url == "https://zh.wikipedia.org/?curid=123"
    assert hits[0].source == SearchSource.WIKIPEDIA
    assert "第一原理" in hits[0].title


def test_wikipedia_retries_simplified_name(monkeypatch):
    from crawl.wikipedia import WikipediaSearch
    from shared import SearchResult

    wiki = WikipediaSearch(delay=0)
    calls = []

    def fake_all(query, num_results):
        calls.append(query)
        if query == "Jeff Bezos":
            return [
                SearchResult(
                    title="Jeff Bezos",
                    url="https://en.wikipedia.org/?curid=1",
                    snippet="founder",
                    source=SearchSource.WIKIPEDIA,
                )
            ]
        return []

    monkeypatch.setattr(wiki, "_search_all_langs", fake_all)
    # 带汉字后缀 → 先搜拉丁名，再用「名字 + 著作」补一维
    hits = wiki.search("Jeff Bezos 著作 书单", 5)
    assert calls[0] == "Jeff Bezos"
    assert '"Jeff Bezos" 著作' in calls
    assert hits[0].title == "Jeff Bezos"

    calls.clear()
    # 纯英文六路：整句先搜；simplify 与整句相同则不再重试
    empty_then_full = wiki.search("Jeff Bezos books letters", 5)
    assert calls == ["Jeff Bezos books letters"]
    assert empty_then_full == []


def test_wikipedia_chinese_uses_name_even_when_suffix_hits(monkeypatch):
    from crawl.wikipedia import WikipediaSearch
    from shared import SearchResult

    wiki = WikipediaSearch(delay=0)
    calls = []

    def fake_all(query, num_results):
        calls.append(query)
        if query == "张小龙":
            return [
                SearchResult(
                    title="張小龍",
                    url="https://zh.wikipedia.org/?curid=1",
                    snippet="微信",
                    source=SearchSource.WIKIPEDIA,
                )
            ]
        return [
            SearchResult(
                title="古龙",
                url="https://zh.wikipedia.org/?curid=2",
                snippet="著作",
                source=SearchSource.WIKIPEDIA,
            )
        ]

    monkeypatch.setattr(wiki, "_search_all_langs", fake_all)
    hits = wiki.search("张小龙 著作 书单 论文 长文", 5)
    assert calls[0] == "张小龙"
    assert '"张小龙" 著作' in calls
    assert hits[0].title == "張小龍"
    assert all(hit.title != "古龙" for hit in hits)


def test_wikipedia_chinese_falls_back_to_full_query_if_name_empty(monkeypatch):
    from crawl.wikipedia import WikipediaSearch
    from shared import SearchResult

    wiki = WikipediaSearch(delay=0)
    calls = []

    def fake_all(query, num_results):
        calls.append(query)
        if query == "冷门对象":
            return []
        return [
            SearchResult(
                title="仅整句命中",
                url="https://zh.wikipedia.org/?curid=3",
                snippet="后缀",
                source=SearchSource.WIKIPEDIA,
            )
        ]

    monkeypatch.setattr(wiki, "_search_all_langs", fake_all)
    hits = wiki.search("冷门对象 生平 时间线 里程碑", 5)
    assert calls == ["冷门对象", "冷门对象 生平 时间线 里程碑"]
    assert hits[0].title == "仅整句命中"


def test_wikipedia_keeps_hint_hits_that_name_the_person(monkeypatch):
    from crawl.wikipedia import WikipediaSearch
    from shared import SearchResult

    wiki = WikipediaSearch(delay=0)

    def hit(title, curid, snippet=""):
        return SearchResult(
            title=title,
            url=f"https://zh.wikipedia.org/?curid={curid}",
            snippet=snippet,
            source=SearchSource.WIKIPEDIA,
        )

    def fake_all(query, num_results):
        if query == "雷军":
            return [hit("雷军", 1, "小米")]
        if query == '"雷军" 演讲':
            return [
                hit("Are you OK", 9, "源自企业家雷军在印度的营销演讲"),
                hit("李彦宏", 8, "中科大演讲砸场"),
            ]
        return [hit("古龙", 2, "著作")]

    monkeypatch.setattr(wiki, "_search_all_langs", fake_all)
    hits = wiki.search("雷军 演讲 公开课", 5)
    titles = [item.title for item in hits]
    assert titles[0] == "Are you OK"
    assert "雷军" in titles
    assert "李彦宏" not in titles
    assert "古龙" not in titles


def test_mentions_name_folds_traditional():
    from shared import SearchResult

    seed = SearchResult(
        title="張小龍",
        url="https://zh.wikipedia.org/?curid=1",
        snippet="微信",
        source=SearchSource.WIKIPEDIA,
    )
    aliases = name_aliases("张小龙", [seed])
    assert "張小龍" in aliases
    assert mentions_name(seed, "张小龙", aliases)
    other = SearchResult(
        title="古龙",
        url="https://zh.wikipedia.org/?curid=2",
        snippet="武侠著作",
        source=SearchSource.WIKIPEDIA,
    )
    assert mentions_name(other, "张小龙", aliases) is False
    listed = SearchResult(
        title="张茵",
        url="https://zh.wikipedia.org/?curid=4",
        snippet="福布斯：张茵、张近东、雷军",
        source=SearchSource.WIKIPEDIA,
    )
    assert mentions_name(listed, "雷军", ["雷军"]) is False
    commander = SearchResult(
        title="高山下的花环",
        url="https://zh.wikipedia.org/?curid=5",
        snippet="其母把求情电话打到雷军长的指挥所",
        source=SearchSource.WIKIPEDIA,
    )
    assert mentions_name(commander, "雷军", ["雷军"]) is False
    speech = SearchResult(
        title="Are you OK",
        url="https://zh.wikipedia.org/?curid=6",
        snippet="源自企业家雷军在印度的营销演讲",
        source=SearchSource.WIKIPEDIA,
    )
    assert mentions_name(speech, "雷军", ["雷军"]) is True
    merged = merge_hits([other], [seed], 2)
    assert [item.title for item in merged] == ["古龙", "張小龍"]
