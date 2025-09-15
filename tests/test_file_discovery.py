from pathlib import Path

from utils.file_discovery import find_files


def test_find_files_with_excludes_and_exts(tmp_path: Path):
    # Layout
    (tmp_path / ".git").mkdir()
    (tmp_path / "node_modules").mkdir()
    (tmp_path / "notes").mkdir()
    (tmp_path / "notes" / "ok.md").write_text("hi", encoding="utf-8")
    (tmp_path / "notes" / "skip.txt~").write_text("tmp", encoding="utf-8")
    (tmp_path / "notes" / "skip.bin").write_text("x", encoding="utf-8")
    (tmp_path / "notes" / "inner").mkdir()
    (tmp_path / "notes" / "inner" / "ok.txt").write_text("hello", encoding="utf-8")
    # custom exclude
    (tmp_path / "private").mkdir()
    (tmp_path / "private" / "secret.md").write_text("shh", encoding="utf-8")

    res = find_files(
        tmp_path,
        extensions={".md", ".txt"},
        exclude_patterns={"private/*"},
    )
    paths = {p.relative_to(tmp_path).as_posix() for p in res}
    assert "notes/ok.md" in paths
    assert "notes/inner/ok.txt" in paths
    assert not any(".git" in p for p in paths)
    assert not any("node_modules" in p for p in paths)
    assert "private/secret.md" not in paths

