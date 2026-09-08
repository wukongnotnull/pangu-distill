<div align="center">

# pangu-distill.meta-skill

<br>

> **Distill everything into runnable thinking frameworks** <br>

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-orange.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![Skills](https://img.shields.io/badge/skills.sh-Compatible-green)](https://skills.sh)

<br>

**Pangu (the Creator), after opening up the heavens and earth, felt the world was lonely,** <br>
**So he molded people from yellow mud, breathed life into them,** <br>
**Result: Mud people now dominate the world.**

<br>

Inspired by [colleague.skill](https://github.com/titanwings/colleague-skill) and [Nuwa.skill](https://github.com/titanwings/colleague-skill), distilling thinking frameworks from famous figures, departed ones, and elites.
<br>
 **pangu-distill.meta-skill** extracts **runnable thinking frameworks** from any subject.

---

**Quick Navigation**

[Demo](#demo) | [Quick Install](#quick-install) | [Classic Cases](#classic-cases) | [Architecture](#architecture) | [Repository Structure](#repository-structure) | [About Me](#about-me)

<br>

**Other Languages**

[中文](README.md) · [日本語](README_JA.md) · [한국어](README_KO.md) · [Español](README_ES.md)

<br>


</div>

---

## Demo

Distilling long-termism extracts not just "persistence," but a runnable cognitive framework:

```
User      ❯ Distill "Long-Termism"

Pangu     ❯ 【Phase 1 in progress】
            ✓ Six-stream collection complete (writings/interviews/criticism/decisions/timeline/similars)
            ✓ Mental model triple verification passed
            ✓ Distillation complete

            Output: "Long-Termism · Thinking Framework"

            Core Mental Models:
            ① Compound thinking: persist as a friend of time, enjoy exponential growth
            ② Long-term focus: ignore short-term fluctuations, concentrate on long-term value
            ③ Perseverance: don't give up during difficult times

            Expression DNA:
            - High certainty: "obviously," "must," "undoubtedly"
            - Few turns of phrase, rarely use "but"
            - Catchphrases: "friend of time," "slow is fast"
```

---

## Quick Install

### Method 1: Technical Users (Command Line)

Install directly with npx:

```bash
npx skills add wukongnotnull/pangu-distill
```

After installation, say this to your Agent:

```markdown
> Distill "Long-Termism"
> I want to build a Buffett thinking framework
```

### Method 2: Non-Technical Users (Conversational)

No commands to remember — just copy and paste this to your Agent:

```
help me to install this skill：https://github.com/wukongnotnull/pangu-distill
```

After installation, tell it what you want in natural language:

```markdown
> Help me distill: long-termism
> I want to build a Buffett thinking framework
```

## Classic Cases

These 13 figures are planned distillation cases. The finished Skills are **not yet published**:

### 💰 Investment / Business

| Person | Domain | Status |
|------|---------|------------------|
| **Naval** | Wealth / Leverage / Life Philosophy | Not yet published |
| **Munger** | Investment / Mental Models / Inversion | Not yet published |
| **Zhang Xuefeng** | Education / Career Planning / Class Mobility | Not yet published |

### 🚀 Startup / Product

| Person | Domain | Status |
|------|---------|------------------|
| **Paul Graham** | Startups / Writing / Product / Life Philosophy | Not yet published |
| **Zhang Yiming** | Product / Organization / Globalization / Talent | Not yet published |
| **Steve Jobs** | Product / Design / Strategy | Not yet published |
| **Elon Musk** | Engineering / Cost / First Principles | Not yet published |

### 🤖 AI / Tech

| Person | Domain | Status |
|------|---------|------------------|
| **Karpathy** | AI / Engineering / Education / Open Source | Not yet published |
| **Ilya Sutskever** | AI Safety / Scaling / Research Taste | Not yet published |

### 🎬 Content Creation

| Person | Domain | Status |
|------|---------|------------------|
| **MrBeast** | Content Creation / YouTube Methodology | Not yet published |

### 🎯 Communication / Power

| Person | Domain | Status |
|------|---------|------------------|
| 🔥**Trump** | Negotiation / Power / Communication / Behavior Prediction | Not yet published |

### 🧠 Thinking / Learning

| Person | Domain | Status |
|------|---------|------------------|
| **Feynman** | Learning / Teaching / Scientific Thinking | Not yet published |
| **Taleb** | Risk / Anti-Fragility / Uncertainty | Not yet published |

---

## Architecture

### Core Capability

Extract runnable thinking frameworks from any subject, producing Person / Content / Idea / Phenomenon Skills.

### Execution Flow

#### Phase 1: Distillation

**Step 1: Information Collection**

3 Agents collect in parallel (master-slave mode):

| Agent | Responsibility | Output File |
|-------|------|---------|
| Master (Material Collector) | Core writings + Timeline | `01-writings.md`, `06-timeline.md` |
| Analyst A | Podcasts/Interviews + Expression DNA | `02-conversations.md`, `03-expression-dna.md` |
| Analyst B | Criticism + Major Decisions + Similars | `04-limitations.md`, `05-decisions.md`, `07-similar-objects.md` |

**Step 2: Framework Extraction**

- **Mental Model Triple Verification**:
  - Verification 1: Cross-domain reproduction (≥2 different fields)
  - Verification 2: Generative power (can infer positions on new questions)
  - Verification 3: Exclusivity (not what every smart person would think)
  - Pass all 3 → Mental model; Pass 1-2 → Decision heuristic

- **Expression DNA Quantification**: Sentence fingerprints, style labels, taboo words and catchphrases

- **Contradiction Handling**: Temporal contradictions → record evolution trajectory; Domain contradictions → record by field; Essential tensions → explicitly define as core tensions

**Step 3: Skill Construction**

3-7 mental models + 5-10 decision heuristics + Expression DNA + Values & Anti-patterns + Honest boundaries

### Quality Validation

Test with 3 questions the person publicly answered — direction must match. Ask a new question not covered in the Skill — the framework should infer a consistent stance.

---

## Repository Structure

```
pangu-distill/
├── SKILL.md                           # pangu-distill main file
├── references/
│   ├── quality-checklist.md            # Quality self-checklist
│   ├── special-scenarios.md           # Special scenario handling
│   ├── examples/                       # Distillation examples
│   │   └── distillation-example.md    # Distillation example (Long-Termism)
│   └── templates/                       # Skill templates
│       ├── README.md                  # Template index
│       ├── person-skill-template.md   # D1 Person-type distillation template
│       ├── content-skill-template.md  # D2 Content-type distillation template
│       ├── idea-skill-template.md     # D3 Idea-type distillation template
│       └── phenomenon-skill-template.md # D4 Phenomenon-type distillation template
└── scripts/                            # Python search module
    ├── search/                         # Search pipeline
    ├── crawl/                          # Web crawling
    └── transcribe/                     # Audio/video transcription
```

---

## About Me

**Wukong Feikong Ye** — Founder of AI Dao, independent developer, YouTuber.

| Platform         | Link                                                                         |
| ------------ | ---------------------------------------------------------------------------- |
| 🌐  Website    | [waytoai.cn](https://waytoai.cn)                                                |
| 𝕏   Twitter   | [悟空非空也](https://x.com/wukongnotnull)                                   |
| 📺  BiliBili       | [悟空非空也](https://space.bilibili.com/456634391)                              |
| ▶️  YouTube   | [悟空非空也](https://www.youtube.com/@wukongnotnull)                        |
| 📕  XiaoHongShu    | [悟空非空也](https://www.xiaohongshu.com/user/profile/5ca89c2f000000001100952b) |
| 💬  WeChat    | Search「悟空非空也」or scan QR code below ↓                                            |

<img src="./images/wechat-qrcode.jpg" alt="WeChat QR Code" width="360">

---

<div align="center">

Apache-2.0 license © [悟空非空也](https://github.com/wukongnotnull)

</div>
