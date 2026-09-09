# 00 采集日志：雷军

## 对象与路由

- 对象：雷军
- `--kind person`（D1）
- 采集命令：`python3 scripts/cli.py collect "雷军" --kind person --no-agent`
- 输出：`.agents/skills/pangu-leijun/references/distillation/`
- `query_locale`：`zh`
- 表达维查询：`雷军 社交媒体 观点 口癖`（已无 Twitter）

## 采集器结果（#10 之后）

`collection_summary.json`：

- `success: true`，退出码 0
- `total_results: 60` / `total_contents: 60`
- 六维全部 `success: true`，各 10 条
- 来源：`wikipedia`（DuckDuckGo HTML 仍被拦）
- `simplify_query` 把六路都收成 `雷军`

同一组带后缀的查询再打维基，标题是：

| 查询 | 实际命中 |
| --- | --- |
| `雷军 著作 书单 论文 长文` | 雷军、小米集團、小米汽车、Lei Jun、Xiaomi SU7 |

只搜 `雷军` 也是这五条。六维重复同一组页。

**条数够。相关性过关（指向雷军/小米，不是古龙/春晚）。维度区分不够（六路同一组百科页）。**

对照 #9 张小龙：修之前，后缀把名字淹没。#10 之后，中文维基保底不再脱靶。

## 本技能实际语料

2012 站长大会七字诀转载、2011 微访谈、2021 口述复盘。采集器证明「名字能对上」，不证明「采到了演讲」。
