#!/usr/bin/env python3
"""
盘古蒸馏 CLI

采集流程：plan（出查询计划）→ 宿主 Agent 搜索 → ingest（落底稿）→ check（校验产物）。
plan / check / fidelity / output-root / skill-root 只用标准库；ingest / search / fetch 需要 requests + bs4。
"""

import argparse
import json
import sys
from pathlib import Path


def _die(message: str, code: int = 2) -> int:
    print(f"❌ {message}", file=sys.stderr)
    return code


# ---------------------------------------------------------------------------
# plan
# ---------------------------------------------------------------------------


def cmd_plan(args):
    from distill.dimensions import SelfKindError, UnknownKindError
    from distill.plan import build_plan, parse_dimension_args

    try:
        plan = build_plan(
            args.target,
            kind=args.kind,
            num_results=args.num,
            output_dir=Path(args.output) if args.output else None,
            dimensions=parse_dimension_args(args.dimensions, args.target),
        )
    except SelfKindError as exc:
        return _die(f"{exc}", 2)
    except (UnknownKindError, ValueError) as exc:
        return _die(str(exc), 2)

    if args.output:
        path = plan.save(Path(args.output))
        if args.format == "json":
            print(json.dumps(plan.to_dict(), ensure_ascii=False, indent=2))
        else:
            print(plan.to_markdown())
        print(f"📝 计划已写入: {path}", file=sys.stderr)
        print(
            f"下一步：宿主搜索后写 {Path(args.output) / 'results.json'}，再跑\n"
            f"  run.py ingest --plan \"{path}\" \"{Path(args.output) / 'results.json'}\"",
            file=sys.stderr,
        )
    elif args.format == "json":
        print(json.dumps(plan.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(plan.to_markdown())
    return 0


# ---------------------------------------------------------------------------
# ingest
# ---------------------------------------------------------------------------


def cmd_ingest(args):
    from distill.dimensions import EMPTY_COLLECTION_HINT
    from distill.ingest import ingest, load_results
    from distill.plan import build_plan, load_plan

    results_path = Path(args.results)
    if not results_path.is_file():
        return _die(f"找不到 results 文件: {results_path}")

    if args.plan:
        plan_path = Path(args.plan)
        if not plan_path.is_file():
            return _die(f"找不到 plan 文件: {plan_path}")
        plan = load_plan(plan_path)
    else:
        if not args.target:
            return _die("没有 --plan 时必须给 --target（并可给 --kind）")
        plan = build_plan(args.target, kind=args.kind)

    output_dir = Path(args.output) if args.output else (Path(plan.output_dir) if plan.output_dir else results_path.parent)

    try:
        raw_items = load_results(results_path)
    except ValueError as exc:
        return _die(f"results 格式错误: {exc}")

    print(f"📥 ingest: {plan.target}（{plan.kind}）")
    print(f"   输入 {len(raw_items)} 条 · 输出目录 {output_dir}")

    summary = ingest(
        plan,
        raw_items,
        output_dir,
        fetch=not args.no_fetch,
        max_workers=args.workers,
        excerpt_chars=args.excerpt,
        max_chars=args.max_chars,
    )

    print(f"   保留 {summary.kept} 条 · 一手占比 {summary.primary_ratio:.0%}")
    print(f"   剔除：黑名单 {summary.dropped_blacklist} · 无效 {summary.dropped_invalid} · 重复 {summary.duplicates}")
    if not args.no_fetch:
        print(f"   抓取：成功 {summary.fetched_ok} · 失败 {summary.fetch_failed}")
    for dim, n in summary.by_dimension.items():
        print(f"   - {dim}: {n}")
    if summary.empty_dimensions:
        print(f"   空维度: {', '.join(summary.empty_dimensions)}")
    for w in summary.warnings:
        print(f"   ⚠️ {w}")
    print(f"   写入: {', '.join(summary.files_written)}")

    if not summary.success:
        print("\n❌ 0 条可用素材")
        print(EMPTY_COLLECTION_HINT)
        return 2
    print("\n✅ ingest 完成。下一步：读 0N-*.md 做七级提取，写 08-extraction-notes.md / 09-key-quotes.md")
    return 0


# ---------------------------------------------------------------------------
# check
# ---------------------------------------------------------------------------


def cmd_check(args):
    from distill.check import run_check

    report = run_check(
        Path(args.skill_dir),
        require_fidelity=args.require_fidelity,
        quick=args.quick,
        kind=args.kind,
    )
    if args.json:
        print(json.dumps(report.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(report.to_text())
    return 0 if report.passed else 1


# ---------------------------------------------------------------------------
# fidelity（测试包：出题 / 答题 / 评分三方分离）
# ---------------------------------------------------------------------------


def cmd_fidelity(args):
    from distill import fidelity as fid

    skill_dir = Path(args.skill_dir)
    if not (skill_dir / "SKILL.md").is_file():
        return _die(f"{skill_dir} 里没有 SKILL.md，先构建再出题")

    if args.action == "init":
        target = args.target
        if not target:
            from distill.markdown import parse_frontmatter
            import re

            _, body = parse_frontmatter((skill_dir / "SKILL.md").read_text(encoding="utf-8", errors="replace"))
            h1 = re.search(r"^#\s+(.+?)\s*$", body, re.MULTILINE)
            target = re.split(r"[·:：—|]", h1.group(1))[0].strip() if h1 else skill_dir.name
        written, skipped = fid.init_packet(skill_dir, target, aliases=args.alias or (), kind=args.kind, force=args.force)
        for p in written:
            print(f"📝 {p}")
        for p in skipped:
            print(f"⏭️  已存在，未覆盖：{p}（--force 覆盖）")
        print()
        print(fid.role_prompts(skill_dir))
        return 0

    if args.action == "blind":
        report: dict = {}
        try:
            out, count, names = fid.blind_answers(
                skill_dir, extra_aliases=args.alias or (), expand=not args.no_expand, report=report
            )
        except FileNotFoundError as exc:
            return _die(str(exc))
        print(f"🕶️  {out}")
        print(f"   遮掉 {count} 处：{'、'.join(names[:8])}")
        auto = report.get("auto") or []
        if auto:
            print(f"   自动补的简称 / 变体 {len(auto)} 个：{'、'.join(auto)}（不想要就加 --no-expand，或在 questions.md aliases 里明写）")
        suspects = report.get("suspects") or []
        if suspects:
            print(f"   ⚠️ 遮完仍像实体名的词（脚本只报不遮，该遮的写进 aliases 后重跑）：{'、'.join(suspects)}")
        if count == 0:
            print("   ⚠️ 一处都没遮到：答题里没出现对象名，或名字没写进 questions.md 的 target / aliases（可用 --alias 补）")
        print("   下一步：把这份复制到不含对象名的临时目录给评分 Agent 先读，盲读记录按 (a) 未遮实体 / (b) 年份典故 / (c) 句法 三类给比例，")
        print("           再读 answers.md / rubric.md / Skill")
        return 0

    return _die(f"未知动作 {args.action}")


# ---------------------------------------------------------------------------
# search / fetch（保底工具，不是主路径）
# ---------------------------------------------------------------------------


def cmd_search(args):
    from crawl.chain import CrawlerSearch

    chain = CrawlerSearch()
    queries = args.query if isinstance(args.query, list) else [args.query]
    print(f"🔍 保底搜索 {len(queries)} 个查询（主路径应用宿主搜索工具）...")

    total = 0
    for query in queries:
        results = chain.search(query, args.num)
        total += len(results)
        print(f"\n{'=' * 60}")
        print(f"查询: {query}")
        print(f"结果: {len(results)} 条")
        for err in chain.last_errors:
            print(f"  跳过: {err}")
        print("=" * 60)
        for j, r in enumerate(results[: args.num]):
            print(f"\n[{j + 1}] {r.title}")
            print(f"    URL: {r.url}")
            print(f"    摘要: {r.snippet[:100]}...")
            print(f"    来源: {r.source.value}")
    return 0 if total else 2


def cmd_fetch(args):
    from crawl.fetcher import ContentFetcher

    fetcher = ContentFetcher()
    urls = args.url if isinstance(args.url, list) else [args.url]
    print(f"📥 抓取 {len(urls)} 个 URL...")

    ok = 0
    for url in urls:
        print(f"\n{'=' * 60}")
        try:
            c = fetcher.fetch(url)
        except RuntimeError as exc:
            print(f"URL: {url}\n失败: {exc}")
            continue
        ok += 1
        print(f"标题: {c.title}")
        print(f"URL: {c.url}")
        print(f"字数: {c.word_count}")
        print(f"语言: {c.language.value}")
        print("-" * 60)
        print(c.content[:500] + "..." if len(c.content) > 500 else c.content)
    return 0 if ok else 2


# ---------------------------------------------------------------------------
# transcribe / collect-local
# ---------------------------------------------------------------------------


def cmd_transcribe(args):
    from transcribe import YouTubeTranscriber, AudioTranscriber, is_youtube_url

    url = args.url
    output_dir = args.output or "./transcripts"
    print(f"🎬 开始转录: {url}")

    if is_youtube_url(url):
        print("📺 检测到 YouTube 视频")
        yt = YouTubeTranscriber(output_dir=output_dir)
        result = yt.get_subtitle(url)
        if result.subtitles:
            print(f"✅ 获取到 {len(result.subtitles)} 个字幕")
            for sub in result.subtitles:
                print(f"   语言: {sub['lang']}, 类型: {sub['type']}")
                print(f"   内容预览: {sub['content'][:100]}...")
            if result.file_path:
                print(f"\n📁 字幕文件: {result.file_path}")
            return 0
        print("⚠️ 无字幕可用，尝试音频转录...")

    transcriber = AudioTranscriber(model=args.model or "base", output_dir=output_dir)
    text = transcriber.transcribe_youtube(url) if is_youtube_url(url) else transcriber.transcribe(url)

    print("\n✅ 转录完成")
    print(f"   字数: {len(text)}")
    print("\n内容预览:")
    print("-" * 60)
    print(text[:500] + "..." if len(text) > 500 else text)
    return 0


def cmd_collect_local(args):
    from distill.local import MaterialCollector

    collector = MaterialCollector(transcript_enabled=not args.no_transcribe)
    paths = args.paths if isinstance(args.paths, list) else [args.paths]

    print(f"📂 开始采集 {len(paths)} 个素材...\n")
    result = collector.collect(paths)

    print("=" * 60)
    print("✅ 采集完成" if result.successful else "❌ 没有成功读取任何素材")
    print("=" * 60)
    print(f"   总文件数: {result.total_files}")
    print(f"   成功: {result.successful}")
    print(f"   失败: {result.failed}")
    print(f"   总字数: {result.total_words:,}\n")

    for mat in result.materials:
        status = "✅" if mat.success else "❌"
        print(f"{status} [{mat.material_type.value}] {Path(mat.path).name}")
        if mat.success:
            print(f"   标题: {mat.title or 'N/A'}")
            print(f"   字数: {mat.word_count:,}")
            print(f"   语言: {mat.language.value}")
            if args.verbose and mat.content:
                preview = mat.content[:200].replace("\n", " ")
                print(f"   预览: {preview}...")
        else:
            print(f"   错误: {mat.error}")
        print("")

    if args.output:
        output_dir = Path(args.output)
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(output_dir / "collection_result.json", "w", encoding="utf-8") as f:
            json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)
        for i, mat in enumerate(result.materials):
            if mat.success and mat.content:
                ext = Path(mat.path).suffix
                name = f"content_{i + 1}{ext if ext in ('.txt', '.md') else '.txt'}"
                (output_dir / name).write_text(mat.content, encoding="utf-8")
        print(f"💾 结果已保存到: {output_dir}")

    return 0 if result.successful else 2


# ---------------------------------------------------------------------------
# 路径
# ---------------------------------------------------------------------------


def cmd_output_root(args):
    from host_paths import detect_output_root, skill_output_dir

    root = detect_output_root()
    if args.slug:
        try:
            print(skill_output_dir(args.slug, root))
        except ValueError as exc:
            return _die(str(exc))
    else:
        print(root)
    return 0


def cmd_skill_root(args):
    from host_paths import detect_skill_root

    root = detect_skill_root()
    if root is None:
        return _die("未检测到 PANGU_SKILL_ROOT / CLAUDE_SKILL_DIR / CODEX_SKILL_DIR / CURSOR_SKILL_DIR")
    print(root)
    return 0


# ---------------------------------------------------------------------------
# parser
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="盘古蒸馏采集工具：plan → 宿主搜索 → ingest → check",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", help="子命令")

    p = sub.add_parser("plan", help="出六路查询计划（不联网），交给宿主 Agent 搜索")
    p.add_argument("target", help="蒸馏对象，如 芒格 / Jeff Bezos / 第一性原理")
    p.add_argument("--kind", default="person", help="person/content/idea/phenomenon（D1–D4）；D5 自我请用 collect-local")
    p.add_argument("-n", "--num", type=int, default=8, help="每路目标条数（默认 8）")
    p.add_argument("-d", "--dimensions", nargs="+", help="覆盖维度：name:query_template 或 name")
    p.add_argument("-o", "--output", help="写 plan.json 到该目录（通常是 references/distillation/）")
    p.add_argument("--format", choices=["md", "json"], default="md", help="stdout 格式（默认 md）")
    p.set_defaults(func=cmd_plan)

    p = sub.add_parser("ingest", help="把宿主搜到的 results.json 落成 00–07 底稿")
    p.add_argument("results", help="results.json（格式见 plan 输出的 results_template）")
    p.add_argument("--plan", help="plan.json 路径；不给则用 --target/--kind 现场生成")
    p.add_argument("--target", help="对象（无 plan 时必填）")
    p.add_argument("--kind", default="person", help="类型（无 plan 时用）")
    p.add_argument("-o", "--output", help="输出目录，默认 plan.output_dir 或 results 所在目录")
    p.add_argument("--no-fetch", action="store_true", help="不抓正文，只落来源表")
    p.add_argument("-w", "--workers", type=int, default=5, help="抓取并发（默认 5）")
    p.add_argument("--excerpt", type=int, default=1500, help="底稿里每条摘录字数（默认 1500）")
    p.add_argument("--max-chars", type=int, default=20000, help="ingest_result.json 里每条正文上限（默认 20000）")
    p.set_defaults(func=cmd_ingest)

    p = sub.add_parser("check", help="机器校验产物目录：命名 / 4.5 层 / 证据三件套 / FIDELITY")
    p.add_argument("skill_dir", help="产物目录，如 .agents/skills/pangu-leijun")
    p.add_argument("--require-fidelity", action="store_true", help="Phase 3 出厂：FIDELITY.md 必须存在且 ≥80")
    p.add_argument("--quick", action="store_true", help="快速版：允许 2 个心智模型")
    p.add_argument("--kind", choices=["person", "self", "generic"], help="覆盖自动推断的类型")
    p.add_argument("--json", action="store_true", help="JSON 输出")
    p.set_defaults(func=cmd_check)

    p = sub.add_parser("fidelity", help="保真度测试包：init 出题模板 / blind 遮名给评分 Agent 盲读")
    p.add_argument("action", choices=["init", "blind"], help="init：写 fidelity/questions|rubric|answers 模板；blind：生成 answers.blind.md")
    p.add_argument("skill_dir", help="产物目录，如 .agents/skills/pangu-leijun")
    p.add_argument("--target", help="对象名（init；默认取 SKILL.md 一级标题）")
    p.add_argument("--alias", action="append", help="对象别名，可重复（init 写进 questions.md；blind 额外遮掉）")
    p.add_argument("--no-expand", action="store_true", help="blind：不自动补简称 / 去分隔符 / 拉丁姓等变体，只遮 aliases 原文")
    p.add_argument("--kind", default="person", help="person/content/idea/phenomenon（init）")
    p.add_argument("--force", action="store_true", help="init 覆盖已有模板")
    p.set_defaults(func=cmd_fidelity)

    p = sub.add_parser("search", help="保底搜索（DuckDuckGo → 维基），主路径请用宿主搜索")
    p.add_argument("query", nargs="+", help="搜索查询")
    p.add_argument("-n", "--num", type=int, default=10, help="每查询结果数 (默认: 10)")
    p.set_defaults(func=cmd_search)

    p = sub.add_parser("fetch", help="抓取 URL 正文")
    p.add_argument("url", nargs="+", help="URL 列表")
    p.set_defaults(func=cmd_fetch)

    p = sub.add_parser("transcribe", help="音视频转录")
    p.add_argument("url", help="YouTube URL 或本地音频路径")
    p.add_argument("-o", "--output", help="输出目录")
    p.add_argument("-m", "--model", choices=["tiny", "base", "small", "medium", "large"], help="Whisper 模型")
    p.set_defaults(func=cmd_transcribe)

    p = sub.add_parser("collect-local", help="采集本地素材（PDF/Word/TXT/MD/Excel/字幕/音视频/URL）")
    p.add_argument("paths", nargs="+", help="文件路径或 URL 列表")
    p.add_argument("-o", "--output", help="输出目录")
    p.add_argument("-v", "--verbose", action="store_true", help="显示详细内容")
    p.add_argument("--no-transcribe", action="store_true", help="跳过音视频转录")
    p.set_defaults(func=cmd_collect_local)

    p = sub.add_parser("output-root", help="打印蒸馏产物应写入的项目 skills 目录")
    p.add_argument("--slug", help="附带 skill 目录名，例如 pangu-buffett")
    p.set_defaults(func=cmd_output_root)

    p = sub.add_parser("skill-root", help="打印宿主注入的本 Skill 根目录")
    p.set_defaults(func=cmd_skill_root)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 1
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
