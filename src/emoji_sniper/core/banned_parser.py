"""
Parse banned.txt and construct a fast regex for scanning.

Supported lines:
- Unicode ranges like: \U0001F600-\U0001F64F (with or without indentation)
- Literal characters on a line, e.g.: ✅❌⚠️✓❗️⭐️
- Comments start with '#'; empty/whitespace lines ignored.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Set, Tuple
import re


_RANGE_RE = re.compile(r"\\U([0-9A-Fa-f]{8})\s*-\s*\\U([0-9A-Fa-f]{8})")
# Support literal character ranges like: 😀-😃
_CHAR_RANGE_RE = re.compile(r"^(.)\s*-\s*(.)$")


@dataclass(frozen=True)
class BannedSpec:
    ranges: Tuple[Tuple[int, int], ...]
    literals: Tuple[str, ...]


def _parse_lines(lines: Iterable[str]) -> BannedSpec:
    ranges: List[Tuple[int, int]] = []
    literals: List[str] = []

    for raw in lines:
        s = raw.strip()
        if not s or s.startswith("#"):
            continue

        # 1) Backslash-U form: \UXXXXXXXX-\UYYYYYYYY
        m = _RANGE_RE.search(s)
        if m:
            start = int(m.group(1), 16)
            end = int(m.group(2), 16)
            if start > end:
                start, end = end, start
            ranges.append((start, end))
            continue

        # 2) Literal character range: X - Y (single code points)
        m2 = _CHAR_RANGE_RE.match(s)
        if m2 and len(m2.group(1)) == 1 and len(m2.group(2)) == 1:
            c1, c2 = m2.group(1), m2.group(2)
            start, end = ord(c1), ord(c2)
            if start > end:
                start, end = end, start
            ranges.append((start, end))
            continue

        # Treat the whole (non-comment) line as a set of literal characters
        # Keep characters as-is; sequences will be matched per code point
        literals.extend(list(s))

    # De-duplicate and sort for stable regex building
    ranges = sorted(set(ranges))
    # Merge overlapping/adjacent ranges for compactness
    merged: List[Tuple[int, int]] = []
    for r in ranges:
        if not merged:
            merged.append(r)
        else:
            last_s, last_e = merged[-1]
            s, e = r
            if s <= last_e + 1:
                merged[-1] = (last_s, max(last_e, e))
            else:
                merged.append(r)

    # Dedup literals while preserving order
    seen: Set[str] = set()
    uniq_literals: List[str] = []
    for ch in literals:
        if ch not in seen:
            seen.add(ch)
            uniq_literals.append(ch)

    return BannedSpec(tuple(merged), tuple(uniq_literals))


def parse_banned_file(path: Path) -> BannedSpec:
    with open(path, "r", encoding="utf-8") as f:
        return _parse_lines(f.readlines())


def build_regex(spec: BannedSpec) -> re.Pattern[str]:
    """
    Build a compiled regex that matches any banned code point.

    Note: complex emoji sequences will be matched per code point; this is
    intentional for fast detection and simple highlighting.
    """
    parts: List[str] = []

    # Add ranges as \UXXXXXXXX-\UYYYYYYYY inside a char class
    for s, e in spec.ranges:
        parts.append(f"\\U{s:08X}-\\U{e:08X}")

    # Add literals. Escape special characters for char class safety.
    for ch in spec.literals:
        # Hyphen has special meaning inside char classes; escape it.
        if ch == "-":
            parts.append(r"\-")
        else:
            parts.append(re.escape(ch))

    if not parts:
        # Fallback that never matches
        return re.compile(r"(?!x)x")

    char_class = "[" + "".join(parts) + "]"
    return re.compile(char_class)
