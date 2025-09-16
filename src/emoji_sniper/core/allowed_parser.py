from __future__ import annotations

"""
Parse an allowlist file and build a regex that matches allowed sequences.

Format:
- Lines starting with '#' are comments; blanks ignored.
- Lines starting with 're:' are treated as raw regular expressions.
- Any other non-empty line is treated as a literal sequence to allow (the entire line).

Allowed matches are later used to suppress banned occurrences that fall within
any allowed match span.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Tuple
import re


@dataclass(frozen=True)
class AllowedSpec:
    sequences: Tuple[str, ...]
    regexes: Tuple[str, ...]


def _parse_lines(lines: Iterable[str]) -> AllowedSpec:
    sequences: List[str] = []
    regexes: List[str] = []

    for raw in lines:
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith("re:"):
            rx = s[len("re:"):].strip()
            if rx:
                regexes.append(rx)
            continue
        sequences.append(s)

    return AllowedSpec(tuple(sequences), tuple(regexes))


def parse_allowed_file(path: Path) -> AllowedSpec:
    with open(path, "r", encoding="utf-8") as f:
        return _parse_lines(f.readlines())


def build_allowed_regex(spec: AllowedSpec) -> re.Pattern[str] | None:
    parts: List[str] = []
    for seq in spec.sequences:
        parts.append(re.escape(seq))
    for rx in spec.regexes:
        # Group raw regex to avoid precedence issues
        parts.append(f"(?:{rx})")

    if not parts:
        return None
    return re.compile("|".join(parts))

