# codex-sniper

Scan files (e.g., an Obsidian vault) for banned characters or Unicode ranges defined in `banned.txt`. Outputs JSON (default) or human-readable text, with rotating logs written to `log/codex-sniper.log`.

## Quick Start
- Install with uv (editable):
  - `uv sync --group dev`
  - `uv tool install --editable .`
- Run a scan (JSON):
  - `emoji-sniper scan /path/to/vault --banned banned.txt`
  - Save a report file: `emoji-sniper scan ./vault --report --report-dir log`
- Text + summary:
  - `emoji-sniper scan ./vault --format txt -v`
- Run tests:
  - `uv run pytest`

## CLI Overview
- `scan VAULT_PATH` — scan files for banned characters
  - `--banned banned.txt` path to the banned list
  - `--ext .md,.txt` comma-separated extensions to include
  - `--exclude pattern` repeatable glob/substring excludes (e.g., `.obsidian/*`)
  - `--names` include Unicode names (slower)
  - `--report` write a timestamped JSON report (to `--report-dir`, default `log/`)
  - `--report-dir PATH` destination directory for reports
  - `--report-prefix NAME` filename prefix (default `emoji-scan`)
  - `-v|-vv` increase verbosity (also logged to file)

## Project Layout
- `main.py` — CLI entry (argparse)
- `scanner/core.py` — SniperScanner and occurrence model
- `scanner/banned_parser.py` — parse `banned.txt` and build regex
- `scanner/output.py` — JSON/text formatting
- `utils/file_discovery.py` — recursive file finder with excludes
- `utils/logging_setup.py` — console + rotating file logging
- `tests/` — pytest suite
- `doc/` — architecture and implementation notes

## Banned List Format
- Unicode ranges: `\U0001F600-\U0001F64F`
- Literal characters on a line: `✅❌`
- Lines starting with `#` are comments; blanks ignored
