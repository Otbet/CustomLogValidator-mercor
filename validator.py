"""Core log-validation logic, kept separate from the Streamlit UI.

Adding a new feature usually means adding a field to `MatchResult` and a
rule here, with little or no change to `app.py`.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Iterable, List, Sequence

# Test names may be pasted one-per-line, comma/semicolon separated, or a mix.
_SPLIT_PATTERN = re.compile(r"[,;\n\r]+")


@dataclass
class MatchResult:
    """Outcome of looking for a single test method inside the logs."""

    name: str
    occurrences: int = 0
    line_numbers: List[int] = field(default_factory=list)

    @property
    def found(self) -> bool:
        return self.occurrences > 0

    @property
    def first_line(self) -> int | None:
        return self.line_numbers[0] if self.line_numbers else None


def parse_test_names(raw: str) -> List[str]:
    """Split pasted test input into a de-duplicated, order-preserving list."""
    names: List[str] = []
    seen: set[str] = set()
    for token in _SPLIT_PATTERN.split(raw or ""):
        name = token.strip().strip("\"'")
        if not name or name in seen:
            continue
        seen.add(name)
        names.append(name)
    return names


def validate(
    logs: str,
    test_names: Sequence[str] | Iterable[str],
    *,
    case_sensitive: bool = False,
    whole_word: bool = False,
) -> List[MatchResult]:
    """Search `logs` for each test name and report where it was found."""
    lines = (logs or "").splitlines()
    haystacks = lines if case_sensitive else [line.lower() for line in lines]

    results: List[MatchResult] = []
    for name in test_names:
        result = MatchResult(name=name)
        needle = name if case_sensitive else name.lower()

        matcher = None
        if whole_word:
            flags = 0 if case_sensitive else re.IGNORECASE
            matcher = re.compile(rf"(?<![\w.]){re.escape(name)}(?![\w])", flags)

        for number, (haystack, original) in enumerate(zip(haystacks, lines), start=1):
            hits = (
                len(matcher.findall(original))
                if matcher is not None
                else haystack.count(needle)
            )
            if hits:
                result.occurrences += hits
                result.line_numbers.append(number)
        results.append(result)
    return results


def summarize(results: Sequence[MatchResult]) -> dict:
    found = sum(1 for r in results if r.found)
    return {
        "total": len(results),
        "found": found,
        "not_found": len(results) - found,
    }
