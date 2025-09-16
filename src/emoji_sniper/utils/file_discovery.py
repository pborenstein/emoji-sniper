"""
File discovery utilities for finding files to scan.

Modeled after ../tagex with small adaptations.
"""
from __future__ import annotations

from pathlib import Path
from typing import List, Set, Union
import fnmatch


DEFAULT_EXCLUDES: Set[str] = {".obsidian", ".git", ".DS_Store", "__pycache__", "node_modules"}


def find_files(
    root_path: str | Path,
    extensions: Union[Set[str], List[str], None] = None,
    exclude_patterns: Union[Set[str], List[str], None] = None,
) -> List[Path]:
    """
    Recursively find files with given extensions under root_path.

    Args:
        root_path: Directory to scan
        extensions: File extensions to include (like {".md", ".txt"}); if None, include all
        exclude_patterns: Glob-like patterns or substrings to exclude

    Returns:
        Sorted list of Paths
    """
    if exclude_patterns is None:
        exclude_patterns = set(DEFAULT_EXCLUDES)
    elif isinstance(exclude_patterns, list):
        exclude_patterns = set(exclude_patterns)

    if isinstance(extensions, list):
        extensions = set(extensions)

    root = Path(root_path)
    if not root.exists():
        raise FileNotFoundError(f"Path does not exist: {root}")
    # Support scanning a single file
    if root.is_file():
        if isinstance(extensions, list):
            extensions = set(extensions)
        if not extensions or root.suffix.lower() in extensions:  # type: ignore[operator]
            return [root]
        return []
    if not root.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {root}")

    results: List[Path] = []

    def should_exclude(path: Path) -> bool:
        rel = str(path.relative_to(root)) if path != root else ""
        for pat in exclude_patterns:  # type: ignore[arg-type]
            if pat.endswith("/*"):
                d = pat[:-2]
                if rel.startswith(d + "/") or rel == d:
                    return True
            elif fnmatch.fnmatch(rel, pat):
                return True
            elif pat in rel:
                return True
        return False

    def walk(dirpath: Path) -> None:
        try:
            for item in dirpath.iterdir():
                if should_exclude(item):
                    continue
                if item.is_file():
                    if not extensions:
                        results.append(item)
                    else:
                        if item.suffix.lower() in extensions:  # type: ignore[operator]
                            results.append(item)
                elif item.is_dir():
                    walk(item)
        except PermissionError:
            return

    walk(root)
    return sorted(results)
