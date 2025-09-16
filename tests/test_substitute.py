from pathlib import Path

from emoji_sniper.core.substitute import Substitutor


def test_substitute_replaces_gaudy_and_respects_allowed(tmp_path: Path):
    vault = tmp_path / "vault"
    vault.mkdir()
    content = "⭐ Star ✨ brilliant and 🦙 and 🦙🦙🦙."
    f = vault / "a.md"
    f.write_text(content, encoding="utf-8")

    # Ban ranges covering: ⭐ (U+2B50), ✨ (U+2728), 🦙 (U+1F999)
    banned = tmp_path / "banned.txt"
    banned.write_text(
        "\n" "\\U00002B00-\\U00002BFF\n" "\\U00002700-\\U000027BF\n" "\\U0001F900-\\U0001FAFF\n",
        encoding="utf-8",
    )

    # Allow the phrase and the llama triplet
    allowed = tmp_path / "allowed.txt"
    allowed.write_text("✨ brilliant\n🦙🦙🦙\n", encoding="utf-8")

    subs = tmp_path / "subs.json"
    subs.write_text(
        '{"map": {"⭐": "*", "✨": "*", "🦙": "llama"}, "regex": [{"pattern": "(?:\\u2728) +brilliant", "replacement": "brilliant"}]}',
        encoding="utf-8",
    )

    subber = Substitutor(
        vault_path=vault,
        banned_path=banned,
        subs_path=subs,
        allowed_path=allowed,
        exclude_patterns=set(),
        extensions={".md"},
    )

    stats = subber.run(dry_run=False)

    # ✨ brilliant is allowed, so it remains; ⭐ → *, single 🦙 → llama; triplet unchanged
    result = f.read_text(encoding="utf-8").rstrip("\n")
    assert result == "* Star ✨ brilliant and llama and 🦙🦙🦙."
    assert stats.files_changed == 1
    assert stats.replacements >= 2


def test_substitute_regex_applies_when_not_allowed(tmp_path: Path):
    vault = tmp_path / "vault"
    vault.mkdir()
    f = vault / "n.md"
    f.write_text("✨   brilliant idea", encoding="utf-8")

    banned = tmp_path / "banned.txt"
    banned.write_text("\\U00002700-\\U000027BF\n", encoding="utf-8")

    subs = tmp_path / "subs.json"
    subs.write_text(
        '{"map": {"✨": "*"}, "regex": [{"pattern": "(?:\\u2728) +brilliant", "replacement": "brilliant"}]}',
        encoding="utf-8",
    )

    subber = Substitutor(
        vault_path=vault,
        banned_path=banned,
        subs_path=subs,
        allowed_path=None,
        exclude_patterns=set(),
        extensions={".md"},
    )

    stats = subber.run(dry_run=False)
    result = f.read_text(encoding="utf-8").rstrip("\n")
    assert result == "brilliant idea"
    assert stats.replacements >= 1
