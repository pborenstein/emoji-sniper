# Repository Guidelines

## Project Structure & Module Organization
- `main.py`: CLI entry point using `argparse` (`scan` and `substitute` stub).
- `scanner/`: core scanning logic
  - `core.py`: `SniperScanner` and occurrence model.
  - `banned_parser.py`: parses `banned.txt` and builds the regex.
  - `output.py`: JSON/text formatting and summary helpers.
- `utils/`: shared helpers (`file_discovery.py` for walking files).
- `banned.txt`: default banned characters/ranges list. Comments start with `#`.
- `idea.md`: design notes.

## Build, Test, and Development Commands
- Using uv (preferred):
  - Create venv + sync: `uv venv && uv sync --group dev`
  - Run tests: `uv run pytest`
  - Run CLI (JSON): `uv run python main.py scan ./vault --banned banned.txt`
  - Save a report: `uv run python main.py scan ./vault --report --report-dir log`
- Python directly:
  - `python3 main.py scan /path/to/vault --banned banned.txt --format json`
  - Text mode: `python3 main.py scan ./vault --format txt -v`
- Filter by extensions: `--ext .md,.txt`; exclude: `--exclude ".obsidian/*" --exclude node_modules/*`
- Include Unicode names (slower): `--names`
 - Reports: `--report [--report-dir DIR] [--report-prefix NAME]`

## Coding Style & Naming Conventions
- Python 3.10+; 4-space indentation; type hints required for public functions.
- Naming: modules/functions `snake_case`, classes `CapWords`, constants `UPPER_SNAKE`.
- Prefer `pathlib.Path`, `logging` over `print` (except CLI output in `main.py`).
- Keep CLI behavior in `main.py`; business logic in `scanner/*`; reusable utilities in `utils/*`.
- Optional formatters: `black` and `ruff` (if installed). Aim for clean diffs and small, focused changes.

## Testing Guidelines
- Framework: pytest (recommended). Place tests under `tests/` mirroring package layout.
- Naming: files `test_*.py`; functions `test_*`.
- What to test: `scanner.banned_parser` parsing (ranges, literals, comments), `utils.file_discovery` exclude/extension logic, and `SniperScanner.scan` happy/error paths.
- Run: `pytest -q` (add as project grows). Keep new code covered; prefer fast, isolated tests with temp dirs/files.

## Commit & Pull Request Guidelines
- Commits: Conventional Commits style is preferred: `feat:`, `fix:`, `refactor:`, `test:`, `docs:`, `chore:`.
- PRs must include: clear description, reproduction or example command, expected vs. actual output, and any flags used.
- Link related issues; add/update tests when changing behavior; update `banned.txt` examples or docs when relevant.
- Keep PRs scoped; avoid unrelated refactors.

## Security & Configuration Tips
- `banned.txt` supports Unicode ranges like `\U0001F600-\U0001F64F` and literal lines (e.g., `✅❌`). Lines starting with `#` are ignored.
- Default excludes include `.obsidian`, `.git`, `.DS_Store`, `__pycache__`, `node_modules`; configure more via `--exclude`.
- Logging: activity is recorded to `log/codex-sniper.log`; increase verbosity with `-v`/`-vv`.
- Ensure files are UTF-8; use `--names` only when needed due to performance cost.
