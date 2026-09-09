# 来源与采集记录

**对象**：第一性原理 / first principles  
**类型**：D3 思想  
**调研时间**：2026-09-08  
**采集模式**：纯网络搜索（用户无一手文件）  
**`{pangu_skill_root}`**：`/workspace`（本会话加载的 SKILL.md 目录；环境变量未设）  
**`{pangu_output_root}`**：`python3 scripts/run.py output-root` → `/workspace/.agents/skills`

## 脚本采集（必须记录，不要假装采过）

按 Phase 1.2 已跑：

```bash
PYTHONPATH=/workspace/scripts python3 scripts/cli.py collect "第一性原理" \
  -o .agents/skills/pangu-first-principles/references/distillation
PYTHONPATH=/workspace/scripts python3 scripts/cli.py team "第一性原理" -a 7 \
  -o .agents/skills/pangu-first-principles/references/distillation
```

结果：

| 项 | 值 |
|----|-----|
| `collection_summary.json` | `total_results: 0`，`total_contents: 0` |
| 六维 `success` | 全部 `true`，`error: null`，`used_source: unknown` |
| `team` | 6 名分析师均写「依据: 0 条相关素材」 |
| `00_master_report.md` | 「共收集 0 条搜索结果，0 条内容」 |

原因（本环境实测，不是推断成「网上没材料」）：

1. `scripts/run.py` 的 `pip install -e .` 路径会因 `setuptools` 发现多个顶层包（`crawl` / `search` / `transcribe`）失败。本次用 `PYTHONPATH` 绕过。
2. Agent 搜索封装优先探测 `claude --version`；本环境没有 Claude CLI，降级到 DuckDuckGo HTML 爬虫后仍返回空列表。
3. 空结果仍标 `success: true`，主流程不会停。

原始空产物保留在同目录：`*.json`、`00_master_report.md`、`0*_analyst_report.md`。

## 实际使用的来源（宿主搜索，2026-09-08）

一手 = 本人开口的访谈/演讲逐字或接近逐字；二手 = 转述、百科、评论。

| # | 来源 | 一手？ | 用途 |
|---|------|--------|------|
| 1 | Kevin Rose × Elon Musk，2012-09，[YouTube](https://www.youtube.com/watch?v=L-s_3b5fRd8) | 一手（口述） | 类比 vs 第一性；电池 $600 → 材料 $80 |
| 2 | 同上访谈的二次整理：[Startup Archive](https://www.startuparchive.org/p/elon-musk-explains-first-principles-thinking) | 二手（贴近原话） | 材料清单与 LME 算法 |
| 3 | [Farnam Street / fs.blog](https://fs.blog/first-principles/) 对 2012 访谈的引述 | 二手 | 交叉核对措辞 |
| 4 | SXSW Live，2013-03-09，[逐字稿转载](https://singjupost.com/transcript-of-elon-musk-interview-sxsw-live-march-9-2013/) | 一手（转载稿，非官方） | 物理训练、检查公理、概率带、「做庄家」 |
| 5 | TED 2013，Chris Anderson 访谈，[archived talk page](https://web.archive.org/web/20140226234726/http:/www.ted.com/talks/elon_musk_the_mind_behind_tesla_spacex_solarcity.html) | 一手 | 「过日子必须用类比；做新东西才用物理」 |
| 6 | [Business Insider, 2013-02](https://www.businessinsider.com/elon-musk-advice-on-innovation-2013-2) | 二手 | TED 要点：火箭逃不开牛顿第三定律 |
| 7 | [Stanford Encyclopedia：Aristotle’s Metaphysics](https://plato.stanford.edu/ENTRIES/aristotle-metaphysics/) | 二手（学术综述） | archai / aitia；「对我们更清楚」vs「就其自身更清楚」 |
| 8 | [Jefago, The Challenge With Thinking From First Principles](https://www.jefago.com/product-management/the-problem-of-first-principles-thinking/) | 一手（批评者原文） | 材料现货价不是第一性；真公理也可能用错层 |
| 9 | Gerrits, *Social Physics in the Age of Generative AI*（[PDF](https://pure.uva.nl/ws/files/341515381/Social_Physics_in_the_Age_of_Generative_AI.pdf)） | 一手（论文） | 社会系统的反身性：意义构成物没有「金属交易所」 |

未获取、不得装成已读：

- 亚里士多德希腊原文或标准英译全书（*Metaphysics* / *Physics* / *Posterior Analytics*）
- Tesla / SpaceX 成本模型、LME 当时报价表
- Kevin Rose 访谈的官方逐字稿（只有视频 + 二次整理）
- 马斯克本人承认「电池拆解算错了」的原始陈述（未见）

**一手占比（按条数，不含空脚本）**：约 5/9 ≈ 55% 是本人或批评者原文；按论证重量，电池故事仍大量依赖二次整理。诚实边界按「一手不足」处理，不一手占比当合格证。
