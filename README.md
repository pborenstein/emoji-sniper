# emoji-sniper

Scan files and folders (Obsidian vaults or any text repo) for banned characters or Unicode ranges defined in `banned.txt`. Outputs JSON (default) or human-readable text, with rotating logs written to `log/emoji-sniper.log`.

```
┌───────────────┐     ┌──────────────────┐     ┌────────────────────┐
│  Files/Dirs   │ ─▶─ │  Regex (banned)  │ ─▶─ │  Occurrences JSON  │
│  (.md, .txt)  │     │  ranges + chars  │     │  + text summary    │
└───────────────┘     └──────────────────┘     └────────────────────┘
         ▲                         │                     │
         │                         ▼                     ▼
   Excludes (via             Name lookup           Report files (*.json)
   repeated --exclude)       (default on)          and rotating logs
```

## Quick Start
- Install with uv (editable):
  - `uv sync --group dev`
  - `uv tool install --editable .`
- Run a scan (JSON):
  - `emoji-sniper scan /path/to/vault --banned banned.txt`
  - Save a report file: `emoji-sniper scan ./vault --report --report-dir log`
  - Fail on any find: `emoji-sniper scan ./vault --fail-on-find`
  - List files with matches: `emoji-sniper scan ./vault --list-files`
- Text + summary:
  - `emoji-sniper scan ./vault --format txt -v`
- Run tests:
  - `uv run pytest`

## CLI Overview
- `scan VAULT_PATH` — scan files for banned characters (accepts a directory or a single file)
  - `--banned banned.txt` path to the banned list
  - `--ext .md,.txt` comma-separated extensions to include
  - `--exclude pattern` repeatable glob/substring excludes (e.g., `.obsidian/*`); no defaults are applied unless you pass patterns
  - `--no-names` skip Unicode names (names included by default)
  - `--report` write a timestamped JSON report (to `--report-dir`, default `log/`)
  - `--report-dir PATH` destination directory for reports
  - `--report-prefix NAME` filename prefix (default `emoji-scan`)
  - `--fail-on-find` return exit code 1 if any matches found
  - `--list-files` print only unique file paths that contain matches
  - `--quiet` suppress the text summary (text mode only)
  - `-v|-vv` increase verbosity (also logged to file)

- `substitute` — stub/not implemented yet
  - Present for future substitutions feature; currently prints an error and exits with code 2
  - Planned usage shape: `emoji-sniper substitute VAULT_PATH --map MAP.json [--dry-run]`

## Project Layout
```
emoji-sniper/
├─ main.py                  # CLI (argparse)
├─ scanner/
│  ├─ core.py               # SniperScanner + Occurrence
│  ├─ banned_parser.py      # Parse banned.txt, build regex
│  └─ output.py             # JSON/text formatting
├─ utils/
│  ├─ file_discovery.py     # Walk files (ext + excludes)
│  └─ logging_setup.py      # Console + rotating file logs
├─ tests/                   # Pytest suite
├─ doc/                     # Architecture notes
└─ banned.txt               # Example banlist (ranges + literals)
```

## Banned List Format
- Unicode ranges: `\U0001F600-\U0001F64F`
- Literal characters on a line: `✅❌`
- Lines starting with `#` are comments; blanks ignored
