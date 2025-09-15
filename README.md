# emoji-sniper

Extract, scan, and report banned characters (e.g., emoji) in Obsidian vaults or any text repo. The `emoji-sniper` CLI reads a banlist (`banned.txt`) of Unicode ranges and literal characters, then reports matches as JSON (default) or human-readable text. Logs are written to `log/emoji-sniper.log`.

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

## Quick start

- Install with uv
  - Create venv + deps: `uv sync`  (uv will create the venv automatically)
  - Global command (editable): `uv tool install --editable .`
- Sanity check CLI: `emoji-sniper --help`
- Scan to JSON: `emoji-sniper scan "$HOME/Obsidian/MyVault" --banned banned.txt`
- Allowlist sequences (optional): `emoji-sniper scan ./vault --banned banned.txt --allowed allowed.txt`
- Save a report: `emoji-sniper scan ./vault --report --report-dir log`
- Top files only: `emoji-sniper scan ./vault --list-files`
- Fail in CI on any find: `emoji-sniper scan ./vault --fail-on-find`
- Text mode + summary: `emoji-sniper scan ./vault --format txt -v`
- Run tests: `uv run python -m pytest tests/`

During development (no tool install):

```bash
# Scan
uv run python main.py scan /path/to/vault --banned banned.txt --format json

# Text mode
uv run python main.py scan ./vault --format txt -v

# Filter by extensions and exclude patterns
uv run python main.py scan ./vault --ext .md,.txt --exclude ".obsidian/*" --exclude node_modules/*

# Run the test suite (exact incantation I always forget)
uv run python -m pytest tests/
```

## Commands

```bash
# Scan a directory or single file
emoji-sniper scan /path/to/vault [options]

# Substitute (replace gaudy with plain)
emoji-sniper substitute /path/to/vault --banned banned.txt --allowed allowed.txt --map subs.json [--dry-run]
```

### scan options

- `--banned PATH`: Banlist file (default: `./banned.txt`)
- `--allowed PATH` (optional): Allowlist file of sequences/regex to permit; any banned match entirely within an allowed span is suppressed.
- `--format {json,txt}`: Output format (default: json)
- `--ext ".md,.txt"`: Comma-separated extensions to include
- `--exclude PATTERN`: Repeatable excludes (glob or substring). The CLI applies no defaults; pass patterns explicitly.
- `--no-names`: Skip Unicode names (names included by default)
- `--report [--report-dir DIR] [--report-prefix NAME]`: Write a timestamped JSON report (default dir: `log/`, prefix: `emoji-scan`)
- `--fail-on-find`: Exit code 1 if any banned characters are found
- `--list-files`: Print only unique file paths that contain matches
- `-v`/`-vv`: Increase verbosity; `-q/--quiet` suppresses text summary

### substitute

- Applies a substitution map to banned characters outside allowed spans.
- Options mirror `scan`: `--banned`, `--allowed`, `--ext`, `--exclude`, `--dry-run`.
- Map format (JSON):
  - Example: `{ "map": {"⭐": "*", "✨": "*", "🦙": "llama"}, "regex": [{"pattern": "(?:\\u2728)\\s+brilliant", "replacement": "brilliant"}] }`
  - Regex rules are applied first when the match contains at least one banned character and does not overlap an allowed span.

## Examples

```bash
# JSON to stdout
emoji-sniper scan ./vault --banned banned.txt -f json

# Text output with summary
emoji-sniper scan ./vault -f txt -v

# Exclude Obsidian system folder and node modules
emoji-sniper scan ./vault --exclude ".obsidian/*" --exclude node_modules/*

# Only list files that contain banned characters
emoji-sniper scan ./vault --list-files

# CI-friendly failure when matches exist
emoji-sniper scan ./vault --fail-on-find
```

## Installation

This project uses uv for dependency management.

```bash
uv tool install --editable .
# or for development (creates venv automatically)
uv sync
```

## Documentation

- Architecture: `doc/ARCHITECTURE.md`

## Project layout

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

## Banlist format

- Unicode ranges: `\U0001F600-\U0001F64F`
- Literal characters on a line: `✅❌`
- Lines starting with `#` are comments; blanks ignored

## Allowlist format

- Lines starting with `#` are comments; blanks ignored
- Lines starting with `re:` are raw regular expressions (e.g., `re:(?:\U0001F999){3}` for a triple llama)
- Any other non-empty line is treated as a literal sequence to allow (entire line), e.g., `🦙🦙🦙`
