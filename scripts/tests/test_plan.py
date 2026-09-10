import json
from pathlib import Path

import pytest

from distill.dimensions import SelfKindError
from distill.plan import PLAN_FILENAME, build_plan, load_plan, parse_dimension_args


def test_build_plan_person_zh():
    plan = build_plan("雷军", kind="person", num_results=5)
    assert plan.kind == "person"
    assert plan.locale == "zh"
    assert plan.dimensions == ["writings", "conversations", "expression", "critics", "decisions", "timeline"]
    q = plan.query_for("writings")
    assert q.query.startswith("雷军 ")
    assert q.file == "01-writings.md"
    assert plan.num_results == 5
    assert "zhihu.com" in plan.blacklist


def test_build_plan_idea_en_and_kind_alias():
    plan = build_plan("First Principles", kind="D3")
    assert plan.kind == "idea"
    assert plan.locale == "en"
    assert "origins" in plan.dimensions
    assert "timeline" not in plan.dimensions
    assert plan.query_for("origins").file == "06-timeline.md"


def test_build_plan_rejects_self_and_empty():
    with pytest.raises(SelfKindError):
        build_plan("我", kind="self")
    with pytest.raises(ValueError):
        build_plan("   ")


def test_plan_save_load_roundtrip(tmp_path: Path):
    plan = build_plan("雷军", output_dir=tmp_path)
    path = plan.save(tmp_path)
    assert path == tmp_path / PLAN_FILENAME
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["target"] == "雷军"
    assert data["results_template"]["results"][0]["dimension"] == "writings"
    assert any("宿主" in step for step in data["instructions"])

    loaded = load_plan(path)
    assert loaded.target == plan.target
    assert loaded.dimensions == plan.dimensions
    assert loaded.query_for("critics").query == plan.query_for("critics").query
    assert loaded.output_dir == str(tmp_path)


def test_plan_markdown_lists_every_query():
    plan = build_plan("张小龙")
    md = plan.to_markdown()
    for q in plan.queries:
        assert q.query in md
        assert q.file in md
    assert "results.json" in md


def test_parse_dimension_args_overrides():
    dims = parse_dimension_args(["books:{target} 书", "podcasts"], "芒格")
    assert dims == {"books": "{target} 书", "podcasts": "{target} podcasts"}
    plan = build_plan("芒格", dimensions=dims)
    assert plan.dimensions == ["books", "podcasts"]
    assert plan.query_for("books").query == "芒格 书"
    assert plan.query_for("podcasts").file == "10-podcasts.md"
    assert parse_dimension_args(None, "x") is None
