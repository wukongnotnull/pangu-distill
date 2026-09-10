import pytest

from distill.dimensions import (
    IDEA_DIMENSIONS,
    PERSON_DIMENSIONS,
    PERSON_DIMENSIONS_EN,
    SelfKindError,
    UnknownKindError,
    dimension_file,
    dimension_hint,
    dimension_label,
    dimensions_for,
    normalize_kind,
    query_locale,
)


def test_kind_aliases_and_idea_has_no_biography():
    assert normalize_kind("D3") == "idea"
    assert normalize_kind("思想") == "idea"
    assert normalize_kind(None) == "person"
    idea = dimensions_for("idea")
    assert idea == IDEA_DIMENSIONS
    blob = " ".join(idea.values())
    assert "生平" not in blob
    assert "Twitter" not in blob
    assert "起源" in idea["origins"]


def test_unknown_kind_raises():
    with pytest.raises(UnknownKindError):
        normalize_kind("planet")


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


def test_zh_person_expression_drops_twitter():
    zh = dimensions_for("person", target="张小龙")
    en = dimensions_for("person", target="Jeff Bezos")
    assert "Twitter" not in " ".join(zh.values())
    assert "twitter" in en["expression"]


def test_self_kind_refuses_web_plan():
    with pytest.raises(SelfKindError):
        dimensions_for("self")


def test_every_dimension_has_file_label_hint():
    for kind in ("person", "content", "idea", "phenomenon"):
        for name in dimensions_for(kind):
            assert dimension_file(name).endswith(".md")
            assert not dimension_file(name).startswith("10-"), name
            assert dimension_label(name) != name
            assert dimension_hint(name)
    assert dimension_file("custom") == "10-custom.md"
    assert dimension_file("critics") == dimension_file("assumptions") == "04-limitations.md"
