"""Gate: configurable terminology blocklist checker."""
from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class TermFinding:
    blocked: str
    preferred: str
    context: str
    start: int = 0


def check_terminology(
    text: str,
    rules: list[dict[str, str]],
) -> list[TermFinding]:
    """Check ``text`` against a list of ``{"blocked": ..., "preferred": ...}`` rules."""
    findings: list[TermFinding] = []
    for rule in rules:
        blocked = rule["blocked"]
        preferred = rule.get("preferred", "")
        flags = 0 if rule.get("case_sensitive") else re.IGNORECASE
        pattern = re.compile(rf"(?<!\w){re.escape(blocked)}(?!\w)", flags)
        for match in pattern.finditer(text):
            lo = max(0, match.start() - 16)
            hi = min(len(text), match.end() + 16)
            findings.append(
                TermFinding(
                    blocked=blocked,
                    preferred=preferred,
                    context=text[lo:hi],
                    start=match.start(),
                )
            )
    return findings


def load_term_rules(path: str | Path) -> list[dict[str, str]]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(raw, list):
        return raw
    return list(raw.get("rules", []))
