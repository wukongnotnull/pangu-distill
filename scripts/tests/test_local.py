from pathlib import Path

from distill.local import Material, MaterialCollector, MaterialType


def test_detect_type():
    c = MaterialCollector()
    assert c._detect_type("https://example.com") == MaterialType.URL
    assert c._detect_type("www.example.com") == MaterialType.URL
    assert c._detect_type("/some/missing.xyz") == MaterialType.UNKNOWN


def test_collect_txt_and_subtitle(tmp_path: Path):
    txt = tmp_path / "notes.txt"
    txt.write_text("我以前觉得快就是好，后来发现慢一点问题才露出来。", encoding="utf-8")
    srt = tmp_path / "talk.srt"
    srt.write_text("1\n00:00:01,000 --> 00:00:03,000\n专注 极致 口碑 快\n\n2\n00:00:04,000 --> 00:00:05,000\n少即是多\n", encoding="utf-8")

    result = MaterialCollector(transcript_enabled=False).collect([str(txt), str(srt), str(tmp_path / "missing.pdf")])
    assert result.total_files == 3
    assert result.successful == 2
    assert result.failed == 1
    by_name = {Path(m.path).name: m for m in result.materials}
    assert by_name["notes.txt"].language.value == "zh"
    assert "-->" not in by_name["talk.srt"].content
    assert "少即是多" in by_name["talk.srt"].content
    assert by_name["missing.pdf"].success is False
    assert by_name["missing.pdf"].error


def test_collect_single_never_raises(tmp_path: Path):
    c = MaterialCollector()
    m = c._collect_single("not-a-valid-path", False)
    assert isinstance(m, Material)
    assert m.success is False and m.error
    media = c._collect_single(str(tmp_path / "x.mp3"), False)
    assert media.material_type == MaterialType.UNKNOWN or media.error
