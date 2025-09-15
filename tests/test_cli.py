from pathlib import Path
import json

from main import main


def test_cli_scan_json_output(tmp_path: Path, capsys):
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "file.md").write_text("Hi 😀", encoding="utf-8")
    banned = tmp_path / "banned.txt"
    banned.write_text("\\U0001F600-\\U0001F64F\n", encoding="utf-8")

    code = main([
        "scan",
        str(vault),
        "--banned",
        str(banned),
        "--format",
        "json",
    ])
    assert code == 0
    out = capsys.readouterr().out
    payload = json.loads(out)
    assert payload["stats"]["occurrences"] >= 1
    assert any(r["file"].endswith("file.md") for r in payload["results"])  # sanity


def test_cli_includes_names_by_default(tmp_path: Path, capsys):
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "file.md").write_text("Hi 😀", encoding="utf-8")
    banned = tmp_path / "banned.txt"
    banned.write_text("\\U0001F600-\\U0001F64F\n", encoding="utf-8")

    code = main([
        "scan",
        str(vault),
        "--banned",
        str(banned),
        "--format",
        "json",
    ])
    assert code == 0
    out = capsys.readouterr().out
    payload = json.loads(out)
    result = payload["results"][0]
    assert "name" in result and isinstance(result["name"], str)



def test_cli_writes_report(tmp_path: Path, capsys):
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "f.md").write_text("Hi 😀", encoding="utf-8")
    banned = tmp_path / "banned.txt"
    banned.write_text("\\U0001F600-\\U0001F64F\n", encoding="utf-8")

    code = main([
        "scan",
        str(vault),
        "--banned",
        str(banned),
        "--format",
        "json",
        "--report",
        "--report-dir",
        str(tmp_path),
        "--report-prefix",
        "emoji-scan-test",
    ])
    assert code == 0

    # Find the report file
    reports = sorted(p for p in tmp_path.glob("emoji-scan-test_*.json"))
    assert reports, "Expected a timestamped report file"
    data = json.loads(reports[-1].read_text(encoding="utf-8"))
    assert data["stats"]["occurrences"] >= 1


def test_cli_fail_on_find(tmp_path: Path, capsys):
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "x.md").write_text("One 😀", encoding="utf-8")
    banned = tmp_path / "banned.txt"
    banned.write_text("\\U0001F600-\\U0001F64F\n", encoding="utf-8")

    code = main([
        "scan",
        str(vault),
        "--banned",
        str(banned),
        "--fail-on-find",
        "--format",
        "json",
    ])
    assert code == 1


def test_cli_list_files_unique(tmp_path: Path, capsys):
    vault = tmp_path / "vault"
    vault.mkdir()
    (vault / "a.md").write_text("😀😀", encoding="utf-8")
    (vault / "b.txt").write_text("nope", encoding="utf-8")
    banned = tmp_path / "banned.txt"
    banned.write_text("\\U0001F600-\\U0001F64F\n", encoding="utf-8")

    code = main([
        "scan",
        str(vault),
        "--banned",
        str(banned),
        "--list-files",
    ])
    assert code == 0
    out = capsys.readouterr().out.strip().splitlines()
    assert len(out) == 1
    assert out[0].endswith("a.md")


def test_cli_accepts_single_file(tmp_path: Path, capsys):
    file_path = tmp_path / "has-emojis.md"
    file_path.write_text("Text 😀 here", encoding="utf-8")
    banned = tmp_path / "banned.txt"
    banned.write_text("\\U0001F600-\\U0001F64F\n", encoding="utf-8")

    code = main([
        "scan",
        str(file_path),
        "--banned",
        str(banned),
        "--list-files",
    ])
    assert code == 0
    out = capsys.readouterr().out.strip().splitlines()
    assert out == [str(file_path)]
