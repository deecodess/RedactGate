from __future__ import annotations

import re
from dataclasses import dataclass

from .models import Detection


WINDOW_RADIUS = 48

NAME_LABEL_RE = re.compile(
    r"\b(?P<label>Customer|User|Name|Account holder)\s*:\s*"
    r"(?P<span>[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b"
)
ADDRESS_LABEL_RE = re.compile(
    r"\b(?P<label>Ship-to address|Ship to|Address)\s*:\s*"
    r"(?P<span>\d{1,6}\s+[A-Za-z0-9 .#-]+?,\s*[A-Za-z .'-]+,\s*[A-Z]{2}\s+\d{5}(?:-\d{4})?)",
    re.IGNORECASE,
)
NUMERIC_ID_RE = re.compile(
    r"\b(?P<label>Patient ID|Customer ID|Account ID|Member ID)\s+"
    r"(?P<span>\d{6,12})\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class CandidateWindow:
    start: int
    end: int
    span: str
    type_hint: str
    trigger: str
    window_start: int
    window_end: int
    window: str

    def to_report(self) -> dict[str, object]:
        return {
            "type_hint": self.type_hint,
            "trigger": self.trigger,
            "start": self.start,
            "end": self.end,
            "window_start": self.window_start,
            "window_end": self.window_end,
            "window_chars": len(self.window),
        }


def extract_candidates(text: str, existing: list[Detection] | None = None) -> list[CandidateWindow]:
    occupied = [(item.start, item.end) for item in existing or []]
    candidates: list[CandidateWindow] = []

    candidates.extend(_matches(text, NAME_LABEL_RE, "PERSON_NAME", occupied))
    candidates.extend(_matches(text, ADDRESS_LABEL_RE, "ADDRESS", occupied))
    candidates.extend(_matches(text, NUMERIC_ID_RE, "IDENTIFIER", occupied))

    return _without_duplicate_spans(candidates)


def _matches(
    text: str,
    pattern: re.Pattern[str],
    type_hint: str,
    occupied: list[tuple[int, int]],
) -> list[CandidateWindow]:
    found: list[CandidateWindow] = []
    for match in pattern.finditer(text):
        start = match.start("span")
        end = match.end("span")
        if _overlaps(start, end, occupied):
            continue
        window_start = max(0, start - WINDOW_RADIUS)
        window_end = min(len(text), end + WINDOW_RADIUS)
        found.append(
            CandidateWindow(
                start=start,
                end=end,
                span=match.group("span"),
                type_hint=type_hint,
                trigger=match.group("label"),
                window_start=window_start,
                window_end=window_end,
                window=text[window_start:window_end],
            )
        )
    return found


def _overlaps(start: int, end: int, ranges: list[tuple[int, int]]) -> bool:
    return any(start < range_end and end > range_start for range_start, range_end in ranges)


def _without_duplicate_spans(candidates: list[CandidateWindow]) -> list[CandidateWindow]:
    selected: list[CandidateWindow] = []
    seen: set[tuple[int, int, str]] = set()
    for item in sorted(candidates, key=lambda candidate: (candidate.start, candidate.end)):
        key = (item.start, item.end, item.type_hint)
        if key in seen:
            continue
        seen.add(key)
        selected.append(item)
    return selected
