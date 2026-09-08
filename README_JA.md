<div align="center">

# 盤古蒸留.meta-skill

<br>

> **万物を蒸留し、実行可能な思考フレームワークを取り出す** <br>

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-orange.svg)](LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-Skill-blueviolet)](https://claude.ai/code)
[![Skills](https://img.shields.io/badge/skills.sh-Compatible-green)](https://skills.sh)

<br>

**盤古（創世神）は、天地を開いた後、世間が寂しくなり、** <br>
**泥で人間を作り、息を吹きかけて生きらせた、** <br>
**結果：泥人間が世界を支配するようになった。**

<br>

[Distilly](https://github.com/titanwings/distilly)、[女娲](https://github.com/alchaincyf/nuwa-skill)、[倉頡](https://github.com/Yeadon8888/cangjie-skill) から保真度を上げる部分を吸収し、欠けている層を足す。
<br>
 **盤古蒸留.meta-skill** は、任意の対象から**実行可能な思考フレームワーク**を取り出す。

---

**クイックナビゲーション**

[デモ](#デモ) | [クイックインストール](#クイックインストール) | [经典案例](#经典案例) | [アーキテクチャ](#アーキテクチャ) | [リポジトリ構造](#リポジトリ構造) | [私について](#私について)

<br>

**多言語**

[中文](README.md) · [English](README_EN.md) · [한국어](README_KO.md) · [Español](README_ES.md)

<br>


</div>

---

## デモ

長期主義を蒸留することは「忍耐」二字だけでなく、実行可能な認知フレームワークを抽出する：

```
ユーザー   ❯ 長期主義を蒸留する

盤古蒸留  ❯ 【フェーズ 1 実行中】
            ✓ 六路収集完了（著作/インタビュー/批判/意思決定/時間軸/類似）
            ✓ メンタルモデル三重検証通過
            ✓ 蒸留完了

            出力：《長期主義・思考フレームワーク》

            コアメンタルモデル：
            ① 複利思考：時間の味方として持続し、指数関数的成長を楽しむ
            ② 長期焦点：短期変動を無視し、長期価値に集中する
            ③ 忍耐力：困難な時期に諦めない

            表現DNA：
            - 高い確実性：「明らかに」「しなければならない」「疑いの余地なく」
            - 少ない転換句、「しかし」をあまり使わない
            - 口癖：「時間の味方」「ゆっくり来た方が速い」
```

---

## クイックインストール

### 方法一：技術ユーザー（コマンドライン）

同じ `SKILL.md` が Claude Code / Cursor / Codex / OpenClaw で動く。発見ディレクトリだけが違う。詳細は [host-compatibility.md](references/host-compatibility.md)。

```bash
git clone https://github.com/wukongnotnull/pangu-distill.git
cd pangu-distill
bash scripts/install-host.sh
bash scripts/install-host.sh --project
```

Claude Code だけなら：

```bash
npx skills add wukongnotnull/pangu-distill
```

インストール後、Agent に这样说：

```markdown
> 長期主義を蒸留する
> バフェットの思考フレームワークを作りたい
```

### 方法二：非技術ユーザー（会話式）

コマンドを覚える必要はありません。以下の文をAgentにコピー＆ペーストしてください：

```
帮我安装这个 skill：https://github.com/wukongnotnull/pangu-distill
```

インストール後、自然言語でほしいことを伝えましょう：

```markdown
> 長期主義を蒸留してほしい
> バフェットの思考フレームワークを作りたい
```

## 经典案例

以下の13名は計画中の蒸留ケースです。完成スキルは**まだ公開していません**：

### 💰 投資/ビジネス

| 人物 | 方向 | 状態 |
|------|---------|------------------|
| **ナ瓦尔** |  富/レバレッジ/人生哲学 | 未公開 |
| **モハン** | 投資/多元思考/逆張り | 未公開 |
| **張雪峰** | 教育/キャリア計画/階層移動 | 未公開 |

### 🚀 スタートアップ/プロダクト

| 人物 | 方向 | 状態 |
|------|---------|------------------|
| **ポウル・グラハム** | スタートアップ/執筆/プロダクト/人生哲学 | 未公開 |
| **張一鳴** | プロダクト/組織/グローバル化/人才 | 未公開 |
| **スティーブ・ジョブズ** | プロダクト/デザイン/戦略 | 未公開 |
| **イーロン・マスク** | エンジニアリング/コスト/第一原理 | 未公開 |

### 🤖 AI/テクノロジー

| 人物 | 方向 | 状態 |
|------|---------|------------------|
| **カラ帕thy** | AI/エンジニアリング/教育/开源 | 未公開 |
| **イリヤ・サツケバー** | AI安全/scaling/研究 맛 | 未公開 |

### 🎬 コンテンツ創作

| 人物 | 方向 | 状態 |
|------|---------|------------------|
| **MrBeast** | コンテンツ創作/YouTube方法論 | 未公開 |

### 🎯 コミュニケーション/パワー

| 人物 | 方向 | 状態 |
|------|---------|------------------|
| 🔥**トランプ** | 交渉/パワー/コミュニケーション/行動予測 | 未公開 |

### 🧠 思考/学習

| 人物 | 方向 | 状態 |
|------|---------|------------------|
| **ファインマン** | 学習/教授/科学思考 | 未公開 |
| **タレブ** | リスク/アンチフラジリティ/不確実性 | 未公開 |

---

## アーキテクチャ

### コア能力

任意の対象から実行可能な思考フレームワークを抽出し、人物 / コンテンツ / 思想 / 現象 / **自己**スキルを生成する。

**4.5層**（誠実な境界は付録ではない）+ **七級抽出**（形成物語が先、金言は最後）+ 三重検証 + トリガー条件 + 推論手順 + `scripts/run.py` 必須実行 + 独立二エージェント保真度採点（≥80、自己採点禁止）。

### 実行フロー

確認 → ディレクトリ作成 → スクリプト六路収集（最大7エージェント）→ 七級抽出 → 構築 → 検証 → 三回精錬。

各メンタルモデルは形成物語・横断証拠・トリガー・推論手順・限界を同時に持つ。

### 品質検証

過程門は `quality-checklist.md`。出荷門は `fidelity-scorecard.md`。解答エージェントと採点エージェントは分ける。80点未満は納品しない。

---

## リポジトリ構造

```
pangu-distill/
├── SKILL.md
├── .agents/skills/
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
```

---

## 私について

**悟空非空也** — AI之道創始者、独立開発者、YouTuber。

| プラットフォーム         | リンク                                                                         |
| ------------ | ---------------------------------------------------------------------------- |
| 🌐  Webサイト    | [waytoai.cn](https://waytoai.cn)                                                |
| 𝕏  Twitter   | [悟空非空也](https://x.com/wukongnotnull)                                   |
| 📺  BiliBili       | [悟空非空也](https://space.bilibili.com/456634391)                              |
| ▶️  YouTube   | [悟空非空也](https://www.youtube.com/@wukongnotnull)                        |
| 📕  XiaoHongShu    | [悟空非空也](https://www.xiaohongshu.com/user/profile/5ca89c2f000000001100952b) |
| 💬  WeChat    | 「悟空非空也」を検索するか、下のQRコードをスキャン ↓                                            |

<img src="./images/wechat-qrcode.jpg" alt="公众号二维码" width="360">

---

<div align="center">

Apache-2.0 license © [悟空非空也](https://github.com/wukongnotnull)

</div>
