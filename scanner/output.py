from __future__ import annotations

from typing import Dict, List

from .core import Occurrence


def format_results_as_json(results: List[Occurrence], stats: Dict[str, int | str]):
    return {
        "stats": stats,
        "results": [
            {
                "file": r.file,
                "line": r.line,
                "col": r.col,
                "char": r.char,
                "codepoint": r.codepoint,
                **({"name": r.name} if r.name is not None else {}),
            }
            for r in results
        ],
    }


def format_results_as_text(results: List[Occurrence]) -> str:
    if not results:
        return "No banned characters found."
    lines = []
    for r in results:
        base = f"{r.file}:{r.line}:{r.col} {r.codepoint} '{r.char}'"
        if r.name:
            base += f" {r.name}"
        lines.append(base)
    return "\n".join(lines)


def print_summary(stats: Dict[str, int | str]) -> None:
    print(
        f"Files: {stats.get('files_scanned', 0)} | "
        f"Occurrences: {stats.get('occurrences', 0)} | "
        f"Errors: {stats.get('errors', 0)}"
    )
