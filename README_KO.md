<div align="center">

# 판고증류.meta-skill

<br>

> **만물을 증류하여 실행 가능한 사고 프레임워크를 추출한다** <br>

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-orange.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![Skills](https://img.shields.io/badge/skills.sh-Compatible-green)](https://skills.sh)

<br>

**판고(창세之神)는 천지를 연 뒤, 세상이 적막하여,** <br>
**황토로 사람을 빚어 숨을 불어넣어 살게 했으니,** <br>
**결과: 흙 인간이 세계를 지배하게 되었다.**

<br>

[Distilly](https://github.com/titanwings/distilly), [여와](https://github.com/alchaincyf/nuwa-skill), [창힐](https://github.com/Yeadon8888/cangjie-skill)에서 충실도를 올리는 부분만 흡수하고, 빠진 층을 더한다.
<br>
 **판고증류.meta-skill** 은 임의의 대상에서 **실행 가능한 사고 프레임워크**를 추출한다.

---

**빠른 탐색**

[데모](#데모) | [빠른 설치](#빠른-설치) | [클래식 케이스](#클래식-케이스) | [아키텍처](#아키텍처) | [저장소 구조](#저장소-구조) | [저자 소개](#저자-소개)

<br>

**다른 언어**

[中文](README.md) · [English](README_EN.md) · [日本語](README_JA.md) · [Español](README_ES.md)

<br>


</div>

---

## 데모

장기주의를 증류하는 것은 "인내"라는 글자만이 아니라 실행 가능한 인지 프레임워크를 추출하는 것이다:

```
사용자    ❯ "장기주의" 증류하기

판고증류  ❯ 【Phase 1 실행 중】
            ✓ 6트랙 수집 완료 (저작/인터뷰/비판/의사결정/타임라인/유사)
            ✓ 멘탈 모델 3중 검증 통과
            ✓ 증류 완료

            산출물: 《장기주의 · 사고 프레임워크》

            핵심 멘탈 모델:
            ① 복리 사고: 시간의 친구로Persist, 지수적 성장 즐기기
            ② 장기 초점: 단기 변동 무시, 장기 가치 집중
            ③ 인내력: 힘든 시기에도 포기하지 않음

            표현 DNA:
            - 높은 확신: "분명히", "반드시", "의심의 여지없이"
            - 적은 전환구, "하지만" 잘 사용 안 함
            - 말버릇: "시간의 친구", "천천히 오는 게 빠르다"
```

---

## 빠른 설치

### 방법 1: 기술 사용자 (커맨드 라인)

npx로 직접 설치:

```bash
npx skills add wukongnotnull/pangu-distill
```

설치 후, Agent에게这样说:

```markdown
> 장기주의 증류하기
> 버핏의 사고 프레임워크를 만들고 싶어요
```

### 방법 2: 비기술 사용자 (대화식)

명령어를 기억할 필요 없이,以下の文をAgentにコピー＆ペーストしてください:

```
帮我安装这个 skill：https://github.com/wukongnotnull/pangu-distill
```

설치 후, 자연어로 원하는 것을 말하세요:

```markdown
> 장기주의를 증류해주세요
> 버핏의 사고 프레임워크를 만들고 싶어요
```

## 클래식 케이스

아래 13명은 계획 중인 증류 사례이며, 완성된 Skill은 **아직 공개되지 않았습니다**:

### 💰 투자/비즈니스

| 인물 | 방향 | 상태 |
|------|---------|------------------|
| ** Naval** |财富/레버리지/인생 철학 | 미공개 |
| ** Munger** | 투자/멀티 모델/역발상 | 미공개 |
| ** 장설봉** | 교육/커리어 플래닝/계층 이동 | 미공개 |

### 🚀 스타트업/제품

| 인물 | 방향 | 상태 |
|------|---------|------------------|
| ** Paul Graham** | 스타트업/글쓰기/제품/인생 철학 | 미공개 |
| ** 장일명** | 제품/조직/글로벌화/ 인재 | 미공개 |
| ** 스티브 잡스** | 제품/디자인/전략 | 미공개 |
| ** 일론 머스크** | 엔지니어링/비용/제1원리 | 미공개 |

### 🤖 AI/기술

| 인물 | 방향 | 상태 |
|------|---------|------------------|
| ** Karpathy** | AI/엔지니어링/교육/오픈소스 | 미공개 |
| ** Ilya Sutskever** | AI 안전/scaling/연구 취향 | 미공개 |

### 🎬 콘텐츠 제작

| 인물 | 방향 | 상태 |
|------|---------|------------------|
| ** MrBeast** | 콘텐츠 제작/YouTube 방법론 | 미공개 |

### 🎯 커뮤니케이션/_POWER

| 인물 | 방향 | 상태 |
|------|---------|------------------|
| 🔥** 트럼프** | 협상/파워/커뮤니케이션/행동 예측 | 미공개 |

### 🧠 사고/학습

| 인물 | 방향 | 상태 |
|------|---------|------------------|
| ** 파인만** | 학습/가르침/과학적 사고 | 미공개 |
| ** 탈레브** | 리스크/안티프래질리티/불확실성 | 미공개 |

---

## 아키텍처

### 핵심 능력

임의의 대상에서 실행 가능한 사고 프레임워크를 추출하여 인물 / 콘텐츠 / 사상 / 현상 / **자아** 스킬을 만든다.

**4.5층**(정직한 경계는 부록이 아님) + **7급 추출**(형성 이야기가 먼저, 명언은 마지막) + 3중 검증 + 트리거 + 추론 단계 + `scripts/run.py` 필수 실행 + 독립 이중 에이전트 충실도 채점(≥80, 자기 채점 금지).

### 실행 흐름

확인 → 디렉터리 생성 → 스크립트 6로 수집(최대 7 에이전트) → 7급 추출 → 구축 → 검증 → 3회 정제.

각 멘탈 모델은 형성 이야기, 교차 증거, 트리거, 추론 단계, 한계를 동시에 가진다.

### 품질 검증

과정 문은 `quality-checklist.md`. 출고 문은 `fidelity-scorecard.md`. 답변 에이전트와 채점 에이전트는 분리. 80점 미만은 납품하지 않는다.

---

## 저장소 구조

```
pangu-distill/
├── SKILL.md
├── .claude/skills/skill-creator/
├── .claude/skills/skill-vetter/
├── references/
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
```

---

## 저자 소개

**오공비공야** — AI之道 창립자, 독립 개발자, 유튜버.

| 플랫폼         | 링크                                                                         |
| ------------ | ---------------------------------------------------------------------------- |
| 🌐  웹사이트    | [waytoai.cn](https://waytoai.cn)                                                |
| 𝕏  Twitter   | [悟空非空也](https://x.com/wukongnotnull)                                   |
| 📺  BiliBili       | [悟空非空也](https://space.bilibili.com/456634391)                              |
| ▶️  YouTube   | [悟空非空也](https://www.youtube.com/@wukongnotnull)                        |
| 📕  XiaoHongShu    | [悟空非空也](https://www.xiaohongshu.com/user/profile/5ca89c2f000000001100952b) |
| 💬  WeChat    | 「悟空非空也」검색 또는 아래 QR 코드 스캔 ↓                                            |

<img src="./images/wechat-qrcode.jpg" alt="WeChat QR 코드" width="360">

---

<div align="center">

Apache-2.0 license © [悟空非空也](https://github.com/wukongnotnull)

</div>
