---
name: skill-vetter
description: 审查盘古蒸馏产物。当技能已写出、需要三层验证和独立保真度评分时使用。
---

# skill-vetter

按 `{pangu_skill_root}/references/quality-checklist.md` 做过程门，按 `{pangu_skill_root}/references/fidelity-scorecard.md` 做结果门。不要凭感觉说「写得不错」。

你是**出题 + 评分 Agent**。不要自己答测试题。答题必须由另一个只读该 Skill 目录、禁止联网的 Agent 完成。三方各留一份文件在 `fidelity/`，脚本核对。

## 审查顺序

0. **机器查**：先跑 `python3 "{pangu_skill_root}/scripts/run.py" check "[skill目录]"`，有 FAIL 直接打回，不进入下面的人工审查
1. **结构**：4.5 层、目录、证据三件套（`check` 查不到的：标题对不对内容、证据是不是真证据）
2. **深度**：形成故事、三重验证、触发条件、默认动作、可检查反模式
3. **可执行 + 可迁移**：没读过原作的人能否做完一件真事
4. **出题**：`run.py fidelity init "[skill目录]" --target [对象] --alias 公司名 --alias 产品名`，填 `fidelity/questions.md`（Q1–Q3 立场：公开表态过且 Skill 没写过；Q4 超范围；Q5 真实任务）和 `fidelity/rubric.md`（参考立场 + 出处 + 判定标志）。写完 rubric 再叫答题 Agent，不要反过来
5. **答题**：开新会话，只给 `fidelity/questions.md` 和 Skill 目录路径，禁止联网、禁止看 rubric；它写 `fidelity/answers.md`
6. **遮名**：`run.py fidelity blind "[skill目录]"` → `fidelity/answers.blind.md`
7. **七维评分**：先只读 `answers.blind.md` 写下「像谁、凭什么」→ 再读 answers → 再对 rubric 逐题判 → 最后读 Skill 打来源与结构。写 `FIDELITY.md`，测试记录逐题写 Q1–Q5
8. **精炼建议**：只指出必须改的 3–5 条，写进 `FIDELITY.md` 的「必须改」

## 通过线

- 三层验证全过
- 总分 ≥ 80，七维相加等于总分
- 任何一维不得崩溃（低于该维满分的 40%）
- 写完 `FIDELITY.md` 跑 `check --require-fidelity`，无 FAIL（测试包齐、题目没抄正文、答题声明未联网、rubric 没泄漏、独立性写清）

不通过就打回蒸馏或构建。不要建议「先用着再改」。没有子 Agent 时同会话分角色，仍写全三份文件，`FIDELITY.md` 独立性一栏写「同会话分角色（未独立）」。

## 必须抓的问题

- 没有形成故事的信念
- 触发条件写成「相关场景」
- AI 味（赋能、抓手、闭环、对齐）
- 百科词条（生平压过决策）
- 把观点写成事实
- 没有「什么情况下不该用我」
- 触发词含糊
- 收集了但不蒸馏
- 自评自证；题目抄自正文；答题里出现 rubric 原句
- `README.md` 预写分数（分数只能在 `FIDELITY.md` 产生后回填）
