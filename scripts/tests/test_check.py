import json
from pathlib import Path

import pytest

from distill.check import FAIL, PASS, WARN, parse_fidelity, parse_frontmatter, run_check
from distill import fidelity as fid
from tests.test_fidelity import write_packet

REPO_ROOT = Path(__file__).resolve().parents[2]

MODEL = """### 模型 {n}：示例模型 {n}

**一句话**：一句话。

**形成故事**：某年某地经历了什么，所以信这个。

**证据**：两个领域的出处。

**触发条件**：看到某个可判断的信号。

**推理步骤**：1) 先做 A；2) 再做 B。

**局限**：什么情况下失效。
"""

SKILL_TEMPLATE = """---
name: {name}
description: |
  当用户要用示例的方式看问题，或说「蒸馏示例」「示例会怎么看」时使用。
---

# 示例 · 思维操作系统

## 角色协议

激活后用「我」回答。

## 身份卡

**我是谁**：示例。

## 核心心智模型

{models}

## 表达 DNA

- 句式：短。

## 决策框架

### 默认路径

1. 先看 A。

### 反模式

- 出现赋能/抓手/闭环/对齐就走歪了。

## 内在张力

1. **A vs B**：两边都写。
2. **C vs D**：不调和。

## 栽过的跟头

1. 某次失败。

## 诚实边界

- **做不到**：X。
- **信息缺口**：没有全书精读。
- **何时不该用我**：Y。

## 工作流

需要事实先查。
"""


def make_skill(tmp_path: Path, name="pangu-demo", models=3, fidelity=None, packet=None, **overrides) -> Path:
    skill = tmp_path / name
    dist = skill / "references" / "distillation"
    dist.mkdir(parents=True)
    (skill / "examples").mkdir()
    (skill / "examples" / "one.md").write_text("# 输入 → 输出\n\n问：…\n答：…", encoding="utf-8")
    (skill / "README.md").write_text("# demo\n\n用法。", encoding="utf-8")
    for f in ("00-sources.md", "08-extraction-notes.md", "09-key-quotes.md"):
        (dist / f).write_text(f"# {f}\n\n" + "证据内容。" * 30, encoding="utf-8")
    text = overrides.get("skill_text") or SKILL_TEMPLATE.format(
        name=overrides.get("yaml_name", name),
        models="\n".join(MODEL.format(n=i) for i in range(1, models + 1)),
    )
    (skill / "SKILL.md").write_text(text, encoding="utf-8")
    if fidelity is not None:
        (skill / "FIDELITY.md").write_text(fidelity, encoding="utf-8")
    if packet or (packet is None and fidelity is not None):
        write_packet(skill)
        fid.blind_answers(skill)
    return skill


FIDELITY_OK = """# 保真度评分卡

**总分：87/100 · 等级 A** | 日期：2026-09-08
出题：测试 | 答题：两个独立子 Agent 之一 | 评分：两个独立子 Agent 之二 | 独立性：独立（答题与评分是两个会话）

| 维度 | 得分 | 判定 |
|------|------|------|
| 立场一致性 | 19/20 | Q1 Q2 Q3 |
| 风格辨识度 | 11/15 | |
| 边缘诚实度 | 14/15 | Q4 |
| 来源透明度 | 9/10 | |
| 结构完整度 | 10/10 | |
| 可执行性 | 12/15 | Q5 |
| 可迁移性 | 12/15 | |
"""


def codes(report, level):
    return {f.code for f in report.findings if f.level == level}


def test_parse_frontmatter_block_and_inline():
    meta, body = parse_frontmatter("---\nname: pangu-x\ndescription: |\n  第一行\n  第二行\n---\n# 正文\n")
    assert meta["name"] == "pangu-x"
    assert meta["description"] == "第一行\n第二行"
    assert body.startswith("# 正文")
    meta2, _ = parse_frontmatter("---\nname: a\ndescription: 一句话\n---\n")
    assert meta2["description"] == "一句话"
    assert parse_frontmatter("# 没有头\n") == ({}, "# 没有头\n")


def test_parse_fidelity():
    total, rows, independent = parse_fidelity(FIDELITY_OK)
    assert total == 87
    assert ("立场一致性", 19, 20) in rows
    assert len(rows) == 7
    assert independent is True
    _, _, dep = parse_fidelity("总分：90/100 · 同会话分角色，未独立评分")
    assert dep is False
    _, _, dep2 = parse_fidelity("总分：90/100 · 独立性：同会话分角色（未独立）")
    assert dep2 is False


def test_good_skill_passes_without_fidelity(tmp_path):
    skill = make_skill(tmp_path)
    report = run_check(skill)
    assert report.passed, report.to_text()
    assert report.kind == "person"
    assert "fidelity" in codes(report, WARN)  # Phase 3 前正常
    assert "style" in codes(report, PASS)
    assert "model-parts" in codes(report, PASS)


def test_good_skill_passes_release_gate(tmp_path):
    skill = make_skill(tmp_path, fidelity=FIDELITY_OK)
    report = run_check(skill, require_fidelity=True)
    assert report.passed, report.to_text()
    assert "fidelity" in codes(report, PASS)


def test_release_gate_requires_fidelity(tmp_path):
    skill = make_skill(tmp_path)
    report = run_check(skill, require_fidelity=True)
    assert "fidelity" in codes(report, FAIL)
    assert "fidelity-packet" in codes(report, FAIL)


def test_release_gate_requires_packet_but_build_only_warns(tmp_path):
    skill = make_skill(tmp_path, fidelity=FIDELITY_OK, packet=False)
    building = run_check(skill)
    assert building.passed, building.to_text()
    assert "fidelity-packet" in codes(building, WARN)
    release = run_check(skill, require_fidelity=True)
    assert "fidelity-packet" in codes(release, FAIL)

    write_packet(skill)
    release = run_check(skill, require_fidelity=True)
    assert release.passed, release.to_text()
    assert "fidelity-blind" in codes(release, WARN)
    legacy = FIDELITY_OK.replace("Q1 Q2 Q3", "1 2 3").replace("Q4", "4").replace("Q5", "5")
    (skill / "FIDELITY.md").write_text(legacy, encoding="utf-8")
    assert "fidelity-records" in codes(run_check(skill, require_fidelity=True), FAIL)
    assert "fidelity-records" in codes(run_check(skill), WARN)


def test_low_or_collapsed_fidelity_fails(tmp_path):
    low = FIDELITY_OK.replace("87/100", "72/100")
    assert "fidelity" in codes(run_check(make_skill(tmp_path, "pangu-low", fidelity=low), require_fidelity=True), FAIL)
    collapsed = FIDELITY_OK.replace("| 风格辨识度 | 11/15 |", "| 风格辨识度 | 5/15 |")
    report = run_check(make_skill(tmp_path, "pangu-col", fidelity=collapsed), require_fidelity=True)
    assert "fidelity-dimension" in codes(report, FAIL)
    dependent = FIDELITY_OK.replace("独立性：独立（答题与评分是两个会话）", "独立性：同会话分角色（未独立）")
    report = run_check(make_skill(tmp_path, "pangu-dep", fidelity=dependent))
    assert "fidelity-independent" in codes(report, WARN)
    bad_sum = FIDELITY_OK.replace("| 可迁移性 | 12/15 |", "| 可迁移性 | 14/15 |")
    assert "fidelity-rows" in codes(run_check(make_skill(tmp_path, "pangu-sum", fidelity=bad_sum)), FAIL)


def test_model_count_rules(tmp_path):
    two = run_check(make_skill(tmp_path, "pangu-two", models=2))
    assert "models-count" in codes(two, FAIL)
    quick = run_check(make_skill(tmp_path, "pangu-quick", models=2), quick=True)
    assert "models-count" in codes(quick, WARN) and quick.passed
    eight = run_check(make_skill(tmp_path, "pangu-eight", models=8))
    assert "models-count" in codes(eight, FAIL)


def test_missing_model_parts_and_layers(tmp_path):
    text = SKILL_TEMPLATE.format(name="pangu-broken", models=MODEL.format(n=1).replace("**形成故事**", "**背景**") + MODEL.format(n=2) + MODEL.format(n=3))
    text = text.replace("## 诚实边界", "## 备注")
    report = run_check(make_skill(tmp_path, "pangu-broken", skill_text=text))
    assert not report.passed
    assert "model-parts" in codes(report, FAIL)
    assert "layers" in codes(report, FAIL)
    assert any("诚实边界" in f.message for f in report.failures)


def test_name_and_yaml_mismatch(tmp_path):
    report = run_check(make_skill(tmp_path, "pangu-demo", yaml_name="pangu-other"))
    assert "yaml-name" in codes(report, FAIL)
    report = run_check(make_skill(tmp_path, "pangu-demo-distill"))
    assert "name" in codes(report, FAIL)
    report = run_check(make_skill(tmp_path, "pangu-distill"))
    assert "name" in codes(report, FAIL)


def test_boundaries_and_tensions_counts(tmp_path):
    text = SKILL_TEMPLATE.format(name="pangu-thin", models="\n".join(MODEL.format(n=i) for i in range(1, 4)))
    text = text.replace("- **信息缺口**：没有全书精读。\n- **何时不该用我**：Y。\n", "")
    text = text.replace("2. **C vs D**：不调和。\n", "")
    report = run_check(make_skill(tmp_path, "pangu-thin", skill_text=text))
    assert "boundaries" in codes(report, FAIL)
    assert "tensions" in codes(report, FAIL)


def test_forbidden_words_warn_but_listing_is_ok(tmp_path):
    text = SKILL_TEMPLATE.format(name="pangu-ai", models="\n".join(MODEL.format(n=i) for i in range(1, 4)))
    text = text.replace("**我是谁**：示例。", "**我是谁**：为业务赋能的抓手。")
    report = run_check(make_skill(tmp_path, "pangu-ai", skill_text=text))
    assert "style" in codes(report, WARN)
    msg = next(f.message for f in report.findings if f.code == "style")
    assert "赋能" in msg and "闭环" not in msg  # 反模式那行是在罗列，不算


def test_missing_evidence_examples_readme(tmp_path):
    skill = make_skill(tmp_path)
    (skill / "references" / "distillation" / "09-key-quotes.md").write_text("短", encoding="utf-8")
    (skill / "examples" / "one.md").unlink()
    (skill / "README.md").unlink()
    report = run_check(skill)
    assert {"evidence", "examples", "readme"} <= codes(report, FAIL)


def test_ingest_summary_feeds_warnings(tmp_path):
    skill = make_skill(tmp_path)
    (skill / "references" / "distillation" / "ingest_summary.json").write_text(
        json.dumps({"kept": 10, "primary_ratio": 0.2, "empty_dimensions": ["critics"]}), encoding="utf-8"
    )
    (skill / "references" / "distillation" / "ingest_result.json").write_text("{}", encoding="utf-8")
    report = run_check(skill)
    warns = [f.message for f in report.warnings]
    assert any("一手占比 20%" in m for m in warns)
    assert any("critics" in m for m in warns)
    assert any("ingest_result.json" in m for m in warns)


def test_missing_dir_and_skill_md(tmp_path):
    assert not run_check(tmp_path / "nope").passed
    empty = tmp_path / "pangu-empty"
    empty.mkdir()
    report = run_check(empty)
    assert "skill-md" in codes(report, FAIL)


@pytest.mark.parametrize("name", ["pangu-leijun", "pangu-bezos", "pangu-zhangxiaolong", "pangu-first-principles"])
def test_repo_samples_pass(name):
    skill = REPO_ROOT / ".agents" / "skills" / name
    if not skill.is_dir():
        pytest.skip("样本不在仓库里")
    report = run_check(skill, require_fidelity=True)
    assert report.passed, report.to_text()
