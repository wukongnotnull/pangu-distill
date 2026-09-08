# 00 采集日志：张小龙

## 对象与路由

- 对象：张小龙
- `--kind person`（D1）
- 采集命令：`python3 scripts/cli.py collect "张小龙" --kind person --no-agent`
- 输出：`.agents/skills/pangu-zhangxiaolong-distill/references/distillation/`
- `query_locale`：`zh`（对象名含汉字）
- 六路查询（`person_dimensions`）：

| 维 | 查询（与 `collection_summary.json` 一致） |
| --- | --- |
| writings | `张小龙 著作 书单 论文 长文` |
| conversations | `张小龙 访谈 播客 演讲` |
| expression | `张小龙 Twitter 社交媒体 观点 口癖` |
| critics | `张小龙 批评 争议 负面评价 局限` |
| decisions | `张小龙 决策 投资 关键选择 复盘` |
| timeline | `张小龙 生平 时间线 里程碑` |

## 采集器结果（数量）

`collection_summary.json`：

- `success: true`
- `total_results: 28`
- `total_contents: 28`
- 六维全部 `success: true`，各约 4–5 条
- 来源：`wikipedia`（DuckDuckGo HTML 被验证码拦截后回退）

**中文六路：条数够。**

## 采集器结果（相关性）

对同一组中文查询再打 Wikipedia `list=search`，前几条**几乎都不指向微信张小龙**：

| 查询 | 实际命中示例 |
| --- | --- |
| `张小龙 著作 书单 论文 长文` | 古龙、倚天屠龙记、张晖 |
| `张小龙 访谈 播客 演讲` | 锵锵三人行、張菲、臺灣客家話 |
| `张小龙 Twitter 社交媒体 观点 口癖` | Libs of TikTok、德雷克、OVERLORD角色列表 |
| `张小龙 批评 争议 负面评价 局限` | 春晚争议、对毛泽东的评价、牛来 |
| `张小龙 决策 投资 关键选择 复盘` | 改革开放、华为、白紙運動 |
| `张小龙 生平 时间线 里程碑` | 張曼玉、徐小鳳、陈丽君 |

对照：只搜 `张小龙` 能落到 張小龍 / Allen Zhang / Foxmail。六路后缀把名字淹没了。

原因：中文维基搜索把后半段关键词权重抬得比「张小龙」高；`Twitter` 对中文产品人物几乎无意义。

**中文六路：相关性不够。不能当一手语料。**

## 本技能实际语料

公开课与媒体转载（见 01–09）。采集器只证明「中文六路能跑出条数」，不证明「能蒸出张小龙」。
