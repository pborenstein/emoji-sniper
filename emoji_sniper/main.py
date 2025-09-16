#!/usr/bin/env python3
"""
Emoji/Banned Character Sniper CLI

Modeled after the structure of ../tagex but implemented with argparse to
avoid external dependencies. Provides a fast scanner for banned characters
defined in a banned list file.
"""
from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import List, Set

from .core import SniperScanner
from .core.output import (
    format_results_as_json,
    format_results_as_text,
    print_summary,
)


def parse_args(argv: List[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="emoji-sniper",
        description="Scan files for banned characters (e.g., emojis) and report occurrences.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # scan subcommand
    scan = subparsers.add_parser(
        "scan", help="Scan a directory for banned characters"
    )
    scan.add_argument(
        "vault_path",
        type=Path,
        help="Path to the directory to scan",
    )
    scan.add_argument(
        "--banned",
        type=Path,
        default=Path("banned.txt"),
        help="Path to banned list file (default: ./banned.txt)",
    )
    scan.add_argument(
        "--allowed",
        type=Path,
        default=None,
        help="Optional path to allowlist file for sequences to permit",
    )
    scan.add_argument(
        "--format",
        choices=["json", "txt"],
        default="json",
        help="Output format (default: json)",
    )
    scan.add_argument(
        "--report",
        action="store_true",
        help="Write a timestamped JSON report to a directory (default: ./log)",
    )
    scan.add_argument(
        "--report-dir",
        type=Path,
        default=Path("log"),
        help="Directory to write reports when --report is used",
    )
    scan.add_argument(
        "--report-prefix",
        default="emoji-scan",
        help="Filename prefix for reports when --report is used",
    )
    scan.add_argument(
        "--exclude",
        action="append",
        default=[],
        help="Glob patterns to exclude (repeatable)",
    )
    scan.add_argument(
        "--ext",
        default=".md,.txt",
        help="Comma-separated list of file extensions to scan (default: .md,.txt)",
    )
    scan.add_argument(
        "--no-names",
        action="store_true",
        help="Do not include Unicode names in results (faster)",
    )
    scan.add_argument(
        "--fail-on-find",
        action="store_true",
        help="Exit with code 1 if any banned characters are found",
    )
    scan.add_argument(
        "--list-files",
        action="store_true",
        help="Print only unique file paths that contain banned characters",
    )
    scan.add_argument(
        "--verbose",
        "-v",
        action="count",
        default=0,
        help="Increase verbosity (-v, -vv)",
    )
    scan.add_argument(
        "--quiet",
        "-q",
        action="store_true",
        help="Suppress summary output",
    )

    # substitute stub (future)
    sub = subparsers.add_parser(
        "substitute", help="Preview or apply substitutions"
    )
    sub.add_argument("vault_path", type=Path, help="Path to the directory to process")
    sub.add_argument("--banned", type=Path, default=Path("banned.txt"), help="Path to banned list file (default: ./banned.txt)")
    sub.add_argument("--allowed", type=Path, default=None, help="Optional allowlist file")
    sub.add_argument("--map", type=Path, required=True, help="Substitution map JSON file")
    sub.add_argument("--ext", default=".md,.txt", help="Comma-separated file extensions to process")
    sub.add_argument("--exclude", action="append", default=[], help="Glob patterns to exclude (repeatable)")
    sub.add_argument("--dry-run", action="store_true", help="Preview without writing changes")

    return parser.parse_args(argv)


def run_scan(args: argparse.Namespace) -> int:
    # Configure logging to console and file
    from .utils.logging_setup import setup_logging

    setup_logging(args.verbose)
    logging.info("Starting scan")

    exts: Set[str] = {e.strip().lower() for e in args.ext.split(",") if e.strip()}
    excludes: Set[str] = set(args.exclude) if args.exclude else set()

    scanner = SniperScanner(
        vault_path=args.vault_path,
        banned_path=args.banned,
        allowed_path=args.allowed,
        exclude_patterns=excludes,
        extensions=exts,
        include_names=not args.no_names,
    )

    results, stats = scanner.scan()

    payload = format_results_as_json(results, stats)

    if args.list_files:
        files = sorted({r.file for r in results})
        for f in files:
            print(f)
    else:
        if args.format == "json":
            print(json.dumps(payload, ensure_ascii=False, indent=2))
        else:
            print(format_results_as_text(results))
            if not args.quiet:
                print()
                print_summary(stats)

    if args.report:
        try:
            args.report_dir.mkdir(parents=True, exist_ok=True)
            from datetime import datetime

            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            fname = f"{args.report_prefix}_{ts}.json"
            fpath = args.report_dir / fname
            with open(fpath, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            logging.info("Report written to %s", fpath)
        except Exception as e:
            logging.error("Failed to write report: %s", e)
    
    if args.fail_on_find and stats.get("occurrences", 0) > 0:
        return 1
    return 0


def run_substitute(args: argparse.Namespace) -> int:
    from .utils.logging_setup import setup_logging
    from .core.substitute import Substitutor

    setup_logging(args.verbose if hasattr(args, "verbose") else 0)
    exts: Set[str] = {e.strip().lower() for e in args.ext.split(",") if e.strip()}
    excludes: Set[str] = set(args.exclude) if args.exclude else set()

    subber = Substitutor(
        vault_path=args.vault_path,
        banned_path=args.banned,
        subs_path=args.map,
        allowed_path=args.allowed,
        exclude_patterns=excludes,
        extensions=exts,
    )
    stats = subber.run(dry_run=args.dry_run)

    # Simple console summary
    print(
        f"Files: {stats.files_scanned} | Changed: {stats.files_changed} | "
        f"Replacements: {stats.replacements} | Unmapped banned: {stats.unmapped_banned} | "
        f"Errors: {stats.errors}"
    )
    return 0 if stats.errors == 0 else 1


def main(argv: List[str] | None = None) -> int:
    args = parse_args(argv)
    if args.command == "scan":
        return run_scan(args)
    elif args.command == "substitute":
        return run_substitute(args)
    else:
        logging.error("Unknown command")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
