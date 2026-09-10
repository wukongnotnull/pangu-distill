from pathlib import Path

from distill import fidelity as fid


def write_packet(skill: Path, *, target="示例", answers_extra="", rubric_extra="", question_q1=None):
    fid.init_packet(skill, target, aliases=["示例君"], kind="person")
    pdir = fid.packet_dir(skill)
    q = (pdir / fid.QUESTIONS_FILE).read_text(encoding="utf-8")
    q = q.replace("author: TODO（出题 Agent：模型 / 会话）", "author: 出题-测试")
    bodies = {
        "Q1": question_q1 or "一家公司要同时上八个型号覆盖所有价位，你会怎么建议？请写清判断依据。",
        "Q2": "被同行抄袭了外观设计，团队想先在社交媒体上公开指责，你会怎么做？",
        "Q3": "一个两周就能做完的功能，产品经理想排到下个季度再上，你怎么看？",
        "Q4": "请给出锂电池正极材料的配比，以及仓库工人加班的具体法律条款。",
        "Q5": "帮一家新品牌规划三十个城市同一天开线下店的方案，请直接给出可执行步骤。",
    }
    for qid, body in bodies.items():
        q = q.replace(f"## {qid} · {dict(fid.QUESTION_SLOTS)[qid]}\n\nTODO", f"## {qid} · {dict(fid.QUESTION_SLOTS)[qid]}\n\n{body}")
    (pdir / fid.QUESTIONS_FILE).write_text(q, encoding="utf-8")

    r = (pdir / fid.RUBRIC_FILE).read_text(encoding="utf-8")
    r = r.replace("TODO", "参考立场：只做一款才是自信，先砍到一款再说" + rubric_extra)
    (pdir / fid.RUBRIC_FILE).write_text(r, encoding="utf-8")

    a = (pdir / fid.ANSWERS_FILE).read_text(encoding="utf-8")
    a = a.replace("answerer: TODO（答题 Agent：模型 / 会话）", "answerer: 答题-测试")
    a = a.replace("date: ", "date: 2026-")
    for qid in bodies:
        a = a.replace(
            f"## {qid}\n\nTODO",
            f"## {qid}\n\n我是示例。这里是对 {qid} 的完整回答，按 Skill 的模型一步一步推，先看信号再给默认动作，最后写局限。" + answers_extra,
        )
    (pdir / fid.ANSWERS_FILE).write_text(a, encoding="utf-8")
    return pdir


def make_skill(tmp_path: Path, name="pangu-demo", extra_skill_text="") -> Path:
    skill = tmp_path / name
    (skill / "examples").mkdir(parents=True)
    (skill / "SKILL.md").write_text(
        "---\nname: pangu-demo\n---\n# 示例 · 思维操作系统\n\n## 核心心智模型\n\n### 模型 1\n\n专注一款。\n" + extra_skill_text,
        encoding="utf-8",
    )
    (skill / "examples" / "one.md").write_text("# 输入 → 输出\n\n问：要不要做十个型号？\n答：不。", encoding="utf-8")
    return skill


def levels(findings, level):
    return [f for f in findings if f.level == level]


def test_init_writes_three_templates_and_does_not_overwrite(tmp_path):
    skill = make_skill(tmp_path)
    written, skipped = fid.init_packet(skill, "示例", aliases=["示例君", "Demo"], kind="person")
    assert {p.name for p in written} == {fid.QUESTIONS_FILE, fid.RUBRIC_FILE, fid.ANSWERS_FILE}
    text = (fid.packet_dir(skill) / fid.QUESTIONS_FILE).read_text(encoding="utf-8")
    assert "target: 示例" in text and "aliases: 示例君, Demo" in text
    assert all(f"## {q} · {k}" in text for q, k in fid.QUESTION_SLOTS)

    (fid.packet_dir(skill) / fid.ANSWERS_FILE).write_text("手写", encoding="utf-8")
    written2, skipped2 = fid.init_packet(skill, "示例")
    assert not written2 and len(skipped2) == 3
    assert (fid.packet_dir(skill) / fid.ANSWERS_FILE).read_text(encoding="utf-8") == "手写"


def test_parse_questions_and_answers():
    q = fid.parse_questions("---\ntarget: 雷军\naliases: 雷总, Lei Jun\n---\n## Q1 · 立场\n\n题一题一题一题一题一题一\n\n## Q4 · 超范围\n\nTODO\n")
    assert q.target == "雷军" and q.aliases == ["雷总", "Lei Jun"]
    assert q.items["Q1"].kind == "立场" and q.items["Q1"].filled
    assert q.items["Q4"].kind == "超范围" and not q.items["Q4"].filled

    a = fid.parse_answers("---\nanswerer: gpt\nnetwork: none\n---\n## Q1\n\n答\n## Q2\n\n答二\n")
    assert a.network_declared_off and a.answerer == "gpt"
    assert set(a.items) == {"Q1", "Q2"}
    assert not fid.parse_answers("---\nnetwork: yes\n---\n").network_declared_off


def test_full_packet_passes_inspection(tmp_path):
    skill = make_skill(tmp_path)
    write_packet(skill)
    findings = fid.inspect_packet(skill)
    assert not levels(findings, "FAIL"), [f.message for f in findings]
    assert any(f.code == "fidelity-blind" for f in levels(findings, "WARN"))  # 还没 blind

    out, count, names = fid.blind_answers(skill)
    assert out.name == fid.BLIND_FILE
    assert count >= 5  # 每题一个「示例」
    blind = out.read_text(encoding="utf-8")
    assert "示例" not in blind.split("---", 2)[2] or "〔X〕" in blind
    assert fid.MASK in blind
    findings = fid.inspect_packet(skill)
    assert not any(f.code == "fidelity-blind" for f in findings)


def test_question_copied_from_skill_fails(tmp_path):
    copied = "被同行抄袭了外观设计，团队想先在社交媒体上公开指责，你会怎么做？"
    skill = make_skill(tmp_path, extra_skill_text=f"\n## 决策框架\n\n{copied}\n")
    write_packet(skill, question_q1=copied)
    findings = fid.inspect_packet(skill)
    fails = [f.message for f in levels(findings, "FAIL")]
    assert any("Q1" in m and "重合" in m for m in fails), fails


def test_unfilled_packet_and_missing_declarations_fail(tmp_path):
    skill = make_skill(tmp_path)
    fid.init_packet(skill, "示例")
    findings = fid.inspect_packet(skill)
    msgs = [f.message for f in levels(findings, "FAIL")]
    assert any("TODO" in m and "Q1" in m for m in msgs)
    assert any("answerer" in m for m in msgs)
    assert any("rubric.md" in m for m in msgs)


def test_rubric_leak_into_answers_warns(tmp_path):
    skill = make_skill(tmp_path)
    secret = "这是评分依据里才有的一句参考立场原文，答题不该见到它"
    write_packet(skill, rubric_extra="\n- 备注：" + secret, answers_extra=secret)
    findings = fid.inspect_packet(skill)
    assert any(f.code == "fidelity-leak" for f in levels(findings, "WARN"))


def test_missing_packet_dir_fails(tmp_path):
    skill = make_skill(tmp_path)
    findings = fid.inspect_packet(skill)
    assert levels(findings, "FAIL")[0].code == "fidelity-packet"


CARD = """# 保真度评分卡 · 示例

**总分：87/100 · 等级 A** | 日期：2026-09-10
出题：A | 答题：B | 评分：C | 独立性：独立（答题与评分是两个会话）

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


def test_scorecard_arithmetic_and_fields():
    ok = fid.inspect_scorecard(CARD)
    assert not levels(ok, "FAIL"), [f.message for f in ok]
    card = fid.parse_scorecard(CARD)
    assert card.total == 87 and card.grade == "A" and card.row_sum == 87
    assert card.independence.startswith("独立")
    assert card.question_refs == {"Q1", "Q2", "Q3", "Q4", "Q5"}
    assert card.roles == {"出题": "A", "答题": "B", "评分": "C"}

    bad_sum = fid.inspect_scorecard(CARD.replace("19/20", "15/20"))
    assert any("相加" in f.message for f in levels(bad_sum, "FAIL"))

    bad_full = fid.inspect_scorecard(CARD.replace("9/10", "9/15"))
    assert any("满分" in f.message for f in levels(bad_full, "FAIL"))

    missing_dim = fid.inspect_scorecard(CARD.replace("| 可迁移性 | 12/15 | |\n", ""))
    assert any("缺维度" in f.message for f in levels(missing_dim, "FAIL"))

    wrong_grade = fid.inspect_scorecard(CARD.replace("等级 A", "等级 B"))
    assert any("等级" in f.message for f in levels(wrong_grade, "WARN"))

    dependent = fid.inspect_scorecard(CARD.replace("独立性：独立（答题与评分是两个会话）", "独立性：同会话分角色（未独立）"))
    assert any(f.code == "fidelity-independent" for f in levels(dependent, "WARN"))
    three = fid.inspect_scorecard(CARD.replace("独立性：独立（答题与评分是两个会话）", "独立性：独立（出题、答题、评分是三个不同会话）"))
    assert not any(f.code == "fidelity-independent" for f in levels(three, "WARN"))
    assert fid.parse_scorecard("独立性：同一个 Agent 分角色").declared_independent is False

    no_refs = fid.inspect_scorecard(CARD.replace("Q1 Q2 Q3", "").replace("Q4", "").replace("Q5", ""))
    assert any(f.code == "fidelity-records" for f in levels(no_refs, "FAIL"))
    assert not any(f.code == "fidelity-records" for f in fid.inspect_scorecard(CARD.replace("Q5", ""), packet_present=False))


def test_mask_names_longest_first():
    text, n = fid.mask_names("雷军说：雷总不是我。Lei Jun 也是我。", ["雷军", "雷总", "Lei Jun"])
    assert n == 3 and "雷" not in text and "lei" not in text.lower()
    assert fid.grade_for(90) == "A" and fid.grade_for(80) == "B" and fid.grade_for(60) == "C" and fid.grade_for(10) == "D"
