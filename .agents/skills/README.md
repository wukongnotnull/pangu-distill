# 跨宿主默认产出目录

本目录是 Codex / Cursor 都会扫描的项目级 skills 路径。盘古蒸馏在工作区里没有现成 skills 目录时，把成品写到这里。

安装本 meta-skill 到当前项目：

```bash
bash scripts/install-host.sh --project
```

不要把仓库根目录再套一层复制进来。`install-host.sh` 只做软链。

`pangu-first-principles-distill/` 是 2026-09-08 的实跑样本，评测见 `references/examples/live-test-first-principles.md`。
