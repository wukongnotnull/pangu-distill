# 多宿主兼容

盘古蒸馏是一份 `SKILL.md` + `scripts/`。不要为每个 Agent 复制正文。差别只有两件事：**它从哪发现这份 Skill**，**蒸馏产物写到哪**。

## 1. 发现路径

| 宿主 | 用户级 | 项目级 |
|------|--------|--------|
| Claude Code | `~/.claude/skills/pangu-distill` | `.claude/skills/pangu-distill` |
| Cursor | 无（用 `~/.agents/skills/`） | `.cursor/skills/` 或 `.agents/skills/` |
| Codex | `~/.codex/skills/pangu-distill` | `.agents/skills/` 或 `.codex/skills/` |
| OpenClaw | `~/.openclaw/skills/pangu-distill` | `skills/` |
| Gemini CLI | `~/.gemini/skills/pangu-distill` | `.gemini/skills/` |
| GitHub Copilot | `~/.config/github-copilot/skills/` | `.github/skills/` |
| Hermes | `~/.hermes/skills/pangu-distill` | — |
| OpenCode | `~/.config/opencode/skills/pangu-distill` | — |

跨宿主默认目录是 `.agents/skills/`：Codex 官方扫描它，Cursor 也扫描它。

安装：

```bash
# 用户级（Claude + Cursor/公共 + Codex）
bash scripts/install-host.sh

# 当前项目（Cursor / Codex 立刻能发现）
bash scripts/install-host.sh --project

# 某一个宿主
bash scripts/install-host.sh --host openclaw
bash scripts/install-host.sh --host cursor --project
```

`npx skills add wukongnotnull/pangu-distill` 仍然可用，通常只进 Claude Code 的用户目录。其他宿主用上面的脚本。

## 2. Skill 根目录 `{pangu_skill_root}`

按这个顺序取，取到就停：

1. 环境变量 `PANGU_SKILL_ROOT`
2. `CLAUDE_SKILL_DIR` / `CODEX_SKILL_DIR` / `CURSOR_SKILL_DIR`（宿主注入谁用谁）
3. 宿主 discovery 上下文里「实际加载的那份 SKILL.md」所在目录
4. 都没有 → 问用户，禁止把 `cwd` 当成 Skill 根目录

脚本和参考文档一律：

`{pangu_skill_root}/scripts/run.py`  
`{pangu_skill_root}/references/...`

探测：

```bash
python3 "{pangu_skill_root}/scripts/run.py" skill-root
```

## 3. 产出目录 `{pangu_output_root}`

蒸馏成品写到**当前工作区里这个 Agent 会读的 skills 目录**，不是永远写 `.claude/skills/`。

优先级：

1. 环境变量 `PANGU_OUTPUT_ROOT`
2. 从 cwd 向上到 git 根，第一个已存在的：
   `.agents/skills` → `.cursor/skills` → `.claude/skills` → `.codex/skills` → `.github/skills` → `skills`
3. 都没有 → 创建 `.agents/skills/`

成品路径：

`{pangu_output_root}/pangu-[对象]/`

探测：

```bash
python3 "{pangu_skill_root}/scripts/run.py" output-root
```

只存在 `.claude/skills/` 的老项目会继续写到那里。新项目默认进 `.agents/skills/`。

## 4. 工具：写能力，不写品牌

| 需要的能力 | 做法 |
|------------|------|
| 联网搜事实 | 用当前宿主的搜索 / 浏览器工具，不要写死 WebSearch |
| 读本地文件 | Read / 读文件 |
| 跑采集脚本 | Bash / 终端执行 `{pangu_skill_root}/scripts/run.py` |
| 再建一个 Agent | 有子 Agent 就分出发题 / 评分；没有就同会话分角色，并在 FIDELITY.md 写明「未独立评分」 |
| 写产物 | 写到 `{pangu_output_root}/...`，不要猜用户家目录 |

## 5. 不要做的

- 不要为 Cursor / Codex 各维护一份 SKILL.md
- 不要把 `npx skills add` 当成全宿主安装器
- 不要先做每家一个 MCP Plugin（那是 Distilly 的产品形态）
