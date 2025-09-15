from pathlib import Path

from scanner.core import SniperScanner


def test_scanner_finds_occurrences(tmp_path: Path):
    # Prepare vault
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "a.md").write_text("Hello 😀 world", encoding="utf-8")
    (vault / "b.txt").write_text("No emoji here", encoding="utf-8")

    banned = tmp_path / "banned.txt"
    banned.write_text("\n\U0001F600-\U0001F64F\n", encoding="utf-8")

    scanner = SniperScanner(
        vault_path=vault,
        banned_path=banned,
        exclude_patterns=set(),
        extensions={".md", ".txt"},
        include_names=False,
    )

    results, stats = scanner.scan()
    assert stats["files_scanned"] == 2
    assert stats["occurrences"] >= 1
    files = {r.file for r in results}
    assert str(vault / "a.md") in files

