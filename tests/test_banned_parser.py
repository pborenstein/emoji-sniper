from pathlib import Path
import tempfile

from scanner.banned_parser import parse_banned_file, build_regex


def write(tmpdir: Path, name: str, content: str) -> Path:
    p = tmpdir / name
    p.write_text(content, encoding="utf-8")
    return p


def test_parse_ranges_and_literals(tmp_path: Path):
    data = """
    # Emoji range
    \U0001F600-\U0001F603
    # Literal line
    ✅❌
    """
    banned = write(tmp_path, "banned.txt", data)

    spec = parse_banned_file(banned)
    assert spec.ranges, "Expected at least one range"
    assert "✅" in spec.literals and "❌" in spec.literals

    pattern = build_regex(spec)
    assert pattern.search("Hello 😀"), "Should match char in range"
    assert not pattern.search("Hello A"), "Should not match ASCII letter"

