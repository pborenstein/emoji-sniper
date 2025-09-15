from pathlib import Path

from scanner.core import SniperScanner


def test_allowed_triplet_llama_suppresses(tmp_path: Path):
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "a.md").write_text("ok 🦙🦙🦙 here", encoding="utf-8")

    banned = tmp_path / "banned.txt"
    # Range that includes llama (U+1F999); using broad supplemental range
    banned.write_text("\n\\U0001F900-\\U0001FAFF\n", encoding="utf-8")

    allowed = tmp_path / "allowed.txt"
    allowed.write_text("🦙🦙🦙\n", encoding="utf-8")

    scanner = SniperScanner(
        vault_path=vault,
        banned_path=banned,
        allowed_path=allowed,
        exclude_patterns=set(),
        extensions={".md"},
        include_names=False,
    )

    results, stats = scanner.scan()
    assert stats["files_scanned"] == 1
    assert stats["occurrences"] == 0
    assert results == []


def test_single_llama_still_banned(tmp_path: Path):
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "note.md").write_text("one 🦙 not allowed", encoding="utf-8")

    banned = tmp_path / "banned.txt"
    banned.write_text("\n\\U0001F900-\\U0001FAFF\n", encoding="utf-8")

    allowed = tmp_path / "allowed.txt"
    allowed.write_text("🦙🦙🦙\n", encoding="utf-8")

    scanner = SniperScanner(
        vault_path=vault,
        banned_path=banned,
        allowed_path=allowed,
        exclude_patterns=set(),
        extensions={".md"},
        include_names=False,
    )

    results, stats = scanner.scan()
    assert stats["occurrences"] == 1
    assert any(r.char == "🦙" for r in results)

