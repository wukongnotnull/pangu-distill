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

[colleague.skill](https://github.com/titanwings/colleague-skill) 과 [Nuwa.skill](https://github.com/titanwings/colleague-skill) 의启发를 받아, 유명인, 고인, 엘리트 등의 사고 프레임워크를 증류한다.
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

판고증류은 13명의 인물을 증류했으며, 분야별로 그룹화되어便于查找:

### 💰 투자/비즈니스

| 인물 | 방향 | 일괄 설치 |
|------|---------|------------------|
| ** Naval** |财富/레버리지/인생 철학 | `npx skills add wukongnotnull/pangu-naval` |
| ** Munger** | 투자/멀티 모델/역발상 | `npx skills add wukongnotnull/pangu-munger` |
| ** 장설봉** | 교육/커리어 플래닝/계층 이동 | `npx skills add wukongnotnull/pangu-zhangxuefeng` |

### 🚀 스타트업/제품

| 인물 | 방향 | 일괄 설치 |
|------|---------|------------------|
| ** Paul Graham** | 스타트업/글쓰기/제품/인생 철학 | `npx skills add wukongnotnull/pangu-paul-graham` |
| ** 장일명** | 제품/조직/글로벌화/ 인재 | `npx skills add wukongnotnull/pangu-zhang-yiming` |
| ** 스티브 잡스** | 제품/디자인/전략 | `npx skills add wukongnotnull/pangu-steve-jobs` |
| ** 일론 머스크** | 엔지니어링/비용/제1원리 | `npx skills add wukongnotnull/pangu-elon-musk` |

### 🤖 AI/기술

| 인물 | 방향 | 일괄 설치 |
|------|---------|------------------|
| ** Karpathy** | AI/엔지니어링/교육/오픈소스 | `npx skills add wukongnotnull/pangu-karpathy` |
| ** Ilya Sutskever** | AI 안전/scaling/연구 취향 | `npx skills add wukongnotnull/pangu-ilya-sutskever` |

### 🎬 콘텐츠 제작

| 인물 | 방향 | 일괄 설치 |
|------|---------|------------------|
| ** MrBeast** | 콘텐츠 제작/YouTube 방법론 | `npx skills add wukongnotnull/pangu-mrbeast` |

### 🎯 커뮤니케이션/_POWER

| 인물 | 방향 | 일괄 설치 |
|------|---------|------------------|
| 🔥** 트럼프** | 협상/파워/커뮤니케이션/행동 예측 | `npx skills add wukongnotnull/pangu-trump` |

### 🧠 사고/학습

| 인물 | 방향 | 일괄 설치 |
|------|---------|------------------|
| ** 파인만** | 학습/가르침/과학적 사고 | `npx skills add wukongnotnull/pangu-feynman` |
| ** 탈레브** | 리스크/안티프래질리티/불확실성 | `npx skills add wukongnotnull/pangu-taleb` |

---

## 아키텍처

### 핵심 능력

임의의 대상에서 실행 가능한 사고 프레임워크를 추출하여 인물 / 콘텐츠 / 사상 / 현상 스킬을 만든다.

### 실행 흐름

#### Phase 1: 증류

**Step 1: 정보 수집**

3개 에이전트가 병렬 수집 (마스터-슬레이브模式):

| 에이전트 | 책임 | 출력 파일 |
|-------|------|---------|
| Master (素材 수집가) | 핵심 저작 + 타임라인 | `01-writings.md`, `06-timeline.md` |
| Analyst A | 팟캐스트/인터뷰 + 표현 DNA | `02-conversations.md`, `03-expression-dna.md` |
| Analyst B | 비판 평가 + 주요 의사결정 + 同類 | `04-limitations.md`, `05-decisions.md`, `07-similar-objects.md` |

**Step 2: 프레임워크 추출**

- **멘탈 모델 3중 검증**:
  - 검증 1: 횡분 야 재현 (≥2개 다른 분야)
  - 검증 2: 생성력 (새 문제에 대한 입장 추론 가능)
  - 검증 3: 배타성 (모든 똑똑한 사람이 이렇게 생각하는 것은 아님)
  - 3개 통과 → 멘탈 모델; 1-2개 통과 → 의사결정 휴리스틱

- **표현 DNA 정량화**: 문장 지문, 스타일 라벨, 금기어와 말버릇

- **모순 처리**: 시간적 모순→진화 궤적 기록; 분야적 모순→분야별로 기록; 본질적 긴장→핵심 긴장으로 명시

**Step 3: 스킬 구축**

3-7개 멘탈 모델 + 5-10개 의사결정 휴리스틱 + 표현 DNA + 가치관과 반패턴 + 정직한 경계

### 품질 검증

이 사람이 공개적으로 답변한 3개 질문으로 테스트하여 방향이 일치해야 통과한다. 스킬에 없는 새 질문에서는 프레임워크가 일관된 입장을 도출해야 한다.

---

## 저장소 구조

```
pangu-distill/
├── SKILL.md                           # 판고증류 本체
├── references/
│   ├── quality-checklist.md            # 품질 자검清单
│   ├── special-scenarios.md           # 특수 장면 처리
│   ├── examples/                       # 증류 예시
│   │   └── distillation-example.md    # 증류 예시 (장기주의)
│   └── templates/                       # 스킬 템플릿
│       ├── README.md                  # 템플릿 인덱스
│       ├── person-skill-template.md   # D1 인물類 증류 템플릿
│       ├── content-skill-template.md  # D2 콘텐츠類 증류 템플릿
│       ├── idea-skill-template.md     # D3 사상類 증류 템플릿
│       └── phenomenon-skill-template.md # D4 현상類 증류 템플릿
└── scripts/                            # Python 검색 모듈
    ├── search/                         # 검색 파이프라인
    ├── crawl/                          # 웹 크롤링
    └── transcribe/                     # 음성/영상 변환
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
