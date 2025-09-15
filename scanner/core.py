from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple
import logging
import re
import unicodedata as ud

from utils.file_discovery import find_files
from .banned_parser import parse_banned_file, build_regex


logger = logging.getLogger(__name__)


@dataclass
class Occurrence:
    file: str
    line: int
    col: int
    char: str
    codepoint: str
    name: str | None


class SniperScanner:
    def __init__(
        self,
        vault_path: Path,
        banned_path: Path,
        exclude_patterns: Set[str] | None = None,
        extensions: Set[str] | None = None,
        include_names: bool = False,
    ) -> None:
        self.vault_path = Path(vault_path)
        self.banned_path = Path(banned_path)
        self.exclude_patterns = exclude_patterns or set()
        self.extensions = extensions or {".md", ".txt"}
        self.include_names = include_names

        spec = parse_banned_file(self.banned_path)
        self.pattern: re.Pattern[str] = build_regex(spec)

    def _iter_file_lines(self, path: Path) -> Iterable[Tuple[int, str]]:
        try:
            with open(path, "r", encoding="utf-8", errors="replace") as f:
                for i, line in enumerate(f, start=1):
                    yield i, line.rstrip("\n")
        except Exception as e:
            logger.debug(f"Failed reading {path}: {e}")
            return

    def scan(self) -> Tuple[List[Occurrence], Dict[str, int | str]]:
        files = find_files(self.vault_path, self.extensions, self.exclude_patterns)
        occurrences: List[Occurrence] = []
        file_count = 0
        error_count = 0

        for fp in files:
            file_count += 1
            try:
                for ln, text in self._iter_file_lines(fp):
                    for m in self.pattern.finditer(text):
                        ch = m.group(0)
                        col = m.start() + 1  # 1-based
                        cp = f"U+{ord(ch):04X}"
                        name = None
                        if self.include_names:
                            try:
                                name = ud.name(ch)
                            except ValueError:
                                name = "<unnamed>"

                        occurrences.append(
                            Occurrence(
                                file=str(fp),
                                line=ln,
                                col=col,
                                char=ch,
                                codepoint=cp,
                                name=name,
                            )
                        )
            except Exception as e:
                logger.debug(f"Error scanning {fp}: {e}")
                error_count += 1

        stats = {
            "vault_path": str(self.vault_path),
            "files_scanned": file_count,
            "errors": error_count,
            "occurrences": len(occurrences),
        }
        return occurrences, stats

