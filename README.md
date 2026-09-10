<div align="center">

# 盘古蒸馏.meta-skill

<br>

> **蒸馏万物，提取可运行的思维框架** <br>

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-orange.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![Skills](https://img.shields.io/badge/skills.sh-Compatible-green)](https://skills.sh)

<br>

**盘古（创世大神），开天辟地后觉天地孤寂，** <br>
**用泥沙黄泥捏人，吹气后泥人成活，** <br>
**结果：泥人主宰世界。**

<br>

吸收 [Distilly / 同事](https://github.com/titanwings/distilly)、[女娲](https://github.com/alchaincyf/nuwa-skill)、[仓颉](https://github.com/Yeadon8888/cangjie-skill) 的长处，补上它们缺的层。<br>
 **盘古蒸馏.meta-skill** 从任意对象提取**可运行的思维框架**。

---

**快捷导航**

[使用演示](#使用演示) | [快速安装](#快速安装) | [经典案例](#经典案例) | [架构原理](#架构原理) | [仓库结构](#仓库结构) | [关于我](#关于我)

<br>

**多国语言**

[English](README_EN.md) · [日本語](README_JA.md) · [한국어](README_KO.md) · [Español](README_ES.md)

<br>


</div>

---

## 使用演示

蒸馏长期主义，提取的不只是"坚持"二字，而是可运行的认知框架：

```
用户      ❯ 蒸馏「长期主义」

盘古蒸馏  ❯ 【蒸馏执行中】
            ✓ 七问澄清（思想类 / 决策用途 / 无一手料）
            ✓ 六路采集：plan 出查询 → 宿主搜索 → ingest 落底稿（著作/访谈/表达/批评/决策/时间线）
            ✓ 七级提取：形成故事 + 决策复盘 + 失败 + 矛盾
            ✓ 4.5 层通过三重验证；check 无 FAIL
            ✓ 独立保真度评分 ≥ 80

            产出：pangu-long-termism

            心智模型（带形成故事 / 触发条件）：
            ① 复利只奖励待得住的人
            ② 报价不是信息
            ③ 坚持 ≠ 不改地图（降为启发式）

            诚实边界：没有缓冲时谈十年是自欺；思想蒸馏 ≠ 巴菲特本人
```

---

## 快速安装

### 技术人员

同一份 `SKILL.md` 可在 Claude Code、Cursor、Codex、OpenClaw、Gemini CLI 等宿主上跑。差别只是发现目录。完整对照见 [references/host-compatibility.md](references/host-compatibility.md)。

```bash
npx skills add wukongnotnull/pangu-distill
```

装好后重启或重新扫描 Agent。

安装完成后，在 Agent 的对话框中说：

```markdown
> 蒸馏「长期主义」
> 做一个巴菲特的思维框架
> 蒸馏我自己
> 蒸馏这段对话
```

### 文科生（对话式）

不需要记命令，直接把下面这段话复制给 Agent：

```
帮我安装这个 skill：https://github.com/wukongnotnull/pangu-distill
```

安装完成后，用自然语言告诉它你想要什么：

```markdown
> 帮我蒸馏：长期主义
> 我想做一个巴菲特的思维框架
> 蒸馏我自己
```

## 经典案例

以下 13 位人物是规划中的蒸馏案例，成品 Skill **尚未发布**：

### 💰 投资/商业

| 人物 | 方向 | 状态 |
|------|---------|------------------|
| **纳瓦尔** | 财富/杠杆/人生哲学 | 尚未发布 |
| **芒格** | 投资/多元思维/逆向思考 | 尚未发布 |
| **张雪峰** | 教育/职业规划/阶层流动 | 尚未发布 |

### 🚀 创业/产品

| 人物 | 方向 | 状态 |
|------|---------|------------------|
| **Paul Graham** | 创业/写作/产品/人生哲学 | 尚未发布 |
| **张一鸣** | 产品/组织/全球化/人才 | 尚未发布 |
| **乔布斯** | 产品/设计/战略 | 尚未发布 |
| **马斯克** | 工程/成本/第一性原理 | 尚未发布 |

### 🤖 AI/技术

| 人物 | 方向 | 状态 |
|------|---------|------------------|
| **Karpathy** | AI/工程/教育/开源 | 尚未发布 |
| **Ilya Sutskever** | AI安全/scaling/研究品味 | 尚未发布 |

### 🎬 内容创作

| 人物 | 方向 | 状态 |
|------|---------|------------------|
| **MrBeast** | 内容创造/YouTube方法论 | 尚未发布 |

### 🎯 传播/权力

| 人物 | 方向 | 状态 |
|------|---------|------------------|
| 🔥**特朗普** | 谈判/权力/传播/行为预判 | 尚未发布 |

### 🧠 思维/学习

| 人物 | 方向 | 状态 |
|------|---------|------------------|
| **费曼** | 学习/教学/科学思维 | 尚未发布 |
| **塔勒布** | 风险/反脆弱/不确定性 | 尚未发布 |

---

## 架构原理

### 核心能力

从任意对象提取可运行的思维框架，产出人物 / 内容 / 思想 / 现象 / **自我** Skill。

合成了同类仓库真正提高保真度的部分，并补上它们缺的层：

| 层 | 盘古蒸馏 |
|----|----------|
| 框架 | **4.5 层**：身份卡 / 心智模型 / 表达 DNA / 决策框架 / **诚实边界**（边界不是附录） |
| 提取 | **七级提取**：形成故事优先，金句最后；没有「为什么信」不准进 Skill |
| 验证 | 三重验证（跨域 / 生成力 / 排他性）+ **触发条件** + **推理步骤** |
| 采集 | **六路 + 一手料**：`scripts/run.py plan` 出查询计划 → 宿主 Agent 用自己的搜索工具搜 → `ingest` 去重 / 黑名单 / 抓正文落底稿。来源清单由脚本落盘，不靠模型记忆 |
| 质检 | `scripts/run.py check` 机器查结构（命名 / 4.5 层 / 证据三件套 / FIDELITY / 测试包）+ 三层过程门 + **出题 / 答题 / 评分三方分离的保真度评分**（≥80，测试包入库，禁止自评） |
| 精炼 | 三轮：结构 → 使用者 → 压力测试 |

### 执行流程

澄清（七问）→ 建目录 → 采集（`plan` → 宿主搜索 → `ingest`）→ 七级提取 → 构建 → `check` → 验证 → 三轮精炼。

采集默认六路：著作 / 访谈 / 表达 / 批评 / 决策 / 时间线。思想 / 现象请加 `--kind idea` 或 `--kind phenomenon`，不要用人物维。用户给了书、逐字稿、聊天记录时，一手料优先，网搜只补缺口。搜索由宿主 Agent 完成——它的联网工具远强于无头爬虫；脚本只做确定性的事：出计划、落底稿、校验。`ingest` 0 条即失败，不许对着空气写分析。

```bash
python3 scripts/run.py plan "雷军" --kind person -o out/references/distillation/   # 出六路查询 + results.json 模板
# …宿主 Agent 按 plan.json 搜索，写 out/references/distillation/results.json…
python3 scripts/run.py ingest --plan out/references/distillation/plan.json out/references/distillation/results.json
python3 scripts/run.py check out/                                                  # 构建后
python3 scripts/run.py fidelity init out/ --target 芒格 --alias 伯克希尔              # 出题模板
python3 scripts/run.py fidelity blind out/                                         # 答题后遮名
python3 scripts/run.py check out/ --require-fidelity                               # 出厂
```

每个心智模型必须同时有：形成故事、跨域证据、触发条件、推理步骤、局限。

### 质量验证

结构门跑 `scripts/run.py check`：命名、YAML 头、4.5 层、模型 3–7 个且各有形成故事 / 触发 / 步骤 / 局限、边界 ≥3、张力 ≥2、证据三件套、禁忌词、FIDELITY 分数与维度崩溃。过程门走 `references/quality-checklist.md`。出厂走 `references/fidelity-scorecard.md`：出题、答题、评分三个会话分开，题目 / rubric / 答题 / 盲读稿留在产物的 `fidelity/` 里，脚本核对题目没抄正文、答题未联网、分数相加、独立性声明。总分 ≥80 且 `check --require-fidelity` 无 FAIL 才交付。仓库里四个早期样本产物都按此协议重评过；`.agents/skills/pangu-munger/` 是用新流水线从零跑完的样本，过程记录在 `references/examples/live-test-munger.md`。

---

## 仓库结构

```
pangu-distill/
├── SKILL.md                              # 盘古蒸馏本体（各宿主共用）
├── .agents/skills/                       # 跨宿主默认产出位置说明
├── .claude/skills/
│   ├── skill-creator/                    # 构建子智能体
│   └── skill-vetter/                     # 独立审查子智能体
├── references/
│   ├── host-compatibility.md             # 各 Agent 安装与路径
│   ├── distillation-methodology.md       # 4.5 层 + 七级提取
│   ├── research-guide.md                 # 六路采集与证据格式
│   ├── quality-checklist.md              # 三层过程门
│   ├── fidelity-scorecard.md             # 独立保真度评分
│   ├── output-spec.md                    # 产物规格
│   ├── anti-patterns.md                  # 反模式库
│   ├── special-scenarios.md              # 自我/对话/保密等
│   ├── examples/distillation-example.md
│   └── templates/                        # 人物/内容/思想/现象/自我
└── scripts/
    ├── run.py                            # plan / ingest / check / collect-local / transcribe / output-root
    ├── distill/                          # plan.py / ingest.py / check.py / fidelity.py / local.py / dimensions.py
    ├── crawl/                            # 正文抓取 + DuckDuckGo / 维基保底搜索
    └── transcribe/
```

---

## 关于我

**悟空非空也** — AI之道创始人，独立开发者，Up主。

| 平台         | 链接                                                                         |
| ------------ | ---------------------------------------------------------------------------- |
| 🌐  官网      | [AI之道官网](https://waytoai.cn)                                                |
| 𝕏  Twitter   | [悟空非空也](https://x.com/wukongnotnull)                                   |
| 📺  B站       | [悟空非空也](https://space.bilibili.com/456634391)                              |
| ▶️  YouTube   | [悟空非空也](https://www.youtube.com/@wukongnotnull)                        |
| 📕  小红书    | [悟空非空也](https://www.xiaohongshu.com/user/profile/5ca89c2f000000001100952b) |
| 💬  公众号    | 微信搜「悟空非空也」或扫码关注 ↓                                            |

<img src="./images/wechat-qrcode.jpg" alt="公众号二维码" width="360">

---

<div align="center">

Apache-2.0 license © [悟空非空也](https://github.com/wukongnotnull)

</div>
