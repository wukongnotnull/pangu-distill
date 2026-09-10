import json
from pathlib import Path

import cli


def test_plan_writes_file_and_returns_zero(tmp_path: Path, capsys):
    rc = cli.main(["plan", "雷军", "--kind", "person", "-o", str(tmp_path), "--format", "json"])
    assert rc == 0
    out = capsys.readouterr().out
    data = json.loads(out)
    assert data["target"] == "雷军"
    assert (tmp_path / "plan.json").is_file()


def test_plan_self_exits_two(capsys):
    assert cli.main(["plan", "我", "--kind", "self"]) == 2
    assert "collect-local" in capsys.readouterr().err


def test_ingest_then_check(tmp_path: Path, capsys):
    assert cli.main(["plan", "雷军", "-o", str(tmp_path)]) == 0
    (tmp_path / "results.json").write_text(
        json.dumps({"results": [{"dimension": "writings", "url": "https://a.example/1", "source_type": "primary"}]}),
        encoding="utf-8",
    )
    rc = cli.main(["ingest", "--plan", str(tmp_path / "plan.json"), str(tmp_path / "results.json"), "--no-fetch"])
    assert rc == 0
    assert (tmp_path / "00-sources.md").is_file()
    capsys.readouterr()

    empty = tmp_path / "empty.json"
    empty.write_text("[]", encoding="utf-8")
    rc = cli.main(["ingest", "--plan", str(tmp_path / "plan.json"), str(empty), "--no-fetch", "-o", str(tmp_path / "empty")])
    assert rc == 2
    assert "0 条可用素材" in capsys.readouterr().out


def test_ingest_without_plan_needs_target(tmp_path: Path):
    results = tmp_path / "r.json"
    results.write_text("[]", encoding="utf-8")
    assert cli.main(["ingest", str(results), "--no-fetch"]) == 2
    assert cli.main(["ingest", str(results), "--no-fetch", "--target", "雷军", "-o", str(tmp_path / "o")]) == 2  # 0 条
    assert (tmp_path / "o" / "00-sources.md").is_file()


def test_check_cli_exit_codes(tmp_path: Path, capsys):
    bad = tmp_path / "pangu-bad"
    bad.mkdir()
    assert cli.main(["check", str(bad)]) == 1
    capsys.readouterr()
    assert cli.main(["check", str(bad), "--json"]) == 1
    data = json.loads(capsys.readouterr().out)
    assert data["passed"] is False
    assert any(f["code"] == "skill-md" for f in data["findings"])


def test_no_command_prints_help(capsys):
    assert cli.main([]) == 1
    assert "plan" in capsys.readouterr().out


def test_run_py_resolves_relative_paths_from_caller_cwd(tmp_path: Path):
    """run.py 不能把 cwd 切到 scripts/，否则 `run.py check ./pangu-x` 会找错目录。"""
    import subprocess
    import sys

    run_py = Path(cli.__file__).resolve().parent / "run.py"
    proc = subprocess.run(
        [sys.executable, str(run_py), "plan", "雷军", "-o", "out", "--format", "json"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 0, proc.stderr
    assert (tmp_path / "out" / "plan.json").is_file()

    proc = subprocess.run(
        [sys.executable, str(run_py), "check", "out"],
        cwd=tmp_path,
        capture_output=True,
        text=True,
    )
    assert proc.returncode == 1
    assert "目录不存在" not in proc.stdout
