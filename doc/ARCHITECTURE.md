# codex-sniper Architecture

## Overview
codex-sniper scans text files for characters matched by a compiled regex built from `banned.txt` (Unicode ranges and literal lines). Results are reported as structured occurrences.

## Components
- CLI (`main.py`)
  - Argparse commands: `scan` (active), `substitute` (stub)
  - Configures logging via `utils.logging_setup`
- Scanner (`scanner/core.py`)
  - `SniperScanner.scan()` walks files and matches per-line with a prebuilt regex
  - Produces `Occurrence` items and aggregates simple stats
- Banned Parser (`scanner/banned_parser.py`)
  - Parses ranges like `\U0001F600-\U0001F64F` and literal lines
  - Builds a compact character class regex
- Output (`scanner/output.py`)
  - Formats results as JSON or plain text + summary
- File Discovery (`utils/file_discovery.py`)
  - Recursive traversal with extension filtering and glob/substring excludes

## Data Flow
`main(scan)` → configure logging → parse `banned.txt` → build regex → discover files → iterate lines → match occurrences → emit JSON or text; optionally write a timestamped JSON report; log warnings/errors.

## Logging
Root logger writes to console and `log/codex-sniper.log` (rotating). Verbosity controlled by `-v/-vv`.

## Testing
Pytest suite covers parser, discovery, scanner integration, and CLI JSON output.
