# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Project Overview

Emoji Sniper is a CLI tool for detecting and managing emoji/banned characters in Obsidian vaults and text repositories. It provides scanning, filtering, and substitution capabilities with configurable allowlists and bannedlists.

## Development Commands

```bash
# Install dependencies
uv sync

# Add test dependencies
uv add --optional test pytest pytest-cov pytest-mock

# Primary CLI usage (development)
uv run python -m emoji_sniper.main [command] [options]

# System-wide tool (if installation succeeds)
uv tool install --editable .
emoji-sniper [command] [options]

# Run tests
uv run python -m pytest tests/ -v

# Linting and formatting
uv run ruff check .
uv run black .
uv run mypy .
```

## Documentation

- [doc/ARCHITECTURE.md](doc/ARCHITECTURE.md) - System architecture (REQUIRED)
- [doc/EMOJI-RANGES.md](doc/EMOJI-RANGES.md) - Emoji detection ranges and allowlist examples
- [tests/README.md](tests/README.md) - Test suite documentation

## Architecture Notes

### Core Modules

- **`core/`** - Core functionality for emoji detection, parsing, and substitution
  - `core.py` - Main scanning and detection logic
  - `allowed_parser.py` - Allowlist configuration parsing
  - `banned_parser.py` - Bannedlist configuration parsing
  - `substitute.py` - Character substitution engine
  - `output.py` - Result formatting and display
- **`utils/`** - Utility functions for file discovery and operations
- **`tests/`** - Comprehensive test suite for all modules

### Key Features

- Multi-format emoji detection (Unicode ranges, named patterns)
- Configurable allowlists and bannedlists
- Character substitution with precedence rules
- File discovery with pattern matching
- Multiple output formats (console, structured data)

## Coding Standards

- Python 3.10+ required
- 2-space indentation (per global CLAUDE.md)
- Type hints required for public functions
- Use pathlib.Path for file operations
- Prefer logging over print (except CLI output in main.py)
- UV-exclusive workflow (no direct python/pip usage)

## Testing Guidelines

- Framework: pytest
- Test files: `test_*.py` in `tests/` directory
- Test functions: `test_*`
- Run tests: `uv run pytest tests/`
- Coverage target: 80%+ for core modules