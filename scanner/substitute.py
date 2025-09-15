from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple
import logging
import re

from utils.file_discovery import find_files
from .banned_parser import parse_banned_file, build_regex
from .allowed_parser import parse_allowed_file, build_allowed_regex
from .substitution_map import SubstitutionMap


logger = logging.getLogger(__name__)


@dataclass
class SubstitutionStats:
    files_scanned: int
    files_changed: int
    replacements: int
    unmapped_banned: int
    errors: int


class Substitutor:
    def __init__(
        self,
        vault_path: Path,
        banned_path: Path,
        subs_path: Path,
        allowed_path: Path | None = None,
        exclude_patterns: Set[str] | None = None,
        extensions: Set[str] | None = None,
    ) -> None:
        self.vault_path = Path(vault_path)
        self.banned_path = Path(banned_path)
        self.allowed_path = Path(allowed_path) if allowed_path is not None else None
        self.exclude_patterns = exclude_patterns or set()
        self.extensions = extensions or {".md", ".txt"}

        bspec = parse_banned_file(self.banned_path)
        self.banned_pattern: re.Pattern[str] = build_regex(bspec)

        self.allowed_pattern: re.Pattern[str] | None = None
        if self.allowed_path and self.allowed_path.exists():
            aspec = parse_allowed_file(self.allowed_path)
            self.allowed_pattern = build_allowed_regex(aspec)

        self.subs = SubstitutionMap.load(Path(subs_path))
        self.regex_rules = self.subs.compiled_regex_rules()

    def _iter_file_lines(self, path: Path) -> Iterable[Tuple[int, str]]:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            for i, line in enumerate(f, start=1):
                yield i, line.rstrip("\n")

    @staticmethod
    def _overlaps_allowed(span: Tuple[int, int], allowed_spans: List[Tuple[int, int]]) -> bool:
        s, e = span
        for as_, ae in allowed_spans:
            if not (e <= as_ or s >= ae):
                return True
        return False

    def run(self, dry_run: bool = True) -> SubstitutionStats:
        files = find_files(self.vault_path, self.extensions, self.exclude_patterns)
        files_scanned = 0
        files_changed = 0
        total_replacements = 0
        unmapped_banned = 0
        errors = 0

        for fp in files:
            files_scanned += 1
            try:
                lines = [text for _, text in self._iter_file_lines(fp)]
                changed = False
                file_replacements = 0

                new_lines: List[str] = []
                for text in lines:
                    allowed_spans: List[Tuple[int, int]] = []
                    if self.allowed_pattern is not None:
                        for m in self.allowed_pattern.finditer(text):
                            allowed_spans.append((m.start(), m.end()))

                    edits: List[Tuple[int, int, str]] = []  # (start, end, replacement)

                    # Apply regex rules first (if they include banned content)
                    for rx, rep in self.regex_rules:
                        for m in rx.finditer(text):
                            span = (m.start(), m.end())
                            if self._overlaps_allowed(span, allowed_spans):
                                continue
                            # require that at least one banned match falls within this span
                            has_banned = any(
                                self.banned_pattern.search(text, pos, span[1])
                                for pos in range(span[0], span[1])
                            )
                            if not has_banned:
                                continue
                            edits.append((span[0], span[1], rep))

                    # Then literal char mapping based on banned matches
                    for m in self.banned_pattern.finditer(text):
                        idx = m.start()
                        span = (idx, idx + 1)
                        if self._overlaps_allowed(span, allowed_spans):
                            continue
                        ch = m.group(0)
                        rep = self.subs.mapping.get(ch)
                        if rep is None:
                            unmapped_banned += 1
                            continue
                        edits.append((span[0], span[1], rep))

                    if not edits:
                        new_lines.append(text)
                        continue

                    # Resolve overlapping edits by keeping the first occurrence of a region
                    # Prefer longer spans at the same start so regex rules win over single-char maps
                    edits.sort(key=lambda t: (t[0], -(t[1] - t[0])))
                    resolved: List[Tuple[int, int, str]] = []
                    last_end = -1
                    for s, e, rep in edits:
                        if s < last_end:
                            # overlaps previous edit; skip to avoid conflicts
                            continue
                        resolved.append((s, e, rep))
                        last_end = e

                    # Apply edits right-to-left
                    buf = text
                    for s, e, rep in reversed(resolved):
                        buf = buf[:s] + rep + buf[e:]
                        file_replacements += 1

                    if buf != text:
                        changed = True
                        new_lines.append(buf)
                    else:
                        new_lines.append(text)

                if changed and not dry_run:
                    Path(fp).write_text("\n".join(new_lines) + "\n", encoding="utf-8")
                    files_changed += 1
                    total_replacements += file_replacements
                elif changed:
                    # Dry run still counts replacements but does not write
                    files_changed += 1
                    total_replacements += file_replacements

            except Exception as e:
                logger.debug(f"Error substituting in {fp}: {e}")
                errors += 1

        return SubstitutionStats(
            files_scanned=files_scanned,
            files_changed=files_changed,
            replacements=total_replacements,
            unmapped_banned=unmapped_banned,
            errors=errors,
        )
