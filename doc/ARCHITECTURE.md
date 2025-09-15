# codex-sniper Architecture

## Overview
codex-sniper scans text files for characters matched by a compiled regex built from `banned.txt` (Unicode ranges and literal lines). Results are reported as structured occurrences and can be saved as timestamped JSON reports.

```
                         ┌────────────────────────┐
                         │        banned.txt      │
                         │  • ranges  • literals  │
                         └────────────┬───────────┘
                                      │ parse
                                      ▼
┌─────────────┐    discover    ┌──────────────┐     per-line     ┌──────────────────┐
│ Files/Dirs  │ ─────────────▶ │  File List   │ ───────────────▶ │  Regex Matcher   │
│  (.md/.txt) │                └──────────────┘                  │ (codepoint/name) │
└──────┬──────┘                       │                          └─────────┬────────┘
       │ excludes + ext filter        │ occurrences                           │
       ▼                               ▼                                       ▼
   utils.file_discovery        scanner.core.SniperScanner                 scanner.output
                                      │                                       │
                                      ▼                                       ▼
                         stdout (JSON/text)                          report files (*.json)
```

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
  - Accepts a single file path as input

## Data Flow
```
main(scan)
  ├─ setup logging (console + rotating file)
  ├─ parse banned.txt → build regex
  ├─ discover inputs (dir or single file)
  ├─ for each file → for each line → find matches
  │    └─ occurrence = {file, line, col, char, codepoint, name?}
  ├─ format output:
  │    ├─ json (default, includes names by default)
  │    └─ text (+ optional summary)
  └─ if --report → write timestamped JSON file
```

## Logging
Root logger writes to console and `log/codex-sniper.log` (rotating). Verbosity controlled by `-v/-vv`.

```
┌──────────┐        ┌──────────────────────────┐
│ main.py  │  logs  │ log/codex-sniper.log     │
└────┬─────┘ ─────▶ │ (1MB x 5 rotate, utf-8)  │
     │              └──────────────────────────┘
     └─ INFO/DEBUG to console (level = -v/-vv)
```

## Testing
Pytest suite covers parser, discovery, scanner integration, and CLI JSON output.
