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

It absorbs what actually raises fidelity from [Distilly](https://github.com/titanwings/distilly), [Nuwa](https://github.com/alchaincyf/nuwa-skill), and [Cangjie](https://github.com/Yeadon8888/cangjie-skill), then adds the layers they leave out.
<br>
 **pangu-distill.meta-skill** extracts **runnable thinking frameworks** from any subject.

---

**Quick Navigation**

[Demo](#demo) | [Quick Install](#quick-install) | [Published Skills](#published-skills) | [Classic Cases](#classic-cases) | [Architecture](#architecture) | [Repository Structure](#repository-structure) | [About Me](#about-me)

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

Pangu     ❯ Distilling
            ✓ Seven-question intake (idea / decision use / no primary files)
            ✓ Six-stream collection: plan → host search → ingest
            ✓ Seven-level extract: origin stories, decisions, failures, tensions
            ✓ 4.5-layer model passed triple verification
            ✓ Independent fidelity score ≥ 80

            Output: pangu-long-termism

            Models (each with origin story + trigger):
            ① Compound interest only pays those who stay
            ② The quote is not the information
            ③ Persistence ≠ refusing to update the map (heuristic)

            Honest boundary: talking about ten years with no buffer is self-deception
```

---

## Quick Install

### Technical Users

The same `SKILL.md` runs on Claude Code, Cursor, Codex, OpenClaw, and Gemini CLI. Only the discovery path changes. See [references/host-compatibility.md](references/host-compatibility.md).

```bash
npx skills add wukongnotnull/pangu-distill
```

Restart or rescan the agent afterwards.

After installation, say this to your Agent:

```markdown
> Distill "Long-Termism"
> I want to build a Buffett thinking framework
> Distill myself
> Distill this conversation
```

### Non-Technical Users (Conversational)

No commands to remember — just copy and paste this to your Agent:

```
help me to install this skill：https://github.com/wukongnotnull/pangu-distill
```

After installation, tell it what you want in natural language:

```markdown
> Help me distill: long-termism
> I want to build a Buffett thinking framework
> Distill myself
```

## Published Skills

Skills already published from pangu-distill:

| Skill | Source | Repository |
|------|------|------|
| **pangu-deepseek-v4** | DeepSeek-V4 Technical Report | [wukongnotnull/pangu-deepseek-v4](https://github.com/wukongnotnull/pangu-deepseek-v4) |
| **pangu-one-day-life-reset** | *How to fix your entire life in 1 day* | [wukongnotnull/pangu-one-day-life-reset](https://github.com/wukongnotnull/pangu-one-day-life-reset) |

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

Extract runnable thinking frameworks from any subject: Person / Content / Idea / Phenomenon / **Self**.

What this repo combines and then exceeds:

| Layer | pangu-distill |
|----|----------|
| Frame | **4.5 layers**: identity / mental models / expression DNA / decision frame / **honest boundary** (not an appendix) |
| Extract | **Seven-level scan**: origin stories first, quotes last. No "why they believe it" → it does not enter the Skill |
| Verify | Triple check (cross-domain / generative / exclusive) + **triggers** + **reasoning steps** |
| Collect | **Six streams + primary files**: `scripts/run.py plan` emits the query plan → the host agent searches with its own tools → `ingest` dedupes, filters blacklisted domains, fetches text and writes the source ledger |
| QA | `scripts/run.py check` (naming / 4.5 layers / evidence trio / FIDELITY / test packet) + process gate + **fidelity score with separated question-writer, answerer and grader** (≥80, test packet shipped, no self-grading) |
| Refine | Three rounds: structure → user → stress test |

### Execution Flow

Intake → create directory → collect (`plan` → host search → `ingest`) → seven-level extract → build → `check` → verify → refine.

Default streams: writings / interviews / expression / criticism / decisions / timeline. User-supplied books, transcripts, and chats beat web summaries. Searching is done by the host agent (its web tools beat any headless crawler); the scripts only do the deterministic parts: plan, ingest, check. `ingest` with zero usable sources fails instead of pretending.

```bash
python3 scripts/run.py plan "Jeff Bezos" --kind person -o out/references/distillation/
# …host agent searches per plan.json and writes out/references/distillation/results.json…
python3 scripts/run.py ingest --plan out/references/distillation/plan.json out/references/distillation/results.json
python3 scripts/run.py check out/                    # after build
python3 scripts/run.py fidelity init out/ --target Munger --alias Berkshire  # question templates
python3 scripts/run.py fidelity blind out/                                    # mask names after answering (auto-expands short forms / surnames, lists leftover entity-like words)
python3 scripts/run.py check out/ --require-fidelity                          # before shipping
```

Every mental model needs an origin story, cross-domain evidence, a trigger, reasoning steps, and a failure condition.

### Quality Validation

Process gate: `references/quality-checklist.md`. Factory gate: `references/fidelity-scorecard.md` with three separate sessions (question writer, answerer, grader); questions, rubric, answers and the name-masked blind copy ship in the product's `fidelity/` folder, and `check --require-fidelity` verifies the questions were not copied from the Skill, the answerer declared no network, the seven scores add up, and independence is stated. Ship only at ≥80 with zero FAIL. All four earlier sample products in the repo were re-scored under this protocol; `.agents/skills/pangu-munger/` is a sample distilled from scratch with the new pipeline, with the run recorded in `references/examples/live-test-munger.md`.

---

## Repository Structure

```
pangu-distill/
├── SKILL.md
├── .agents/skills/                     # portable default output dir
├── .claude/skills/skill-creator/
├── .claude/skills/skill-vetter/
├── references/
│   ├── host-compatibility.md
│   ├── distillation-methodology.md
│   ├── research-guide.md
│   ├── quality-checklist.md
│   ├── fidelity-scorecard.md
│   ├── output-spec.md
│   ├── anti-patterns.md
│   ├── special-scenarios.md
│   ├── examples/distillation-example.md
│   └── templates/
└── scripts/
    ├── run.py                          # plan / ingest / check / collect-local / transcribe
    ├── distill/                        # plan.py / ingest.py / check.py / fidelity.py / local.py
    ├── crawl/                          # fetcher + DuckDuckGo / Wikipedia fallback search
    └── transcribe/
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
