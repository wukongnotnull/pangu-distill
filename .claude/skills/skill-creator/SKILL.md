---
name: skill-creator
description: 把已经蒸馏好的 4.5 层模型写成可安装的 Agent Skill。当盘古蒸馏完成蒸馏、进入构建阶段时使用。适用于 Claude Code、Cursor、Codex、OpenClaw 等宿主。
---

# skill-creator

你负责**构建**，不负责重新蒸馏。输入应已包含身份卡、心智模型（含形成故事 / 触发条件 / 推理步骤）、表达 DNA、决策框架、诚实边界。

## 必须做

1. 先跑 `python3 "{pangu_skill_root}/scripts/run.py" output-root` 得到 `{pangu_output_root}`，再按 `{pangu_skill_root}/references/output-spec.md` 建目录：
   `{pangu_output_root}/pangu-[对象]/`
2. 选对模板（均在 `{pangu_skill_root}/references/templates/`）：
   - 人物 → `person-skill-template.md`
   - 内容 → `content-skill-template.md`
   - 思想 → `idea-skill-template.md`
   - 现象 → `phenomenon-skill-template.md`
   - 自我 → `self-skill-template.md`
3. 写入 `SKILL.md`：YAML 头 + 4.5 层 + 工作流 + 验证清单
4. 细节放到 `references/`，例子放到 `examples/`
5. `SKILL.md` 控制在约 500 行，用对象自己的词
6. 确认 `references/distillation/` 里已有 `00-sources.md`、`08-extraction-notes.md`、`09-key-quotes.md`；没有就打回蒸馏，不要空造
7. 写完跑 `python3 "{pangu_skill_root}/scripts/run.py" check "{pangu_output_root}/pangu-[对象]"`，FAIL 为零才交给 skill-vetter；WARN 写进诚实边界
8. 删掉 `references/distillation/ingest_result.json`（含正文全文的工作文件）

## 禁止

- 禁止在构建阶段发明新原则
- 禁止删掉诚实边界来「更好看」
- 禁止删掉形成故事、触发条件
- 禁止把收集到的原文整页粘进 SKILL.md
- 禁止输出超越版 / plus 目录
- 禁止自评保真度（交给 skill-vetter）；禁止在 `README.md` / `SKILL.md` 预写分数，分数只能在 `FIDELITY.md` 产生后回填
- 禁止自己出保真度测试题或碰 `fidelity/`（出题是 skill-vetter 的事，构建者出题会挑软题）
