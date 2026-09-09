# 来源与采集记录

**对象**：Jeff Bezos / 贝索斯  
**类型**：D1 人物（决策 / 经营判断）  
**调研时间**：2026-09-08  
**一手文件**：无用户文件  
**`{pangu_output_root}`**：`.agents/skills`

不在 README「经典案例」13 人名单里。本目录是 D1 实跑样本，不是官方人物案例发布。

## 脚本采集

```bash
python3 scripts/cli.py collect "Jeff Bezos" --kind person --no-agent \
  -o .agents/skills/pangu-bezos/references/distillation
```

| 项 | 值 |
|----|-----|
| 总结果 | 1 |
| 总正文 | 1 |
| 成功维 | `conversations`（wikipedia） |
| 空维 | writings / expression / critics / decisions / timeline（`success: false`） |
| 退出码 | 0（有 1 条即算采集成功） |

人物维查询仍是中文后缀（`著作 书单`、`生平`）套在英文名上，维基搜不到。`--kind person` 修好了「问错 pens」，没修好「中英查询」。空维已标失败，没有假成功。原始 `*.json` 保留。

## 宿主搜索补的一手 / 准一手

| # | 来源 | 一手？ | 用途 |
|---|------|--------|------|
| 1 | [1997 股东信](https://www.aboutamazon.com/news/company-news/amazons-original-1997-letter-to-shareholders) / [PDF](https://s2.q4cdn.com/299287126/files/doc_financials/annual/Shareholderletter97.pdf) | 一手 | 长期、客户、Day 1 |
| 2 | 2015 信（2016 发布）[SEC EX-99.1](https://www.sec.gov/Archives/edgar/data/1018724/000119312516530910/d168744dex991.htm) | 一手 | 单向/双向门、失败与发明 |
| 3 | 2016 信（2017 发布）[GeekWire 全文](https://www.geekwire.com/2017/full-text-annual-letter-amazon-ceo-jeff-bezos-explains-avoid-becoming-day-2-company/) / [aboutamazon](https://www.aboutamazon.com/news/company-news/2016-letter-to-shareholders) | 一手 | Day 2、代理指标、disagree and commit |
| 4 | Academy of Achievement 口述 Central Park / regret minimization | 一手 | 离开 D. E. Shaw |
| 5 | Fortune 2014-12 Business Insider Ignition：「billions of dollars of failures」 | 一手（会议口述） | Fire Phone 前后 |
| 6 | 2018 信（转述 Echo/Fire Phone）[CNBC](https://www.cnbc.com/2020/05/22/jeff-bezos-why-you-cant-feel-bad-about-failure.html) | 混合 | 失败规模要随公司变大 |
| 7 | NYT 2015-08-16 Kantor/Streitfeld | 二手（批评） | 职场强度 |
| 8 | 2015-08 内部备忘 [GeekWire / Boston Globe](https://www.geekwire.com/2015/full-memo-jeff-bezos-responds-to-cutting-nyt-expose-says-tolerance-for-lack-of-empathy-needs-to-be-zero/) | 一手 | 本人回应：不认识那家公司；无共情零容忍 |

未读：全书 *The Everything Store*、近年 Blue Origin / 华盛顿邮报经营细节、仓配一线劳动争议的本人长篇复盘。
