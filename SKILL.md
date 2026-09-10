---
name: pangu-distill
description: |
  盘古蒸馏：从任意对象提取可运行的思维框架（人物/内容/思想/现象/自我），并生成可激活的 Skill。
  适用于 Claude Code、Cursor、Codex、OpenClaw、Gemini CLI 等能加载 SKILL.md 的宿主。
  入口：蒸馏XX → 澄清、六路采集、七级提取、构建、验证、精炼
  触发词：「蒸馏XX」「帮我蒸馏XX」「做一个XX的思维框架」「蒸馏我自己」「蒸馏这段对话」
  模糊需求触发：「我想做一个领域的方法论」「帮我提炼XX的思维框架」
---

# 盘古蒸馏 · Meta Skill

> 「蒸馏万物，提取可运行的思维框架。」

运行前先解析两个路径，细则见 [host-compatibility.md](references/host-compatibility.md)。

**`{pangu_skill_root}`**：宿主实际加载的这份 `SKILL.md` 所在目录。候选：`PANGU_SKILL_ROOT`、`CLAUDE_SKILL_DIR`、`CODEX_SKILL_DIR`、`CURSOR_SKILL_DIR`、宿主 discovery 给出的路径。不要把 `cwd` 当成 Skill 根目录。

**`{pangu_output_root}`**：当前工作区里这个 Agent 会读的 skills 目录。先跑：

```bash
python3 "{pangu_skill_root}/scripts/run.py" output-root
```

不要写死 `.claude/skills/`。没有已存在的目录时，默认创建 `.agents/skills/`。成品写到 `{pangu_output_root}/pangu-[对象]/`。母体是 `pangu-distill`，产物不要再加 `-distill` 后缀。

脚本和参考文档一律从 `{pangu_skill_root}` 解析。联网搜索用当前宿主的搜索工具，不要写死 WebSearch；脚本不搜索，只做 `plan`（出查询计划）→ `ingest`（落底稿）→ `check`（校验产物）。没有子 Agent 时，构建/评分在同会话分角色，并在 `FIDELITY.md` 标明未独立评分。

---

## 核心理念

盘古蒸馏不是资料摘要。**它是创造其他技能的技能。**

蒸馏是理解：弄清本质、形成故事、触发条件和边界，让 Agent 能按该框架思考与回答。

同类 meta-skill 各自擅长一层。盘古蒸馏把它们压进同一条流水线：

- 4.5 层模型（身份卡 / 心智模型 / 表达 DNA / 决策框架 / **诚实边界**）
- 七级提取（形成故事优先，金句最后）
- 心智模型三重验证 + 触发条件 + 推理步骤
- 六路采集：脚本出计划，宿主搜索，脚本落底稿并校验（`plan` → `ingest` → `check`）
- 独立双 Agent 保真度评分（禁止自评）

详细方法见 [蒸馏方法论](references/distillation-methodology.md)。

---

## 触发词清单

### 明确触发（直接执行）

| 触发词 | 动作 | 说明 |
|--------|------|------|
| 「蒸馏XX」 | **蒸馏** | Phase 0A → 0.5 → 1 → 2 → 3 → 4 |
| 「帮我蒸馏XX」 | 蒸馏 | 同上 |
| 「做一个XX的思维框架」 | 蒸馏 | 同上 |
| 「蒸馏我自己」 | 自我蒸馏 | 见 Phase 0A 第 7 问 + [特殊场景](references/special-scenarios.md) |
| 「蒸馏这段对话 / 这些聊天记录」 | 对话蒸馏 | 以用户材料为一手料，禁止网搜补人格 |

### 模糊触发（先诊断）

| 触发词 | 动作 |
|--------|------|
| 「我想做一个领域的方法论」 | 蒸馏该领域核心思想 |
| 「帮我提炼XX的思维框架」 | 蒸馏 |

进化 / 纠错（已有 Skill 时）：

| 触发词 | 动作 |
|--------|------|
| 「这不对」「他不会这样」「他应该是」 | 进入精炼，保留证据，改框架 |
| 「我有新文件 / 追加」 | 增量采集后重蒸薄弱层 |
| 「更新这个 Skill」 | 走特殊场景「更新已有 Skill」 |

---

## 4.5 层模型

生成的每个 Skill 都必须有这五层。缺诚实边界等于没蒸馏完。

| 层 | 必须包含 |
|----|----------|
| 身份卡 | 第一人称、起点、别人怎么用我 |
| 心智模型 | 3–7 个；每个有形成故事、证据、触发条件、推理步骤、局限 |
| 表达 DNA | 句式指纹 + 禁忌词 + 口癖 |
| 决策框架 | 默认路径、判断句、反模式 |
| 诚实边界 | ≥3 条做不到的事、信息缺口、何时不该用 |

心智模型准入：形成故事 + 三重验证（跨域 / 生成力 / 排他性）。缺一则降级或删除。

---

## 蒸馏对象分类

### D1: 人物类

| 类型 | 示例 | 蒸馏重点 |
|------|------|---------|
| 名人精英 | 芒格、巴菲特、马斯克 | 形成故事、决策复盘、表达 DNA |
| 身边牛人 | 老板 / 导师 / 同事 | 可复用的判断习惯，必须有一手料 |
| 自我蒸馏 | 用户自己 | 真实权重，含自我欺骗 |

### D2: 内容类

| 类型 | 示例 | 蒸馏重点 |
|------|------|---------|
| 书籍 | 《反脆弱》《穷查理宝典》 | 核心理论 + 隐藏假设 + 应用边界 |
| 影视 | 《教父》《黑客帝国》 | 叙事结构 + 角色范式 + 主题隐喻 |
| 课程 / 演讲 | TED、播客 | 论证结构 + 记忆点 |

### D3: 思想类

| 类型 | 示例 | 蒸馏重点 |
|------|------|---------|
| 理论 | 第一性原理、演化论 | 核心机制 + 适用条件 + 反例 |
| 观念 | 「长期主义」「杠杆思维」 | 起源场景 + 失效案例 |
| 学科范式 | 经济学思维 | 公理 + 推导链 + 世界观假设 |

### D4: 现象类

| 类型 | 示例 | 蒸馏重点 |
|------|------|---------|
| 商业 / 社会 / 组织 | 瑞幸增长、内卷、公司文化 | 底层机制 + 偶然因素 + 可复制性 |

### D5: 自我类

用户自己或一段真实对话。重点不是理想人设，而是**行为证据里的决策系统**。模板用 [self-skill-template.md](references/templates/self-skill-template.md)。

---

## 执行流程

### Phase 0: 入口分流

| 用户输入 | 路径 |
|---------|------|
| 蒸馏XX / 做一个XX的思维框架 | Phase 0A → 0.5 → 1 → 2 → 3 → 4 |
| 蒸馏我自己 / 蒸馏这段对话 | Phase 0A（第 7 问必做）→ 本地语料模式 |
| 模糊需求 | Phase 0B |
| 纠错 / 追加 / 更新 | 特殊场景，不重新从零澄清 |

---

### Phase 0A: 七问澄清

用户要求蒸馏时，确认这 7 项。能从上下文直接填的不要再问。

1. **对象是谁**：「XX 是指……？」
2. **类型**：D1 人物 / D2 内容 / D3 思想 / D4 现象 / D5 自我？
3. **聚焦**：全面，还是只蒸决策 / 创业 / 人生哲学？
4. **用途**：思维顾问 / 决策参考 / 方法论 / 角色扮演？
5. **一手资料**：有没有书、PDF、访谈逐字稿、笔记、聊天记录？
6. **深度**：标准六路，还是用户只要快速版（模型减到 2–3 个，诚实边界加大）？
7. **自我 / 对话**：是不是蒸用户自己或这段对话？是 → 关闭纯网搜补人格。

默认：全面蒸馏 + 有一手用一手 + 无一手才网搜。用户只说「做 XX」→ 按默认推进，不必把七问做成问卷。

确认后 → Phase 0.5。

---

### Phase 0B: 需求诊断

最多问 2 轮。用户已经说清 → 直接推荐对象。

| 需求维度 | 典型表达 | 推荐方向 |
|---------|---------|---------|
| 决策与判断 | 「总选错」 | 多元思维、逆向、概率 |
| 表达与写作 | 「复杂说不清」 | 费曼、故事化、类比 |
| 创业与商业 | 「找不到 PMF」 | 第一性原理、杠杆、克制 |
| 教学与传播 | 「讲课没人听」 | 从已知到未知、最少必要知识 |
| 批判思维 | 「看不透本质」 | 证伪、演化、偏差识别 |
| 内容创作 | 「没特色」 | 注意力工程、测试迭代 |
| 人生策略 | 「方向迷茫」 | 长期主义、杠杆、复利 |
| 风险 | 「怕黑天鹅」 | 反脆弱、凸性、尾部 |
| 自我操作系统 | 「我想看清自己」 | D5 自我蒸馏 |

```
用户：我想提升决策能力
盘古蒸馏：主要是商业判断，还是人生/职业选择？
用户：商业上的，要不要做产品、接不接合作
盘古蒸馏：核心是「信息不完整时做商业判断」。可以蒸芒格或张一鸣。你想蒸谁？
```

---

### Phase 0.5: 创建目录

调研前先建目录：

```
{pangu_output_root}/pangu-[object-name]/
├── SKILL.md
├── README.md
├── FIDELITY.md                 # Phase 3 才写
├── examples/
└── references/
    └── distillation/
        ├── 00-sources.md
        ├── 01-writings.md
        ├── 02-conversations.md
        ├── 03-expression-dna.md
        ├── 04-limitations.md
        ├── 05-decisions.md
        ├── 06-timeline.md
        ├── 07-similar-objects.md
        ├── 08-extraction-notes.md
        └── 09-key-quotes.md
```

命名必须是 `pangu-[对象]`。规格见 [output-spec.md](references/output-spec.md)。对象 slug 不能是 `distill`（会和母体撞名）。

检查：

- [ ] 目录已创建
- [ ] 类型 D1–D5 已确认
- [ ] 本地语料模式？采集策略已标记
- [ ] 中国人物：中文一手源优先
- [ ] `{pangu_skill_root}` 已解析，脚本路径可用
- [ ] `{pangu_output_root}` 已用 `scripts/run.py output-root` 探测，不是猜的

---

## Phase 1: 蒸馏

### Step 1.0: 模式判断

| 模式 | 触发 | 策略 |
|------|------|------|
| 纯网络搜索 | 没有本地素材 | `plan` 出六路查询 → 宿主搜索 → `ingest` 落底稿 |
| 本地语料优先 | 用户给了素材 | 先 `collect-local` / `transcribe`，网搜只补缺口 |
| 纯本地语料 | 用户说「只用我给的」或 D5 / 对话蒸馏 | 不网搜补人格，不跑 `plan` |
| 快速版 | 用户只要快 | 模型 2–3 个，边界加大，仍要形成故事 |

一手素材（全书、长访谈原文、本人聊天）质量远高于二手转述。优先用。

采集和分块细则：[research-guide.md](references/research-guide.md)。

---

### Step 1.1: 对象识别

1. 类型（D1–D5）
2. 一句话核心价值
3. 用途场景
4. 有没有一手料

---

### Step 1.2: 信息采集（脚本出计划 → 宿主搜索 → 脚本 ingest → 脚本 check）

六路：著作、访谈、表达、外部评价、决策、时间线 / 同类。另加用户一手料。

搜索由宿主 Agent 自己的搜索工具完成——它比无头爬虫强得多。脚本只做三件确定性的事：出查询计划、把结果落成底稿、校验产物。四步：

**① 出计划（不联网）**

```bash
python3 "{pangu_skill_root}/scripts/run.py" plan "[对象]" --kind [person|content|idea|phenomenon] -o "[skill目录]/references/distillation/"
```

得到 `plan.json`：六路查询、每路要找什么、结果落到哪个文件、黑名单、`results.json` 模板。`--kind` 对应 D1–D4：D3 思想用 `idea`，D4 现象用 `phenomenon`，不要用默认人物维（生平）。对象名没有汉字时（如 `Jeff Bezos`）自动改用英文六路。D5 自我不出计划，只跑 `collect-local`。

**② 宿主搜索**

按 `plan.json` 的每一路查询，用当前宿主的搜索工具搜，每路约 8 条。官方渠道优先；本人第一手优于转述；收最近 12 个月；每条标 URL 和 `primary / secondary / inferred`。黑名单（知乎、百度百科）不收，标题摘要都不点名对象的页丢掉。某一路搜不到就留空，不要用别的维度凑数。结果写成 `[skill目录]/references/distillation/results.json`（格式见 plan 输出）。

**③ 落底稿**

```bash
python3 "{pangu_skill_root}/scripts/run.py" ingest --plan "[skill目录]/references/distillation/plan.json" "[skill目录]/references/distillation/results.json"
```

脚本去重、过黑名单、抓正文，写出 `00-sources.md`（来源清单、一手占比、剔除 / 抓取失败 / 空维度）和 `01–07` 素材底稿（来源表 + 摘录 + 待填的七级提取记录），以及 `ingest_summary.json`。退出码 2 = 0 条可用素材：写进 `00-sources.md`，禁止对着空气写分析。ingest 不覆盖你手写过的文件（写到 `*.ingest.md`）。抓取失败的页用宿主的读网页工具补。

**④ 校验**（Phase 1.5、Phase 2 结束、Phase 3 出厂各跑一次）

```bash
python3 "{pangu_skill_root}/scripts/run.py" check "[skill目录]"                     # 构建中
python3 "{pangu_skill_root}/scripts/run.py" check "[skill目录]" --require-fidelity  # 出厂
```

有本地文件先：

```bash
python3 "{pangu_skill_root}/scripts/run.py" collect-local "[路径...]" -o "[skill目录]/references/distillation/"
```

脚本失败或 0 条写进 `00-sources.md`，不要假装采过。`plan` 和 `check` 只用标准库，没装依赖也能跑。

#### Agent 分工（宿主侧子 Agent；最多 7 个：1 Master + 6 Analysts）

这是宿主 Agent 的分工，不是脚本功能。没有子 Agent 就一个会话按顺序做完。

| Agent | 职责 | 输出 |
|-------|------|------|
| Master 素材收集师 | 按 `plan.json` 搜索，写 `results.json`，跑 `ingest` | `00-sources.md` + `01–07` 底稿 |
| Analyst A | 对话 + 表达 | `02-conversations.md`, `03-expression-dna.md` |
| Analyst B | 批评 + 决策 + 同类 | `04-limitations.md`, `05-decisions.md`, `07-similar-objects.md` |
| Analyst C | 一手资料 / 用户上传 | `01-source-*.md` 或补进 01–02 |
| Analyst D | 七级提取汇总 | `08-extraction-notes.md` |
| Analyst E | 关键原文 + 交叉验证 | `09-key-quotes.md`，矛盾不调和 |
| Analyst F | 失败、沉默、过时假设 | 补进 `04-limitations.md` |

Master Prompt 要点：官方渠道优先；本人第一手优于转述；收最近 12 个月；每条标 URL 和一手/二手/推断；黑名单：知乎、公众号洗稿、百度百科。

Analyst 要点：发现矛盾直接记录；即兴问答优于演讲；失败必须本人承认。

超时：单 Agent 5 分钟无结果就继续，Phase 1.5 标「信息不足」。可用来源 <10 → 降低期望，加大诚实边界。

---

### Step 1.3: 七级提取 + 框架提炼

先按七级清单扫 `08-extraction-notes.md`，再提炼框架。不要先写金句再找证据。

1. 信念形成故事  
2. 真实决策复盘  
3. 本人承认的失败  
4. 内在矛盾  
5. 认知边界  
6. 思维习惯案例  
7. 通用观点（无形成故事则跳过）

然后做三重验证、量化表达 DNA、给每个模型补触发条件和推理步骤。方法见 [蒸馏方法论](references/distillation-methodology.md)。

#### 蒸馏结果结构

```
## [对象] 的思维框架

### 身份卡
**我是谁** / **我的起点** / **我现在在做什么**

### 核心心智模型（3-7）
每个模型：
- 一句话
- 形成故事（没有就不进）
- 证据（≥2 个领域，标出处）
- 触发条件（可判断的信号，不是「相关场景」）
- 推理步骤（别人读完能用）
- 应用 / 局限

### 决策框架
- 默认路径
- 5-10 条启发式（每条有场景 + 案例）
- 反模式（可检查）

### 表达 DNA
句式、词汇、节奏、幽默、确定性、引用习惯、禁忌词

### 内在张力（≥2 对）
不调和

### 诚实边界
做不到什么、信息缺口、调研时间、何时不该用
```

---

### Step 1.4: 局限识别

与蒸馏同步，不要最后补：

```
### 核心局限（≥3）
### 内在矛盾
### 时代适应性（前提在当前环境还成立吗）
### 信息缺口（已获取 vs 待获取）
```

---

### Phase 1.5: 采集质量门

来源数、一手占比、空维度直接读 `ingest_summary.json` / `00-sources.md`，不要凭印象填。

```
┌──────────────┬────────┬────────────────┐
│ 维度         │ 来源数 │ 关键发现       │
│ 著作/对话/表达/他者/决策/时间线 │ │ │
│ 一手占比     │        │ <50% 要写进边界 │
│ 1-4级提取    │        │ ≥10 才过       │
│ 矛盾 / 缺口  │        │                │
└──────────────┴────────┴────────────────┘
```

用户确认 → Phase 2。某维不够 → 补采（再搜，追加到 `results.json`，重跑 `ingest`）。垃圾进垃圾出，这里拦截比 Phase 3 返工便宜。

---

## Phase 2: 构建

交给 `{pangu_skill_root}/.claude/skills/skill-creator/SKILL.md`。构建阶段禁止发明新原则。产物目录用 `{pangu_output_root}`，不要写死 `.claude/skills/`。

模板索引：[templates/README.md](references/templates/README.md)

| 类型 | 模板 |
|------|------|
| D1 | person-skill-template.md |
| D2 | content-skill-template.md |
| D3 | idea-skill-template.md |
| D4 | phenomenon-skill-template.md |
| D5 | self-skill-template.md |

分层：入口在 `SKILL.md`（约 500 行内），细节进 `references/`，例子进 `examples/`。禁止整页粘贴原文。禁止输出超越版 / plus 目录。

构建完成先跑 `run.py check "[skill目录]"`：命名、YAML 头、4.5 层、模型 3–7 个且各有形成故事 / 触发 / 步骤 / 局限、边界 ≥3、张力 ≥2、证据三件套、examples、禁忌词。有 FAIL 不进 Phase 3。

写入生成 Skill 的回答工作流：

| 问题类型 | 行动 |
|---------|------|
| 需要事实 | 先检索再回答 |
| 纯框架 | 直接用心智模型 |
| 混合 | 先拿事实，再用框架 |
| 此人从未表态 | 先说「这是框架推断」，不要伪装成本人立场 |
| 结构性沉默 | 呈现沉默，不要替他折衷 |

---

## Phase 3: 验证

两道门都过才能交付。

### 门 1：三层过程检查

见 [quality-checklist.md](references/quality-checklist.md)

1. 结构：4.5 层 + 目录 + 触发词——`run.py check` 机器查，FAIL 为零才算过  
2. 深度：形成故事、为什么、默认动作、可检查的反模式  
3. 可执行 + 可迁移：没读过原作的人能做完一件真事

### 门 2：独立保真度评分

见 [fidelity-scorecard.md](references/fidelity-scorecard.md)

交给 `{pangu_skill_root}/.claude/skills/skill-vetter/SKILL.md`。答题和评分必须是两个独立会话；宿主不能开子 Agent 时同会话分角色，并写明未独立评分。总分 ≥80，且无维崩溃。写完 `FIDELITY.md` 跑 `run.py check "[skill目录]" --require-fidelity`：分数、维度崩溃、独立性声明由脚本核对。

验证矩阵：

| 测试 | 通过 |
|------|------|
| 3 个已知公开问题 | 方向一致 |
| 1 个 Skill 没写过的新问题 | 能按框架推导 |
| 1 个真实任务 | 能做完，不只有口号 |
| 「何时失效」 | 诚实边界说得清 |

失败 → 回薄弱 Phase。迭代超过 2 次 → 在诚实边界标注薄弱维，交付当前最优，并写明未过线。

---

## Phase 4: 三轮精炼 + 压力测试

验证通过后默认做三轮，不要只改措辞。

**第 1 轮 · 结构**：4.5 层是否齐，模型是否有形成故事和触发条件。  
**第 2 轮 · 使用者**：一个没读过原作的人按 Skill 能否动手；触发词是否覆盖真实说法。  
**第 3 轮 · 压力**：超范围问题、过时前提、自我欺骗（D5）、和已知失败案例对打。

每轮最多改 3–5 处，必须让 Skill「激活即执行」：先做什么、碰到什么停。

改完复跑门 2 和 `check --require-fidelity`。仍 <80 或有 FAIL → 不要宣称完成。

---

## 特殊场景

见 [special-scenarios.md](references/special-scenarios.md)

自我蒸馏、对话蒸馏、已有 Skill、快速变化领域、批量、部分素材、更新、保密、跨文化、一手资料不足。

---

## 示例

- [蒸馏示例：长期主义](references/examples/distillation-example.md)

下面四次实跑用的是旧的 `collect` / `team` 命令（已被 `plan` / `ingest` / `check` 替代），记录保留为负结果证据：

- [实跑评测：第一性原理（2026-09-08）](references/examples/live-test-first-principles.md)
- [实跑评测：贝索斯（2026-09-08）](references/examples/live-test-bezos.md)
- [实跑评测：张小龙（2026-09-08）](references/examples/live-test-zhangxiaolong.md)
- [实跑评测：雷军（2026-09-08）](references/examples/live-test-leijun.md)

---

## 品味守则

| 原则 | 说明 |
|------|------|
| 形成故事先于结论 | 模型已知道他信什么；Skill 要提供他为什么信 |
| 证据先于金句 | 每条原则能追溯到提取记录 |
| 触发条件先于工具箱 | 不知道何时拿起，镜片只是装饰 |
| 保留张力 | 矛盾是特征 |
| 边界比能力更重要 | 写清失效，比写能力更重要 |
| 脚本先于记忆 | 采集走 `plan` → 宿主搜索 → `ingest`，来源清单由脚本落盘，不靠模型记忆 |
| 机器先于自觉 | 结构门跑 `check`，脚本能查的不靠人眼 |
| 独立评分 | 禁止自评自证 |

## 绝不做的事

- 编造原框架没有的内容
- 没有形成故事却写入信念
- 在信息不足时假装完整
- 把矛盾调成单一正确立场
- 把整书塞进 references
- 输出超越版 / plus
- 把产物命名成 `pangu-[对象]-distill`（那是旧格式；母体才是 `pangu-distill`）
- 用赋能、抓手、闭环、对齐、落地当正文

反模式库：[anti-patterns.md](references/anti-patterns.md)

---

## 关于盘古蒸馏

盘古蒸馏是「创造其他技能的技能」。

它不只是复制，更是提炼：从任意对象提取可运行的思维框架。

> 「万物皆可蒸馏。」

---

> 本 Meta Skill 由 [盘古蒸馏](https://github.com/wukongnotnull/pangu-distill) 提供
