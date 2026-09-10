import json
from pathlib import Path

import pytest

from distill.ingest import (
    INGEST_MARKER,
    RESULT_FILENAME,
    SUMMARY_FILENAME,
    coerce_results,
    ingest,
    is_blacklisted,
    normalize_source_type,
    normalize_url,
    _excerpt,
)
from distill.plan import build_plan
from shared import ContentResult


class FakeFetcher:
    def __init__(self, fail_on=()):
        self.fail_on = set(fail_on)
        self.calls = []

    def fetch(self, url):
        self.calls.append(url)
        if url in self.fail_on:
            raise RuntimeError("抓取失败 [x]: 404")
        return ContentResult(url=url, title=f"T:{url}", content=f"这是 {url} 的正文。" * 20, word_count=100)


def test_coerce_results_accepts_common_shapes():
    flat = [{"dimension": "writings", "url": "https://a"}]
    assert coerce_results(flat) == flat
    assert coerce_results({"target": "x", "results": flat}) == flat
    grouped = coerce_results({"dimensions": {"critics": ["https://b", {"url": "https://c", "title": "C"}]}})
    assert grouped == [
        {"dimension": "critics", "url": "https://b"},
        {"dimension": "critics", "url": "https://c", "title": "C"},
    ]
    top = coerce_results({"writings": [{"url": "https://d"}], "note": "ignored"})
    assert top == [{"url": "https://d", "dimension": "writings"}]
    with pytest.raises(ValueError):
        coerce_results({"nothing": "here"})
    with pytest.raises(ValueError):
        coerce_results("text")


def test_normalizers():
    assert normalize_source_type("一手") == "primary"
    assert normalize_source_type("Secondary") == "secondary"
    assert normalize_source_type("推断") == "inferred"
    assert normalize_source_type(None) == "unknown"
    assert normalize_url("https://zh.wikipedia.org/wiki/%E9%9B%B7%E5%86%9B#x") == normalize_url(
        "https://zh.wikipedia.org/wiki/雷军"
    )
    assert normalize_url("https://a.com/p/?utm_source=x") == "https://a.com/p"
    assert is_blacklisted("https://www.zhihu.com/q/1", ["zhihu.com"])
    assert is_blacklisted("https://baike.baidu.com/item/x", ["baike.baidu.com"])
    assert not is_blacklisted("https://mp.weixin.qq.com/s/abc", ["zhihu.com", "baike.baidu.com"])


def test_excerpt_prefers_sentence_lines():
    sentence = "这是一句足够长的话，用来模拟正文段落里真正的论述内容，不是信息框里的碎片。"
    noisy = "\n".join(["雷军", "性别", "男", "出生", "1969"] + [sentence] * 10)
    out = _excerpt(noisy, 400)
    assert "性别" not in out
    assert out.startswith("这是一句")
    short = _excerpt("短\n行", 100)
    assert short == "短\n行"


def _results():
    return [
        {"dimension": "writings", "url": "https://zh.wikipedia.org/wiki/%E9%9B%B7%E5%86%9B", "title": "雷军", "source_type": "secondary"},
        {"dimension": "conversations", "url": "https://zh.wikipedia.org/wiki/雷军", "title": "dup"},
        {"dimension": "conversations", "url": "https://mi.com/talk", "title": "演讲", "source_type": "primary", "note": "2012"},
        {"dimension": "critics", "url": "https://baike.baidu.com/item/雷军"},
        {"dimension": "expression", "url": "https://www.zhihu.com/question/1"},
        {"dimension": "decisions", "url": "https://dead.example/x", "source_type": "primary"},
        {"dimension": "decisions", "url": "not a url"},
        {"url": "https://nodim.example/"},
        {"dimension": "extra", "url": "https://host.example/pre", "source_type": "inferred", "content": "宿主已抓好。" * 10},
    ]


def test_ingest_end_to_end(tmp_path: Path):
    plan = build_plan("雷军", output_dir=tmp_path)
    fetcher = FakeFetcher(fail_on={"https://dead.example/x"})
    summary = ingest(plan, _results(), tmp_path, fetcher=fetcher)

    assert summary.total_input == 9
    assert summary.kept == 4
    assert summary.dropped_blacklist == 2
    assert summary.dropped_invalid == 2
    assert summary.duplicates == 1
    assert summary.fetched_ok == 3
    assert summary.fetch_failed == 1
    assert summary.by_source_type == {"secondary": 1, "primary": 2, "inferred": 1}
    assert summary.by_dimension == {"writings": 1, "conversations": 1, "decisions": 1, "extra": 1}
    assert summary.empty_dimensions == ["expression", "critics", "timeline"]
    assert summary.unknown_dimensions == ["extra"]
    assert summary.success is True
    assert "https://host.example/pre" not in fetcher.calls  # 宿主给了正文就不再抓

    for name in ("00-sources.md", "01-writings.md", "02-conversations.md", "03-expression-dna.md", "10-extra.md"):
        assert (tmp_path / name).is_file(), name
        assert (tmp_path / name).read_text(encoding="utf-8").startswith(INGEST_MARKER)

    sources = (tmp_path / "00-sources.md").read_text(encoding="utf-8")
    assert "黑名单域名 baike.baidu.com" in sources
    assert "重复（已在 writings）" in sources
    assert "https://dead.example/x — 抓取失败" in sources
    assert "一手占比 50%" in sources
    assert "expression、critics、timeline" in sources

    writings = (tmp_path / "01-writings.md").read_text(encoding="utf-8")
    assert "这是 https://zh.wikipedia.org" in writings
    assert "提取记录（待填" in writings
    empty = (tmp_path / "03-expression-dna.md").read_text(encoding="utf-8")
    assert "信息不足" in empty

    result = json.loads((tmp_path / RESULT_FILENAME).read_text(encoding="utf-8"))
    assert len(result["items"]) == 9
    dead = next(i for i in result["items"] if i["url"] == "https://dead.example/x")
    assert dead["fetch_error"].startswith("抓取失败")
    s = json.loads((tmp_path / SUMMARY_FILENAME).read_text(encoding="utf-8"))
    assert s["kept"] == 4 and s["primary_ratio"] == 0.5


def test_ingest_shared_file_gets_multiple_sections(tmp_path: Path):
    plan = build_plan("反脆弱", kind="content", output_dir=tmp_path)
    items = [
        {"dimension": "critics", "url": "https://a.example/1", "source_type": "secondary"},
        {"dimension": "applications", "url": "https://a.example/2", "source_type": "primary"},
        {"dimension": "assumptions", "url": "https://a.example/3", "source_type": "primary"},
    ]
    summary = ingest(plan, items, tmp_path, fetch=False)
    assert summary.fetched_ok == 0 and summary.fetch_failed == 0
    limitations = (tmp_path / "04-limitations.md").read_text(encoding="utf-8")
    assert "## 维度：critics" in limitations
    assert "## 维度：assumptions" in limitations
    decisions = (tmp_path / "05-decisions.md").read_text(encoding="utf-8")
    assert "## 维度：applications" in decisions
    adjacent = (tmp_path / "07-similar-objects.md").read_text(encoding="utf-8")
    assert "信息不足" in adjacent  # 计划里的空维度也写出来
    assert not (tmp_path / "03-expression-dna.md").exists()
    assert not (tmp_path / "06-timeline.md").exists()


def test_ingest_does_not_overwrite_manual_files(tmp_path: Path):
    plan = build_plan("雷军", output_dir=tmp_path)
    manual = tmp_path / "01-writings.md"
    manual.write_text("# 手写的调研记录\n\n人工内容", encoding="utf-8")
    summary = ingest(plan, [{"dimension": "writings", "url": "https://a.example/1", "source_type": "primary"}], tmp_path, fetch=False)
    assert manual.read_text(encoding="utf-8").startswith("# 手写的调研记录")
    assert (tmp_path / "01-writings.ingest.md").is_file()
    assert "01-writings.md" in summary.files_skipped
    assert any("未覆盖" in w for w in summary.warnings)

    # 再跑一次：ingest 自己写的文件可以覆盖
    summary2 = ingest(plan, [{"dimension": "writings", "url": "https://a.example/2", "source_type": "primary"}], tmp_path, fetch=False)
    assert "00-sources.md" not in summary2.files_skipped


def test_ingest_zero_kept_is_failure(tmp_path: Path):
    plan = build_plan("雷军", output_dir=tmp_path)
    summary = ingest(plan, [{"dimension": "writings", "url": "https://zhihu.com/x"}], tmp_path, fetch=False)
    assert summary.success is False
    assert summary.kept == 0
    sources = (tmp_path / "00-sources.md").read_text(encoding="utf-8")
    assert "0 条可用素材" in sources
    assert summary.empty_dimensions == plan.dimensions


def test_ingest_warns_when_nothing_labelled(tmp_path: Path):
    plan = build_plan("雷军", output_dir=tmp_path)
    summary = ingest(plan, [{"dimension": "writings", "url": "https://a.example/1"}], tmp_path, fetch=False)
    assert any("source_type" in w for w in summary.warnings)
