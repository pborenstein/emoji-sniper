from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple
import json
import re


@dataclass(frozen=True)
class RegexRule:
    pattern: str
    replacement: str


@dataclass(frozen=True)
class SubstitutionMap:
    mapping: Dict[str, str]
    regex_rules: Tuple[RegexRule, ...]

    @staticmethod
    def load(path: Path) -> "SubstitutionMap":
        data = json.loads(path.read_text(encoding="utf-8"))
        mapping = data.get("map", {}) or {}
        regex_list = data.get("regex", []) or []
        rules: List[RegexRule] = []
        for item in regex_list:
            pat = item.get("pattern")
            rep = item.get("replacement")
            if isinstance(pat, str) and isinstance(rep, str):
                rules.append(RegexRule(pat, rep))
        return SubstitutionMap(dict(mapping), tuple(rules))

    def compiled_regex_rules(self) -> List[tuple[re.Pattern[str], str]]:
        return [(re.compile(r.pattern), r.replacement) for r in self.regex_rules]

