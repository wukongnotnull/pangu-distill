from pathlib import Path

from host_paths import (
    detect_output_root,
    detect_skill_root,
    find_project_root,
    skill_output_dir,
)


def test_find_project_root_uses_git(tmp_path: Path):
    (tmp_path / ".git").mkdir()
    nested = tmp_path / "a" / "b"
    nested.mkdir(parents=True)
    assert find_project_root(nested) == tmp_path


def test_output_root_prefers_existing_agents_dir(tmp_path: Path):
    (tmp_path / ".git").mkdir()
    (tmp_path / ".claude" / "skills").mkdir(parents=True)
    (tmp_path / ".agents" / "skills").mkdir(parents=True)
    root = detect_output_root(cwd=tmp_path / "pkg", env={})
    assert root == tmp_path / ".agents" / "skills"


def test_output_root_falls_back_to_claude(tmp_path: Path):
    (tmp_path / ".git").mkdir()
    (tmp_path / ".claude" / "skills").mkdir(parents=True)
    root = detect_output_root(cwd=tmp_path, env={})
    assert root == tmp_path / ".claude" / "skills"


def test_output_root_default_agents_when_none(tmp_path: Path):
    (tmp_path / ".git").mkdir()
    root = detect_output_root(cwd=tmp_path, env={})
    assert root == tmp_path / ".agents" / "skills"


def test_output_root_env_override(tmp_path: Path):
    dest = tmp_path / "custom"
    root = detect_output_root(cwd=tmp_path, env={"PANGU_OUTPUT_ROOT": str(dest)})
    assert root == dest


def test_skill_root_env_order():
    env = {
        "PANGU_SKILL_ROOT": "/tmp/pangu",
        "CLAUDE_SKILL_DIR": "/tmp/claude",
    }
    assert detect_skill_root(env) == Path("/tmp/pangu")
    assert detect_skill_root({"CLAUDE_SKILL_DIR": "/tmp/claude"}) == Path("/tmp/claude")
    assert detect_skill_root({}) is None


def test_skill_output_dir_appends_slug(tmp_path: Path):
    assert skill_output_dir("pangu-foo-distill", tmp_path) == tmp_path / "pangu-foo-distill"
