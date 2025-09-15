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
