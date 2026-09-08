import pytest

from crawl.base import BlockedError
from crawl.duckduckgo import DuckDuckGoSearch
from crawl.wikipedia import strip_wiki_markup
from search.dimensions import (
    IDEA_DIMENSIONS,
    SelfKindError,
    dimensions_for,
    normalize_kind,
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
