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
            ✓ 脚本六路采集（著作/访谈/表达/批评/决策/时间线）
            ✓ 七级提取：形成故事 + 决策复盘 + 失败 + 矛盾
            ✓ 4.5 层通过三重验证
            ✓ 独立保真度评分 ≥ 80

            产出：pangu-long-termism-distill

            心智模型（带形成故事 / 触发条件）：
            ① 复利只奖励待得住的人
            ② 报价不是信息
            ③ 坚持 ≠ 不改地图（降为启发式）

            诚实边界：没有缓冲时谈十年是自欺；思想蒸馏 ≠ 巴菲特本人
```

---

## 快速安装

同一份 `SKILL.md` 可在 Claude Code、Cursor、Codex、OpenClaw、Gemini CLI 等宿主上跑。差别只是发现目录。完整对照见 [references/host-compatibility.md](references/host-compatibility.md)。

### 方式一：跨宿主（推荐）

克隆后软链到各 Agent 的 skills 目录：

```bash
git clone https://github.com/wukongnotnull/pangu-distill.git
cd pangu-distill
bash scripts/install-host.sh              # 用户级：Claude + Codex + ~/.agents/skills
bash scripts/install-host.sh --project    # 当前项目：.agents/skills（Cursor / Codex）
```

只装一家：

```bash
bash scripts/install-host.sh --host openclaw
bash scripts/install-host.sh --host cursor --project
```

装好后重启或重新扫描 Agent。

### 方式二：Claude Code（npx）

```bash
npx skills add wukongnotnull/pangu-distill
```

这条通常只进 `~/.claude/skills/`。其他宿主请用方式一。

安装完成后，在 Agent 的对话框中说：

```markdown
> 蒸馏「长期主义」
> 做一个巴菲特的思维框架
> 蒸馏我自己
> 蒸馏这段对话
```

### 方式三：文科生（对话式）

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
| 采集 | **六路 + 一手料**，强制跑 `scripts/run.py`（搜索 / 爬取 / 转录），不是只靠模型记忆 |
| 质检 | 三层过程门 + **独立双 Agent 保真度评分**（≥80，禁止自评） |
| 精炼 | 三轮：结构 → 使用者 → 压力测试 |

### 执行流程

澄清（七问）→ 建目录 → 采集（脚本 + 最多 7 Agent）→ 七级提取 → 构建 → 验证 → 三轮精炼。

采集默认六路：著作 / 访谈 / 表达 / 批评 / 决策 / 时间线。思想 / 现象请加 `--kind idea` 或 `--kind phenomenon`，不要用人物维。用户给了书、逐字稿、聊天记录时，一手料优先，网搜只补缺口。脚本 0 条必须失败并改用宿主搜索。

每个心智模型必须同时有：形成故事、跨域证据、触发条件、推理步骤、局限。

### 质量验证

过程门走 `references/quality-checklist.md`。出厂走 `references/fidelity-scorecard.md`：答题 Agent 和评分 Agent 必须分开。总分 ≥80 才交付。

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
    ├── install-host.sh                   # 软链到各宿主 skills 目录
    ├── run.py                            # 采集 + output-root / skill-root
    ├── search/ crawl/ transcribe/
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
